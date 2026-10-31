# SEO maintenance

## Page metadata

Add public routes to `PAGES` in `app/seo.py`. It supplies page titles, descriptions,
sharing previews, canonical URLs, structured data, and the URLs in `/sitemap.xml`.
`base.html` renders the metadata. Unlisted application routes, including login and
admin pages, receive an `X-Robots-Tag: noindex, nofollow` header. Error responses
also receive that header. `/robots.txt` allows crawling so search engines can
read these instructions and find the sitemap.

`SITE_URL` defaults to `https://goatmountainview.com`. It must be an absolute
HTTP(S) origin without a path, query, or fragment. Canonical URLs and the sitemap
use this setting, independent of the request host and tracking parameters.
EditorMelinda.com permanently redirects to this origin and preserves page paths.
If the preferred domain changes, update `SITE_URL` and the host's redirects together.

The homepage and contact page offer a free sample edit of up to 500 words.
Inquiries go through the existing Square contact form.

## Image descriptions

`app/image_alt.json` holds reviewed descriptions, keyed by paths relative to
`app/static/images`. The `image_alt()` template helper uses these descriptions
and falls back to the goat or soap name for new uploads. Review new photos and
add descriptions when they need more detail.

Duplicate slideshow strips have empty alt text and are hidden from screen
readers. The enlarged image viewer uses the thumbnail's description. Visible
captions and page prose are separate from these descriptions.

## Checks

Run from the project directory:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The tests use a temporary SQLite database and a test secret. They leave the
configured database and admin credentials untouched.

## Deployment

1. Deploy the source and restart the Flask application using the normal hosting
   workflow. Preserve `instance/storage.db` and `app/static/images/uploads/`;
   the admin dashboard maintains those live records and photos.
2. Check `/`, `/portfolio`, `/contact`, `/robots.txt`, and `/sitemap.xml` on the live domain.
3. In the owner's Google Search Console property for Goat Mountain View, submit
   `https://goatmountainview.com/sitemap.xml`. Request indexing of the homepage,
   portfolio, and contact page through URL Inspection.
4. Monitor indexing and search queries in Search Console. Search engines choose
   the final snippets and rankings.

Google documents [titles and descriptions](https://developers.google.com/search/docs/fundamentals/seo-starter-guide),
[canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),
and [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
The unused meta-keywords tag is omitted because
[Google ignores it](https://developers.google.com/search/docs/crawling-indexing/special-tags).
