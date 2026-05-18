#!/usr/bin/env python3
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "extract-page-copy" / "extract_copy.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module():
    spec = importlib.util.spec_from_file_location("extract_copy", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_fixture(name):
    module = load_module()
    parser = module.CopyParser()
    parser.feed((FIXTURES / name).read_text(encoding="utf-8"))
    return module, parser.items


def test_grouped_output():
    module, items = parse_fixture("grouped.html")
    output = module.grouped_output(items)

    assert "## Meta Description" in output
    assert "A practical page for testing copy extraction." in output
    assert "# Build a better checkout" in output
    assert "Give customers a faster path from product discovery to completed purchase." in output
    assert "- Start free trial" in output
    assert "- Home" in output
    assert "- Merchant dashboard showing checkout performance" in output


def test_reading_order_output():
    module, items = parse_fixture("reading-order.html")
    output = module.reading_order_output(items)
    expected = "\n".join(
        [
            "[meta description] Reading order keeps the page narrative intact.",
            "# Launch the campaign",
            "Start with the promise, then explain why the offer matters.",
            "",
            "## Measure what changes",
            "[CTA] See results",
        ]
    )

    assert output == expected


def test_script_style_comment_and_hidden_copy_are_stripped():
    module, items = parse_fixture("stripping.html")
    output = module.grouped_output(items)

    assert "Only visible copy remains" in output
    assert "This paragraph should be the only body copy in the stripped output." in output
    assert "Do not extract CSS" not in output
    assert "Do not extract JavaScript" not in output
    assert "Do not extract comments" not in output
    assert "Do not extract hidden copy" not in output


if __name__ == "__main__":
    tests = [
        test_grouped_output,
        test_reading_order_output,
        test_script_style_comment_and_hidden_copy_are_stripped,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
