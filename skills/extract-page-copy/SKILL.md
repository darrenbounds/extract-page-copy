---
name: extract-page-copy
description: Use when evaluating, reviewing, or critiquing copy or messaging on a local HTML file. Also use when the user provides an HTML file path and wants to read, assess, or discuss the text on the page without wading through markup.
---

# Extract Page Copy

Strip all markup, scripts, and styles from a local HTML file and output only the text a visitor would read — grouped by semantic role.

## When to Use

- User says "review the copy on this page" with an HTML path
- User asks "what does this page say" pointing to a local file
- You need to evaluate messaging before providing feedback — saves context vs. reading raw HTML

## How to Run

The extraction script lives alongside this skill. Run it with:

```bash
python3 "$(dirname "$0")/extract_copy.py" /path/to/file.html
```

Or use the reading-order mode when you want to evaluate copy flow (how the message unfolds top-to-bottom):

```bash
python3 "$(dirname "$0")/extract_copy.py" /path/to/file.html --reading-order
```

## What It Extracts

- `<meta name="description">` content
- Headings h1–h6 (always kept, no minimum length)
- Body paragraphs, list items, table cells, blockquotes, and common `div`/`span` text containers (≥25 characters by default)
- Short visible labels such as eyebrows, names, titles, form labels, card tags, and footer/meta text when class names indicate they are real copy
- Button and link text (CTAs — kept even when short)
- Nav / header / footer text (grouped separately, shorter minimum)
- `alt` text on images (it's copy — describes visuals to readers and search)

## What It Strips

- All `<script>` and `<style>` blocks and their contents
- SVG, icon, and template markup
- HTML comments
- All HTML attributes (class, id, href, src, etc.)
- Inline-hidden text (`display:none` or `visibility:hidden`)
- Duplicate strings (exact-match, case-insensitive)

## Output Modes

**Grouped** (default): Meta description → Headings → Body Copy → CTAs → Nav → Alt Text
- Best for copy audits, comparing messaging hierarchy

**Reading order** (`--reading-order`): Copy in page flow, top to bottom
- Best for evaluating narrative arc and message sequencing

## Limitations

- Class-based nav patterns (`<div class="nav">`) are not detected — only semantic `<nav>`, `<header>`, `<footer>`
- CSS hidden by external stylesheets is not evaluated; inline hidden text is skipped
- Dynamically injected content (React, Angular, etc.) won't appear — run on the rendered HTML if needed
- JavaScript-rendered pages: save the DOM from browser DevTools first

## Quick Tip

If the page is JavaScript-rendered, use Chrome DevTools → Elements → right-click `<html>` → Copy → Copy outerHTML, save to a temp file, then run the script on that.
