# How to publish a letter

1. Add a new file in this folder named `YYYY-MM-DD-short-title.md`
   (e.g. `2026-10-21-how-to-price-your-product.md`). The part after the date becomes the web address.
2. Start it with this header, then write the article below it:

```
---
title: Your post title
date: 2026-10-21
summary: One line shown under the title on the letters list.
---

Your first paragraph. A blank line starts a new paragraph.

## A subheading

More text with **bold**, *italic* and [a link](https://example.com).

> A quote looks like this.
```

3. To add a picture, upload it to the `images/letters/` folder (e.g. `images/letters/caroline.jpg`), then put this on its own line in your post:

```
![Caroline wearing the product](/images/letters/caroline.jpg "Optional caption shown under the picture")
```

   The text in square brackets describes the picture for screen readers and search engines. The caption in quotes is optional.
   Keep pictures under about 500 KB (resize or compress them first) so the page loads fast.

4. Commit to `main`. A couple of minutes later the post is live at `herveky.com/letters/short-title/`
   and appears at the top of the letters list (newest first).

To edit a post, edit its file. To remove one, delete its file.
