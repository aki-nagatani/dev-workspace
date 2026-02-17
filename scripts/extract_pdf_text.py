#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF からテキストを抽出するスクリプト（obsidian-inbox-summarize 用）。

1. pypdf でテキスト抽出を試行
2. テキストが十分に得られない場合のフォールバック（優先順）:
   a) おたよりナビ OCR API（http://localhost:5003/ 固定。OTAYORI_OCR_API_KEY は認証時のみ。OTAYORI_OCR_TIMEOUT でタイムアウト秒数を指定可能、デフォルト120）
      - API で検索可能PDFを取得し、pypdf で再抽出
   b) Azure Document Intelligence 直接（AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY が設定されている場合）

使用方法:
  python extract_pdf_text.py <PDFファイルパス>

出力:
  - 成功時: 抽出したテキストを stdout に出力
  - 失敗時: 空文字を出力し、終了コード 1 で終了

依存:
  - pypdf: 必須（pip install pypdf）
  - azure-ai-documentintelligence: フォールバックb用オプション（pip install azure-ai-documentintelligence）
  - requests: フォールバックa用オプション（pip install requests）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# テキスト不足とみなす閾値（文字数）。これ未満ならフォールバックを試行。
MIN_TEXT_LENGTH = 50


def extract_with_pypdf(pdf_path: Path) -> str:
    """pypdf でテキストを抽出する。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n".join(parts).strip() if parts else ""


OTAYORI_OCR_API_BASE = "http://localhost:5003"


def extract_with_otayori_api(pdf_path: Path) -> str:
    """
    おたよりナビ OCR API（POST /api/ocr/searchable-pdf）で検索可能PDFを取得し、pypdf でテキスト抽出する。
    URL は固定で http://localhost:5003/ を使用。OTAYORI_OCR_API_KEY は認証が必要な場合のみ設定（未設定なら認証なしで呼び出す）。
    """
    api_url = OTAYORI_OCR_API_BASE.rstrip("/")

    try:
        import requests
    except ImportError:
        return ""

    endpoint = f"{api_url}/api/ocr/searchable-pdf"
    api_key = os.environ.get("OTAYORI_OCR_API_KEY", "").strip()
    timeout = int(os.environ.get("OTAYORI_OCR_TIMEOUT", "120"))
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    with pdf_path.open("rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        try:
            resp = requests.post(
                endpoint,
                files=files,
                headers=headers,
                timeout=timeout,
            )
        except requests.RequestException:
            return ""

    if resp.status_code != 200:
        return ""
    pdf_bytes = resp.content
    if not pdf_bytes:
        return ""
    # 検索可能PDFを一時ファイルに書き、pypdf で再抽出
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)
    try:
        text = extract_with_pypdf(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return text


def extract_with_azure(content: bytes) -> str:
    """
    Azure Document Intelligence（Read モデル）で OCR してテキストを抽出する。
    環境変数 AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY が必要。
    """
    import os

    endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "").strip()
    key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY", "").strip()
    if not endpoint or not key:
        return ""

    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
        from azure.core.credentials import AzureKeyCredential
    except ImportError:
        return ""

    try:
        client = DocumentIntelligenceClient(
            endpoint=endpoint.rstrip("/"),
            credential=AzureKeyCredential(key),
        )
        poller = client.begin_analyze_document(
            "prebuilt-read",
            AnalyzeDocumentRequest(bytes_source=content),
            locale="ja",
        )
        result = poller.result()
    except Exception:
        return ""

    content_attr = getattr(result, "content", None)
    if content_attr is None and isinstance(result, dict):
        content_attr = result.get("content")
    if content_attr is None or not isinstance(content_attr, str):
        return ""
    return content_attr.strip()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: extract_pdf_text.py <PDF_PATH>", file=sys.stderr)
        return 1

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        return 1
    if not pdf_path.is_file():
        print(f"Not a file: {pdf_path}", file=sys.stderr)
        return 1

    text = extract_with_pypdf(pdf_path)

    if len(text) < MIN_TEXT_LENGTH:
        api_text = extract_with_otayori_api(pdf_path)
        if api_text:
            text = api_text
        else:
            content = pdf_path.read_bytes()
            azure_text = extract_with_azure(content)
            if azure_text:
                text = azure_text

    if text:
        print(text)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
