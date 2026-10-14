#!/usr/bin/env python3
"""Build the blog from posts/*.md.

Each post is posts/YYYY-MM-DD-slug.md, starting with a header:

    ---
    title: My title
    date: 2026-10-21
    summary: One-line summary shown on the blog list.
    ---

followed by the article. Supported: blank line = new paragraph, "## " and "### "
headings, "> " quote, **bold**, *italic*, [text](url), and images on their own
line: ![description](/images/blog/photo.jpg "optional caption").
Output: blog/index.html and blog/<slug>/index.html. No dependencies.
"""
import datetime, html, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS, BLOG, TPL = ROOT / "posts", ROOT / "blog", ROOT / "scripts"


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def render(body):
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if not block:
            continue
        img = re.fullmatch(r'!\[(.*?)\]\(((?:https?://|/)\S+?)(?:\s+"(.*?)")?\)', block)
        if img:
            alt, src, caption = img.groups()
            cap = f"<figcaption>{inline(caption)}</figcaption>" if caption else ""
            out.append(f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy">{cap}</figure>')
        elif block.startswith("### "):
            out.append(f"<h3>{inline(block[4:])}</h3>")
        elif block.startswith("## "):
            out.append(f"<h2>{inline(block[3:])}</h2>")
        elif block.startswith(">"):
            quote = " ".join(l.lstrip("> ").strip() for l in block.splitlines())
            out.append(f"<blockquote>{inline(quote)}</blockquote>")
        else:
            out.append(f"<p>{inline(' '.join(block.splitlines()))}</p>")
    return "\n".join("    " + line for line in out)


def parse(path):
    m = re.match(r"﻿?---\s*\n(.*?)\n---\s*\n(.*)", path.read_text(encoding="utf-8"), re.S)
    if not m:
        sys.exit(f"{path.name}: missing the --- header block at the top")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    for key in ("title", "date", "summary"):
        if not meta.get(key):
            sys.exit(f"{path.name}: header is missing '{key}:'")
    try:
        date = datetime.date.fromisoformat(meta["date"])
    except ValueError:
        sys.exit(f"{path.name}: date must look like 2026-10-21")
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    return dict(meta, date=date, slug=slug, body=m.group(2))


def fill(template, **values):
    for k, v in values.items():
        template = template.replace("{{" + k + "}}", v)
    return template


def main():
    posts = sorted((parse(p) for p in POSTS.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md")), key=lambda p: p["date"], reverse=True)
    post_tpl = (TPL / "post.template.html").read_text(encoding="utf-8")
    index_tpl = (TPL / "index.template.html").read_text(encoding="utf-8")

    slugs = {p["slug"] for p in posts}
    for d in BLOG.iterdir():  # drop pages for deleted posts
        if d.is_dir() and d.name not in slugs:
            shutil.rmtree(d)

    items = []
    for p in posts:
        (BLOG / p["slug"]).mkdir(parents=True, exist_ok=True)
        (BLOG / p["slug"] / "index.html").write_text(fill(
            post_tpl,
            TITLE=html.escape(p["title"], quote=False),
            SUMMARY=html.escape(p["summary"]),
            DATE_LONG=f"{p['date'].day} {p['date']:%B %Y}",
            CONTENT=render(p["body"]),
        ), encoding="utf-8")
        items.append(f'''    <a class="post fade-in" href="/blog/{p['slug']}/">
      <p class="post-meta">{p['date'].day} {p['date']:%b %Y}</p>
      <h2 class="post-title">{html.escape(p['title'], quote=False)}</h2>
      <p class="post-summary">{html.escape(p['summary'], quote=False)}</p>
    </a>''')
    (BLOG / "index.html").write_text(fill(index_tpl, POSTS="\n".join(items)), encoding="utf-8")
    print(f"Built {len(posts)} post(s)")


main()
