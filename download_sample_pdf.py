#!/usr/bin/env python3
"""
Download a sample annual report PDF for testing the financial extractor.
Uses a public SEC EDGAR URL (Apple 10-K) so no auth is required.
"""

import sys
from pathlib import Path

import requests

# Public annual report PDF (Cisco Systems 10-K FY2024 from investor relations)
SAMPLE_PDF_URL = (
    "https://s2.q4cdn.com/951347115/files/doc_financials/2024/q4/3380349a-f7c8-4189-88f7-52098a7b9c28.pdf"
)
OUTPUT_PATH = Path(__file__).resolve().parent / "sample_annual_report.pdf"
USER_AGENT = "FinancialLLMExtractor/1.0 (Testing; mailto:your-email@example.com)"


def main() -> int:
    print("Downloading sample annual report PDF...")
    print(f"URL: {SAMPLE_PDF_URL}")
    try:
        resp = requests.get(
            SAMPLE_PDF_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return 1

    OUTPUT_PATH.write_bytes(resp.content)
    print(f"Saved to: {OUTPUT_PATH}")
    print(f"Size: {len(resp.content):,} bytes")
    print("\nTest the API with:")
    print(f'  curl -X POST http://localhost:8000/upload -F "pdf=@{OUTPUT_PATH}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
