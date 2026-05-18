# extract-page-copy

Extract visitor-readable copy from local HTML so AI agents can review messaging without spending context on markup, scripts, styles, and framework payloads.

This is a small Agent Skill for copy review work. It keeps the workflow intentionally narrow: point it at a local HTML file and get either grouped copy or reading-order copy.

GitHub: https://github.com/darrenbounds/extract-page-copy

## Why this exists

When an agent is asked to review website copy, raw HTML is usually the wrong input. Modern marketing pages often include large JavaScript payloads, serialized app state, SVGs, tracking code, attributes, and styling that do not help with copy critique.

This skill extracts the words a visitor is likely to read:

- meta description
- headings
- body copy
- CTAs, buttons, and links
- navigation, header, and footer text
- image alt text

It strips scripts, styles, comments, SVG/icon markup, template noise, attributes, inline-hidden text, and exact duplicate strings.

## Case study: Shopify Canada homepage

The token comparison uses `https://www.shopify.com/ca`, fetched on 2026-05-17. The raw Shopify HTML is not committed to this repository; the commands and measurements are recorded in `AUDIT.md`.

Measured from the Shopify fetch recorded in `AUDIT.md`:

- raw HTML: `426,131` bytes, about `106,533` tokens using a chars/4 estimate
- grouped copy output: `8,100` bytes, about `2,025` tokens
- reading-order output: `8,440` bytes, about `2,110` tokens

For grouped output, that is about `52.6x` smaller, or a `98.1%` reduction in estimated tokens, before the agent starts the copy review.

## Example

The `examples/` directory contains a small synthetic page and generated outputs so the expected format is easy to inspect without republishing a third-party page.

```bash
python3 skills/extract-page-copy/extract_copy.py examples/sample.html
python3 skills/extract-page-copy/extract_copy.py examples/sample.html --reading-order
```

## Install

For Claude Code, copy the skill folder into your local skills directory:

```bash
cp -R skills/extract-page-copy ~/.claude/skills/extract-page-copy
```

For other local coding agents, keep the `skills/extract-page-copy` folder available and have the agent run the script directly.

## Usage

Grouped output is the default and is best for copy audits:

```bash
python3 skills/extract-page-copy/extract_copy.py path/to/page.html
```

Reading-order output is best for evaluating how the page message unfolds top to bottom:

```bash
python3 skills/extract-page-copy/extract_copy.py path/to/page.html --reading-order
```

## Tests

Run the fixture-based tests with the standard library only:

```bash
python3 tests/test_extract_copy.py
```

The tests cover:

- grouped output
- reading-order output
- script, style, comment, and inline-hidden copy stripping

## Publishing

GitHub is the primary distribution target for this artifact: https://github.com/darrenbounds/extract-page-copy

This README does not claim listing or submission status for any public skill directory.

## License

MIT
