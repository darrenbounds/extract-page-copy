---
name: extract-page-copy
description: Use when evaluating, reviewing, or critiquing copy or messaging on an HTML file or URL. Also use when the user wants to read, assess, or discuss the text on a page without wading through markup.
---

# Extract Page Copy

Strip all markup, scripts, and styles from an HTML file and output only the text a visitor would read — grouped by semantic role. This reduces token usage by up to 98% compared to passing raw HTML.

## When to Use

- User says "review the copy on this page" with an HTML path or URL
- User asks "what does this page say" pointing to a file or webpage
- You need to evaluate messaging before providing feedback — raw HTML wastes context

## How to Extract

Read the HTML source (from a file or URL), then apply these rules in order:

**Strip completely — do not include any text from:**
- `<script>`, `<style>`, `<svg>`, `<template>`, `<noscript>` elements and all their contents
- HTML comments (`<!-- ... -->`)
- Elements with inline `display:none` or `visibility:hidden` styles

**Extract and group by role:**

1. **Meta description** — `<meta name="description" content="...">` value
2. **Headings** — all `<h1>` through `<h6>` text, always include regardless of length
3. **Body copy** — `<p>`, `<li>`, `<td>`, `<th>`, `<blockquote>` text (≥25 characters)
4. **CTAs** — `<button>` text and `<a>` link text (keep even when short)
5. **Nav / Header / Footer** — text inside `<nav>`, `<header>`, `<footer>` (shorter minimum, ≥10 characters)
6. **Image alt text** — `alt` attribute values on `<img>` tags (it's copy)

**Deduplication:** Skip any string already seen (case-insensitive exact match).

## Output Format

### Grouped mode (default — best for copy audits)

```
META DESCRIPTION
----------------
[meta description text]

HEADINGS
--------
[h1] ...
[h2] ...

BODY COPY
---------
...

CTAS
----
...

NAV / HEADER / FOOTER
---------------------
...

IMAGE ALT TEXT
--------------
...
```

### Reading-order mode (best for evaluating narrative arc)

Output all extracted text in top-to-bottom document order, prefixed with its type:

```
[h1] ...
[p] ...
[cta] ...
[h2] ...
```

## Limitations

- Dynamically injected content (React, Angular, etc.) won't appear in static HTML — fetch the rendered DOM if needed
- CSS-hidden elements controlled by external stylesheets are not detected; only inline styles are evaluated
- Class-based nav patterns (`<div class="nav">`) are not grouped as nav — only semantic `<nav>`, `<header>`, `<footer>`

## Quick Tip

For JavaScript-rendered pages, get the live DOM: open browser DevTools → Elements → right-click `<html>` → Copy → Copy outerHTML → save to a file, then extract from that.
