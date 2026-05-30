#!/usr/bin/env python3
"""
Extract visible copy from a local HTML file for copy review.
Strips all CSS, JS, attributes, and structural noise; outputs only reader-visible text.

Usage:
  python3 extract_copy.py <file.html>              # grouped by role (default)
  python3 extract_copy.py <file.html> --reading-order   # page reading order
"""
import sys
import re
from html.parser import HTMLParser

SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'path', 'symbol', 'defs', 'use', 'iframe'}
HEADING_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
BLOCK_TAGS = {
    'p', 'li', 'td', 'th', 'blockquote', 'figcaption', 'dt', 'dd',
    'caption', 'summary', 'legend', 'article', 'section', 'aside',
    'div', 'span', 'label',
}
NAV_CONTEXT_TAGS = {'nav', 'header', 'footer'}
CTA_TAGS = {'button', 'a'}
MIN_BODY_LEN = 25
SHORT_TEXT_CLASS_HINTS = {
    'eyebrow', 'kicker', 'tag', 'name', 'title', 'property', 'brand',
    'meta', 'req', 'foot', 'prompt', 'result', 'lead', 'eb',
}


class CopyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.skip_stack = []
        self.nav_depth = 0
        self.frames = []

        # (role, text) — roles: 'meta', 'h1'..'h6', 'body', 'nav', 'cta', 'alt'
        self.items = []
        self.seen = set()

    # ------------------------------------------------------------------ helpers

    def _clean(self, parts):
        text = re.sub(r'\s+', ' ', ' '.join(parts)).strip()
        return text

    def _add(self, role, text):
        if not text:
            return
        key = text.lower()
        if key in self.seen:
            return
        self.seen.add(key)
        self.items.append((role, text))

    # ------------------------------------------------------------------ parser callbacks

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)

        # Meta description — no body content
        if tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            if name == 'description':
                content = attrs_dict.get('content', '').strip()
                if content:
                    self._add('meta', content)
            return

        # Alt text on images — it's real copy
        if tag == 'img':
            alt = attrs_dict.get('alt', '').strip()
            if alt and alt.lower() not in ('', 'image', 'photo', 'img', 'icon'):
                self._add('alt', alt)
            return

        if self.skip_depth > 0:
            self.skip_depth += 1
            self.skip_stack.append(tag)
            return

        if tag in SKIP_TAGS:
            self.skip_depth += 1
            self.skip_stack.append(tag)
            return

        style = attrs_dict.get('style', '').lower().replace(' ', '')
        if 'display:none' in style or 'visibility:hidden' in style:
            self.skip_depth += 1
            self.skip_stack.append(tag)
            return

        if tag in NAV_CONTEXT_TAGS:
            self.nav_depth += 1

        if tag in HEADING_TAGS or tag in BLOCK_TAGS or tag in CTA_TAGS:
            self.frames.append({'tag': tag, 'parts': [], 'class': attrs_dict.get('class', '')})

    def handle_endtag(self, tag):
        tag = tag.lower()

        if self.skip_depth > 0:
            if self.skip_stack and self.skip_stack[-1] == tag:
                self.skip_stack.pop()
                self.skip_depth -= 1
            return

        if tag in NAV_CONTEXT_TAGS:
            self.nav_depth = max(0, self.nav_depth - 1)

        frame = None
        if self.frames and self.frames[-1]['tag'] == tag:
            frame = self.frames.pop()

        if not frame:
            return

        text = self._clean(frame['parts'])
        parent_tags_that_need_child_text = HEADING_TAGS | CTA_TAGS | {'p', 'li', 'blockquote', 'summary', 'label', 'span'}
        if self.frames and text and self.frames[-1]['tag'] in parent_tags_that_need_child_text:
            self.frames[-1]['parts'].append(text)

        parent_tag = self.frames[-1]['tag'] if self.frames else None
        inside_heading_or_cta = any(f['tag'] in HEADING_TAGS or f['tag'] in CTA_TAGS for f in self.frames)

        if tag in HEADING_TAGS:
            self._add(tag, text)

        elif tag in BLOCK_TAGS:
            role = 'nav' if self.nav_depth > 0 else 'body'
            if tag in {'div', 'span'} and (inside_heading_or_cta or parent_tag == 'li'):
                return
            classes = set(frame.get('class', '').lower().replace('-', ' ').replace('_', ' ').split())
            keep_short = bool(classes & SHORT_TEXT_CLASS_HINTS) and len(text) >= 2 and not re.fullmatch(r'[\W\d_]+', text)
            if role == 'nav' or tag == 'label' or keep_short or len(text) >= MIN_BODY_LEN:
                self._add(role, text)

        elif tag in CTA_TAGS:
            # Only keep CTAs with meaningful text (not just icons/whitespace)
            if len(text) >= 2:
                self._add('cta', text)

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        text = data.strip()
        if text and self.frames:
            self.frames[-1]['parts'].append(text)

    def handle_comment(self, data):
        pass  # discard HTML comments


# ------------------------------------------------------------------ output formatters

def grouped_output(items):
    """Group extracted copy by semantic role."""
    buckets = {
        'meta': [], 'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
        'body': [], 'cta': [], 'nav': [], 'alt': [],
    }
    for role, text in items:
        if role in buckets:
            buckets[role].append(text)

    lines = []

    if buckets['meta']:
        lines.append("## Meta Description")
        for t in buckets['meta']:
            lines.append(t)
        lines.append("")

    headings = []
    for level in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        for t in buckets[level]:
            headings.append(('#' * int(level[1])) + ' ' + t)
    if headings:
        lines.append("## Headings")
        lines.extend(headings)
        lines.append("")

    if buckets['body']:
        lines.append("## Body Copy")
        for t in buckets['body']:
            lines.append(t)
            lines.append("")

    if buckets['cta']:
        lines.append("## CTAs / Buttons / Links")
        seen_ctas = []
        for t in buckets['cta']:
            # Skip CTAs that are just a repeat of heading text
            if t.lower() not in {h.split(' ', 1)[-1].lower() for h in headings}:
                seen_ctas.append(t)
        for t in seen_ctas:
            lines.append(f"- {t}")
        lines.append("")

    if buckets['nav']:
        lines.append("## Navigation / Header / Footer")
        for t in buckets['nav']:
            lines.append(f"- {t}")
        lines.append("")

    if buckets['alt']:
        lines.append("## Image Alt Text")
        for t in buckets['alt']:
            lines.append(f"- {t}")
        lines.append("")

    return '\n'.join(lines)


def reading_order_output(items):
    """Output copy in the order it appears on the page."""
    lines = []
    for role, text in items:
        if role.startswith('h') and role[1:].isdigit():
            level = int(role[1])
            lines.append('#' * level + ' ' + text)
        elif role == 'meta':
            lines.append(f"[meta description] {text}")
        elif role == 'alt':
            lines.append(f"[img alt] {text}")
        elif role == 'cta':
            lines.append(f"[CTA] {text}")
        else:
            lines.append(text)
            lines.append("")
    return '\n'.join(lines)


def stats(items):
    roles = [r for r, _ in items]
    headings = sum(1 for r in roles if r.startswith('h') and r[1:].isdigit())
    body = sum(1 for r in roles if r == 'body')
    words = sum(len(t.split()) for _, t in items)
    return f"[{headings} headings | {body} paragraphs/blocks | ~{words} words]"


# ------------------------------------------------------------------ main

def main():
    args = sys.argv[1:]
    reading_order = '--reading-order' in args
    paths = [a for a in args if not a.startswith('--')]

    if not paths:
        print(f"Usage: {sys.argv[0]} <file.html> [--reading-order]", file=sys.stderr)
        sys.exit(1)

    for path in paths:
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                html = f.read()
        except FileNotFoundError:
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)

        parser = CopyParser()
        parser.feed(html)

        if len(paths) > 1:
            print(f"\n{'='*60}\n{path}\n{'='*60}")

        print(stats(parser.items))
        print()

        if reading_order:
            print(reading_order_output(parser.items))
        else:
            print(grouped_output(parser.items))


if __name__ == '__main__':
    main()
