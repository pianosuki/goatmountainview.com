"""Verify search-facing behavior without touching the site's database or credentials."""

from html.parser import HTMLParser
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree


test_instance = tempfile.TemporaryDirectory(prefix="editor-melinda-seo-")
with patch.dict(os.environ, {"SECRET_KEY": "test-only-secret", "SITE_URL": "https://goatmountainview.com"}), \
        patch("flask.Flask.auto_find_instance_path", return_value=test_instance.name):
    from app import app, db
    from app.models import BookHS, BookST


class PageParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.title = ""
        self.json_scripts = []
        self.in_title = False
        self.in_json = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        self.in_title = tag == "title" or self.in_title
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_json = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_json:
            self.json_scripts.append(data)

    def matching(self, tag, **attrs):
        return [values for name, values in self.tags if name == tag
                and all(values.get(key) == value for key, value in attrs.items())]


class ImageAltParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.images = []
        self.hidden_lists = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "ul":
            self.hidden_lists.append(attrs.get("aria-hidden") == "true" or any(self.hidden_lists))
        elif tag == "img":
            self.images.append((attrs, any(self.hidden_lists)))

    def handle_endtag(self, tag):
        if tag == "ul" and self.hidden_lists:
            self.hidden_lists.pop()


class SearchMetadataTests(unittest.TestCase):
    paths = ("/", "/portfolio", "/contact", "/goats", "/goats/does",
             "/goats/adoptions", "/goats/foundation", "/soap", "/art")

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()
            for model in (BookHS, BookST):
                db.session.add(model(name="Example textbook", editors="Example author",
                                     year=2025, link="https://example.com/book"))
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        test_instance.cleanup()

    def test_public_pages_have_unique_metadata_and_one_main_heading(self):
        titles, descriptions = set(), set()
        for path in self.paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("noindex", response.headers.get("X-Robots-Tag", ""))
                page = PageParser(response.get_data(as_text=True))
                self.assertEqual(len(page.matching("title")), 1)
                self.assertEqual(len(page.matching("h1")), 1)
                self.assertEqual(len(page.matching("meta", name="viewport")), 1)
                description = page.matching("meta", name="description")
                self.assertEqual(len(description), 1)
                self.assertTrue(description[0]["content"].strip())
                self.assertNotIn(page.title, titles)
                self.assertNotIn(description[0]["content"], descriptions)
                titles.add(page.title)
                descriptions.add(description[0]["content"])
                self.assertEqual(page.matching("link", rel="canonical")[0]["href"],
                                 "https://goatmountainview.com" + path)
                self.assertEqual(page.matching("meta", property="og:title")[0]["content"], page.title)
                self.assertEqual(page.matching("meta", property="og:description")[0]["content"],
                                 description[0]["content"])

    def test_structured_data_and_breadcrumbs_are_valid(self):
        for path in self.paths:
            with self.subTest(path=path):
                page = PageParser(self.client.get(path).get_data(as_text=True))
                data = json.loads("".join(page.json_scripts))
                self.assertEqual(data["@context"], "https://schema.org")
                nodes = {node["@type"]: node for node in data["@graph"]}
                self.assertEqual(nodes["Person"]["name"], "Melinda Wedgewood")
                if path == "/":
                    self.assertEqual(nodes["Service"]["provider"]["@id"], nodes["Person"]["@id"])
                else:
                    items = nodes["BreadcrumbList"]["itemListElement"]
                    self.assertEqual([item["position"] for item in items], list(range(1, len(items) + 1)))
                    self.assertEqual(items[-1]["item"], "https://goatmountainview.com" + path)
                    if path.startswith("/goats/"):
                        self.assertEqual(items[-2]["item"], "https://goatmountainview.com/goats")

    def test_canonical_urls_ignore_request_host_and_tracking_parameters(self):
        response = self.client.get("/portfolio?utm_source=resume", base_url="http://localhost:4321")
        page = PageParser(response.get_data(as_text=True))
        canonical = "https://goatmountainview.com/portfolio"
        self.assertEqual(page.matching("link", rel="canonical")[0]["href"], canonical)
        self.assertEqual(page.matching("meta", property="og:url")[0]["content"], canonical)

    def test_site_url_configuration_updates_all_discovery_urls(self):
        with patch.dict(app.config, {"SITE_URL": "https://editor.example"}):
            page = PageParser(self.client.get("/").get_data(as_text=True))
            self.assertEqual(page.matching("link", rel="canonical")[0]["href"], "https://editor.example/")
            self.assertIn("https://editor.example/static/", page.matching("meta", property="og:image")[0]["content"])
            self.assertIn("Sitemap: https://editor.example/sitemap.xml", self.client.get("/robots.txt").text)
            self.assertNotIn("https://goatmountainview.com", self.client.get("/sitemap.xml").text)

    def test_sitemap_lists_only_canonical_public_pages(self):
        response = self.client.get("/sitemap.xml", base_url="http://localhost:4321")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/xml")
        root = ElementTree.fromstring(response.data)
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [item.text for item in root.findall("s:url/s:loc", namespace)]
        self.assertCountEqual(urls, ["https://goatmountainview.com" + path for path in self.paths])

    def test_robots_allows_public_crawling_and_advertises_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertIn("User-agent: *\nAllow: /", response.text)
        self.assertIn("Sitemap: https://goatmountainview.com/sitemap.xml", response.text)
        self.assertNotIn("Disallow:", response.text)

    def test_private_routes_and_errors_are_not_indexable(self):
        for path in ("/login", "/admin", "/logout", "/api/images", "/does-not-exist"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.headers.get("X-Robots-Tag"), "noindex, nofollow")

    def test_sample_edit_offer_has_a_working_contact_path(self):
        home = PageParser(self.client.get("/").text)
        self.assertEqual(len(home.matching("a", href="/contact#sample-edit")), 1)
        self.assertEqual(len(home.matching("a", href="/portfolio", **{"class": "content-header-button"})), 1)
        contact = PageParser(self.client.get("/contact").text)
        self.assertTrue(contact.matching("section", id="sample-edit"))
        self.assertTrue(contact.matching("a", href="https://goat-mountain-view.square.site/contact-us"))
        self.assertFalse(contact.matching("link", href="/static/css/contact.css"))

    def test_share_images_are_served(self):
        for path in self.paths:
            with self.subTest(path=path):
                page = PageParser(self.client.get(path).text)
                image = page.matching("meta", property="og:image")[0]["content"]
                response = self.client.get(image.removeprefix("https://goatmountainview.com"))
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.mimetype.startswith("image/"))
                finally:
                    response.close()

    def test_public_images_are_described_without_repeating_slideshow_copies(self):
        for path in self.paths:
            with self.subTest(path=path):
                page = ImageAltParser(self.client.get(path).text)
                for attrs, hidden in page.images:
                    with self.subTest(src=attrs.get("src")):
                        self.assertIn("alt", attrs)
                        if hidden:
                            self.assertEqual(attrs["alt"], "")
                        elif attrs.get("src"):
                            self.assertTrue(attrs["alt"].strip())

    def test_image_descriptions_cover_leading_slashes_and_future_uploads(self):
        from app.image_accessibility import image_alt

        with app.open_resource("image_alt.json") as source:
            descriptions = json.load(source)
        self.assertTrue(descriptions)
        for filename, description in descriptions.items():
            self.assertTrue(isinstance(description, str) and description.strip())
            self.assertEqual(image_alt(filename), description)
            self.assertEqual(image_alt("/" + filename), description)
        self.assertEqual(image_alt("uploads/new-goat.jpg", "Fern, a Nigerian Dwarf goat"),
                         "Fern, a Nigerian Dwarf goat")

    def test_image_description_attributes_escape_quotes_and_markup(self):
        description = 'Goat named "Fern" beside a sign reading <Welcome> & flowers'
        html = app.jinja_env.from_string('<img alt="{{ image_alt(filename, fallback) }}">').render(
            filename="uploads/new-goat.jpg", fallback=description)
        page = PageParser(html)
        self.assertEqual(page.matching("img")[0]["alt"], description)
        self.assertFalse(page.matching("welcome"))


if __name__ == "__main__":
    unittest.main()
