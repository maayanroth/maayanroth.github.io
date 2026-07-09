#!/usr/bin/env python3
"""Regenerate blog/feed.xml from the HTML files in blog/posts/."""

import glob
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

SITE_URL = "https://www.maayanroth.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "blog", "posts")
FEED_PATH = os.path.join(ROOT, "blog", "feed.xml")


def parse_post(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    title_match = re.search(r"<title>(.*?)\s*&middot;.*?</title>", html, re.S)
    date_match = re.search(r'<p class="post-date">(.*?)</p>', html, re.S)
    main_match = re.search(r"<main>(.*?)</main>", html, re.S)
    if not (title_match and date_match and main_match):
        return None

    title = title_match.group(1).strip()
    date_str = date_match.group(1).strip()
    pub_date = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)

    body = main_match.group(1)
    body = re.sub(r"<h2>.*?</h2>", "", body, count=1, flags=re.S)
    body = re.sub(r'<p class="post-date">.*?</p>', "", body, count=1, flags=re.S)
    body = body.strip()

    slug = os.path.basename(path)
    link = f"{SITE_URL}/blog/posts/{slug}"

    return {
        "title": title,
        "link": link,
        "pub_date": pub_date,
        "body": body,
    }


def main():
    posts = []
    for path in glob.glob(os.path.join(POSTS_DIR, "*.html")):
        post = parse_post(path)
        if post:
            posts.append(post)

    posts.sort(key=lambda p: p["pub_date"], reverse=True)

    items = []
    for post in posts:
        items.append(f"""    <item>
      <title>{escape(post['title'])}</title>
      <link>{escape(post['link'])}</link>
      <guid>{escape(post['link'])}</guid>
      <pubDate>{format_datetime(post['pub_date'])}</pubDate>
      <description><![CDATA[{post['body']}]]></description>
    </item>""")

    last_build = format_datetime(datetime.now(timezone.utc))

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Maayan Roth's Blog</title>
    <link>{SITE_URL}/blog/index.html</link>
    <description>Engineer, potter, e-bike enthusiast, mom of two.</description>
    <language>en-us</language>
    <lastBuildDate>{last_build}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""

    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(feed)

    print(f"Wrote {FEED_PATH} with {len(posts)} post(s).")


if __name__ == "__main__":
    main()
