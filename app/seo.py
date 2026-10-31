"""Search metadata, canonical URLs, and discovery for the public pages."""

from xml.etree.ElementTree import Element, SubElement, tostring

from flask import Response, request, url_for

from app import app


# Keep the sitemap and page metadata together; never discover admin routes by crawling.
PAGES = {
    "index": {
        "title": "Scientific & Medical Copyeditor | Editor Melinda",
        "description": (
            "Scientific and medical copyediting for ESL authors. Experience with 2,500+ "
            "Cell Press articles and 100+ Elsevier books. Request a free 500-word sample edit."
        ),
        "label": "Copyediting",
    },
    "portfolio": {
        "title": "Cell Press & Elsevier Editing Portfolio | Editor Melinda",
        "description": (
            "Scientific and medical copyediting by Melinda Wedgewood: 2,500+ Cell Press "
            "journal articles and 100+ Elsevier textbooks. Editing since 2014."
        ),
        "label": "Editing portfolio",
        "type": "CollectionPage",
    },
    "contact": {
        "title": "Free 500-Word Sample Edit & Contact | Editor Melinda",
        "description": (
            "Request a free 500-word sample edit for your scientific or medical manuscript. "
            "Contact Editor Melinda about ESL editing, style requirements, and deadlines."
        ),
        "label": "Contact",
        "type": "ContactPage",
    },
    "goats": {
        "title": "Nigerian Dwarf Goats in Poulsbo, WA | Goat Mountain View",
        "description": (
            "Nigerian Dwarf goats at Goat Mountain View, a small farm in Poulsbo, Washington. "
            "Photos of the herd and information about goat adoptions."
        ),
        "label": "Nigerian Dwarf goats",
        "image": "images/goats.jpg",
        "image_alt": "Nigerian Dwarf goats at Goat Mountain View",
    },
    "does": {
        "title": "Nigerian Dwarf Does | Goat Mountain View, Poulsbo",
        "description": (
            "Photos and information about the Nigerian Dwarf does at Goat Mountain View, "
            "a small dairy goat herd in Poulsbo, Washington."
        ),
        "label": "Does",
        "parent": "goats",
        "image": "images/goats.jpg",
        "image_alt": "Nigerian Dwarf goats at Goat Mountain View",
    },
    "adoptions": {
        "title": "Nigerian Dwarf Goat Adoptions | Goat Mountain View",
        "description": (
            "Nigerian Dwarf goat adoption information for Goat Mountain View in Poulsbo, "
            "Washington. Contact Melinda about availability."
        ),
        "label": "Adoptions",
        "parent": "goats",
        "image": "images/goats.jpg",
        "image_alt": "Nigerian Dwarf goats at Goat Mountain View",
    },
    "foundation": {
        "title": "Nigerian Dwarf Foundation Goats | Goat Mountain View",
        "description": (
            "Foundation goats of the Nigerian Dwarf herd at Goat Mountain View in Poulsbo, "
            "Washington, with photographs and background on each goat."
        ),
        "label": "Foundation goats",
        "parent": "goats",
        "image": "images/goats.jpg",
        "image_alt": "Nigerian Dwarf goats at Goat Mountain View",
    },
    "soap": {
        "title": "Handcrafted Goat Milk Soap in Poulsbo | Goat Mountain View",
        "description": (
            "Small-batch goat milk soap from Goat Mountain View, made with milk from our "
            "Nigerian Dwarf goats. Available online and at Nordiska in Poulsbo, Washington."
        ),
        "label": "Goat milk soap",
        "image": "images/soap.jpg",
        "image_alt": "Handcrafted Goat Mountain View soap",
    },
    "art": {
        "title": "Art Studies by Melinda Wedgewood | Editor Melinda",
        "description": (
            "Colored pencil, watercolor, drawing, and sketchbook studies by Melinda Wedgewood, "
            "from art classes and independent practice."
        ),
        "label": "Art studies",
        "image": "images/art/whole.jfif",
        "image_alt": "Art study by Melinda Wedgewood",
    },
}


def canonical_url(endpoint):
    """Build URLs from configuration, independent of request host and query strings."""
    return app.config["SITE_URL"] + url_for(endpoint)


@app.context_processor
def search_metadata():
    page = PAGES.get(request.endpoint)
    if page is None:
        return {"seo": None}

    canonical = canonical_url(request.endpoint)
    home = canonical_url("index")
    portrait = app.config["SITE_URL"] + url_for("static", filename="images/melinda2.jpg")
    image = app.config["SITE_URL"] + url_for("static", filename=page.get("image", "images/melinda2.jpg"))
    person = {
        "@type": "Person",
        "@id": home + "#melinda",
        "name": "Melinda Wedgewood",
        "alternateName": "Editor Melinda",
        "url": home,
        "image": portrait,
        "jobTitle": "Freelance scientific and medical copyeditor",
        "sameAs": ["https://www.linkedin.com/in/melinda-wedgewood-22314867"],
        "knowsAbout": ["Scientific copyediting", "Medical manuscript editing", "ESL editing",
                       "AMA style", "Chicago Manual of Style", "APA style"],
    }
    webpage = {
        "@type": page.get("type", "WebPage"),
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": page["title"],
        "description": page["description"],
        "inLanguage": "en",
        "isPartOf": {"@id": home + "#website"},
    }
    graph = [
        {"@type": "WebSite", "@id": home + "#website", "url": home,
         "name": "Editor Melinda", "alternateName": "Goat Mountain View",
         "publisher": {"@id": person["@id"]}, "inLanguage": "en"},
        person,
        webpage,
    ]
    if request.endpoint == "index":
        service = {
            "@type": "Service",
            "@id": home + "#copyediting",
            "name": "Scientific and medical copyediting",
            "serviceType": "Scientific and medical manuscript copyediting and line editing",
            "description": page["description"],
            "provider": {"@id": person["@id"]},
            "url": home,
        }
        webpage["mainEntity"] = {"@id": service["@id"]}
        graph.append(service)
    else:
        ancestors = ["index"]
        if page.get("parent"):
            ancestors.append(page["parent"])
        ancestors.append(request.endpoint)
        breadcrumb = {
            "@type": "BreadcrumbList",
            "@id": canonical + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": position,
                 "name": PAGES[endpoint]["label"], "item": canonical_url(endpoint)}
                for position, endpoint in enumerate(ancestors, start=1)
            ],
        }
        webpage["breadcrumb"] = {"@id": breadcrumb["@id"]}
        graph.append(breadcrumb)

    return {"seo": {**page, "canonical": canonical, "image": image,
                    "image_alt": page.get("image_alt", "Melinda Wedgewood, Editor Melinda"),
                    "structured_data": {"@context": "https://schema.org", "@graph": graph}}}


@app.route("/robots.txt")
def robots_txt():
    # Allow crawlers to see the noindex response headers on login/admin pages.
    return Response(
        "User-agent: *\nAllow: /\n\nSitemap: " + canonical_url("sitemap_xml") + "\n",
        mimetype="text/plain",
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for endpoint in PAGES:
        entry = SubElement(root, "url")
        SubElement(entry, "loc").text = canonical_url(endpoint)
    return Response(tostring(root, encoding="utf-8", xml_declaration=True),
                    mimetype="application/xml")


@app.after_request
def indexing_headers(response):
    """Keep administrative pages and errors out of search, including redirects."""
    public_endpoints = {*PAGES, "static", "robots_txt", "sitemap_xml"}
    if request.endpoint not in public_endpoints or response.status_code >= 400:
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response
