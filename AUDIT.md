# Audit Notes

This file records the evidence behind the public example and token-efficiency comparison for `extract-page-copy`.

GitHub repository:

```text
https://github.com/darrenbounds/extract-page-copy
```

## Public Example Source

Source URL:

```text
https://www.shopify.com/ca
```

Fetch date:

```text
2026-05-17
```

Fetch command:

```bash
curl -sL https://www.shopify.com/ca -o /tmp/shopify-ca-2026-05-17.html
```

Generated grouped output:

```bash
python3 skills/extract-page-copy/extract_copy.py /tmp/shopify-ca-2026-05-17.html > /tmp/shopify-ca-2026-05-17.grouped.txt
```

Generated reading-order output:

```bash
python3 skills/extract-page-copy/extract_copy.py /tmp/shopify-ca-2026-05-17.html --reading-order > /tmp/shopify-ca-2026-05-17.reading-order.txt
```

The raw Shopify HTML and generated Shopify copy outputs are not committed to this repository. The checked-in `examples/` directory uses a small synthetic page to demonstrate the output format.

## Measurement Method

Token counts are estimates, not model-tokenizer counts. They use the same simple `bytes / 4` approximation for raw HTML and extracted outputs.

This keeps the comparison auditable with only standard local tools and avoids depending on a tokenizer package.

Measurement command:

```bash
python3.11 -c 'from pathlib import Path; paths=("/tmp/shopify-ca-2026-05-17.html","/tmp/shopify-ca-2026-05-17.grouped.txt","/tmp/shopify-ca-2026-05-17.reading-order.txt"); sizes={p:len(Path(p).read_bytes()) for p in paths}; [print(f"{Path(p).name}: bytes={sizes[p]:,} est_tokens={round(sizes[p]/4):,}") for p in paths]; raw=sizes["/tmp/shopify-ca-2026-05-17.html"]/4; grouped=sizes["/tmp/shopify-ca-2026-05-17.grouped.txt"]/4; reading=sizes["/tmp/shopify-ca-2026-05-17.reading-order.txt"]/4; print(f"grouped_ratio={raw/grouped:.1f}x grouped_reduction={(1-grouped/raw)*100:.1f}%"); print(f"reading_ratio={raw/reading:.1f}x reading_reduction={(1-reading/raw)*100:.1f}%")'
```

Observed output:

```text
shopify-ca-2026-05-17.html: bytes=426,131 est_tokens=106,533
shopify-ca-2026-05-17.grouped.txt: bytes=8,100 est_tokens=2,025
shopify-ca-2026-05-17.reading-order.txt: bytes=8,440 est_tokens=2,110
grouped_ratio=52.6x grouped_reduction=98.1%
reading_ratio=50.5x reading_reduction=98.0%
```

## Verification Commands

Fixture tests:

```bash
python3 tests/test_extract_copy.py
```

Observed output:

```text
3 tests passed
```

Repository status after the initial packaging pass:

```bash
git status --short --branch
```

Observed output:

```text
## main
```

## Public Directory Claims

The README does not claim the skill has been submitted to or listed in any public skill directory.

## Publishing Status

The package is intended to be published at:

```text
https://github.com/darrenbounds/extract-page-copy
```
