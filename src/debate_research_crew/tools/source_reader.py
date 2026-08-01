import io
import re

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
MAX_PDF_PAGES = 40
MAX_OUTPUT_CHARS = 18000
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
NON_CONTENT_TAGS = ("script", "style", "nav", "header", "footer", "aside", "form")


class SourceReaderInput(BaseModel):
    """Input schema for SourceReaderTool."""

    url: str = Field(..., description="Direct URL of the web page or PDF to read.")


class SourceReaderTool(BaseTool):
    name: str = "read_source_document"
    description: str = (
        "Read the readable text of a web page or PDF at a URL. Extracts text from "
        "government, agency, and academic PDF reports, so use this whenever a "
        "citation points at a .pdf file. Returns plain text only, truncated to a "
        "fixed budget, and never raw file bytes."
    )
    args_schema: type[BaseModel] = SourceReaderInput

    def _run(self, url: str) -> str:
        try:
            content, content_type = _download(url)
        except requests.RequestException as exc:
            return f"Could not retrieve {url}: {exc}"
        except ValueError as exc:
            return f"Could not read {url}: {exc}"

        is_pdf = "application/pdf" in content_type or content[:5] == b"%PDF-"
        try:
            text = _pdf_text(content) if is_pdf else _html_text(content)
        except Exception as exc:
            kind = "PDF" if is_pdf else "HTML"
            return f"Could not parse {kind} at {url}: {exc}"

        if not text:
            return f"No extractable text found at {url}."
        return _truncate(text)


def _download(url: str) -> tuple[bytes, str]:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=45, stream=True)
    response.raise_for_status()

    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=65536):
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_DOWNLOAD_BYTES:
            response.close()
            limit_mb = MAX_DOWNLOAD_BYTES // (1024 * 1024)
            raise ValueError(f"document is larger than {limit_mb} MB")

    return b"".join(chunks), response.headers.get("content-type", "").lower()


def _pdf_text(content: bytes) -> str:
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        total_pages = len(pdf.pages)
        for page in pdf.pages[:MAX_PDF_PAGES]:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)

    text = _normalize("\n\n".join(pages))
    if total_pages > MAX_PDF_PAGES:
        text += (
            f"\n\n[Read the first {MAX_PDF_PAGES} of {total_pages} pages. "
            f"Cite a locator only from the text shown above.]"
        )
    return text


def _html_text(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    for tag in soup(NON_CONTENT_TAGS):
        tag.decompose()
    return _normalize(soup.get_text(" ", strip=True))


def _normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return (
        text[:MAX_OUTPUT_CHARS]
        + "\n\n[Truncated. Request a more specific page or section if you need more.]"
    )
