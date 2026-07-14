# src/vendor_doc_assessment.py
# Purpose: Extract text from uploaded vendor/technology documents (PDFs) and
# generate a structured, cross-document second-line risk assessment using
# Claude — reading in trust layers and hunting for contradictions between
# documents. Returns STRUCTURED JSON (not markdown) so the output can be
# rendered directly by report_generator.build_report() with no parsing.

import os
import io
import json
import re
import anthropic
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

MAX_CHARS_PER_DOC = 6000   # cap extracted text per document to control token usage
MAX_TOTAL_CHARS = 60000    # cap total text sent to Claude across all documents


def get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client using API key from .env"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    return anthropic.Anthropic(api_key=api_key)


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> str:
    """Extract text from a single uploaded PDF file. Returns truncated text
    with a note if the document exceeds the per-document character cap."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
        full_text = "\n".join(pages_text).strip()
    except Exception as e:
        return f"[Could not extract text from {filename}: {e}]"

    if not full_text:
        return f"[No extractable text found in {filename} — it may be a scanned image PDF]"

    if len(full_text) > MAX_CHARS_PER_DOC:
        full_text = full_text[:MAX_CHARS_PER_DOC] + f"\n\n[... truncated, {len(full_text) - MAX_CHARS_PER_DOC} additional characters not shown ...]"

    return full_text


def build_document_summary(documents: dict) -> str:
    """Build a combined, length-capped text block from multiple extracted documents."""
    combined = ""
    remaining = MAX_TOTAL_CHARS
    for filename, text in documents.items():
        header = f"\n\n===== DOCUMENT: {filename} =====\n"
        chunk = header + text
        if len(chunk) > remaining:
            chunk = chunk[:remaining] + "\n[... additional document content truncated for length ...]"
        combined += chunk
        remaining -= len(chunk)
        if remaining <= 0:
            combined += "\n\n[... remaining documents not included due to length cap ...]"
            break
    return combined


def build_structured_assessment_prompt(vendor_name: str, business_unit: str, documents: dict) -> str:
    """Build the trust-layer cross-document analysis prompt, requesting
    structured JSON output matching the report_generator.build_report() schema."""
    doc_list = ", ".join(documents.keys())
    doc_text = build_document_summary(documents)

    prompt = f"""You are a senior second-line technology risk analyst performing an independent cross-document risk assessment for {vendor_name}, requested by {business_unit}.

You have been given {len(documents)} documents: {doc_list}

DOCUMENT CONTENTS:
{doc_text}

=====================================================================
METHODOLOGY — READ IN TRUST LAYERS, NOT DOCUMENT ORDER
=====================================================================

Do not assess these documents independently or in the order given. The real
issues live in the CONTRADICTIONS BETWEEN documents, not within any single
one. Read and reason in four trust layers:

LAYER 1 — Establish the system model. Which document(s) describe what this
system/vendor actually is (architecture, scope, ownership)?

LAYER 2 — Establish what SHOULD be true. Which document(s) are policies,
standards, or control commitments? These define the organization's own
declared bar — do not import external standards not implied by the documents.

LAYER 3 — Establish what IS actually true. Which document(s) are evidence —
pen test results, vulnerability scans, audit reports (SOC 1/SOC 2), SBOMs?

LAYER 4 — Establish what LEADERSHIP BELIEVES is true. Which document(s) are
executive summaries, board reports, or internal correspondence? This is
where the highest-value findings surface.

Read Layer 1 first, Layer 2 second, Layer 3 third, Layer 4 last.

=====================================================================
ANALYTICAL TEST — APPLY THESE THREE QUESTIONS
=====================================================================

1. CONTRADICTION — Do two documents make incompatible statements about the
   same control, finding, or fact?
2. UNSUPPORTED CLOSURE — Is something declared "remediated" or "effective"
   where the evidence does not demonstrate full closure?
3. CIRCULAR ASSURANCE — Is a conclusion drawn using a control or capability
   the documents themselves admit is absent or out of scope?

Only report findings supported by a SPECIFIC contradiction or gap between
two or more named documents. If a document's content was not available for
review, say so explicitly rather than assuming its contents. Rank findings
by the DECISION they change, not by technical severity score alone — a
documentation-integrity or false-assurance finding can outrank a
higher-CVSS technical defect if it means leadership was misinformed.

=====================================================================
OUTPUT FORMAT — RETURN ONLY VALID JSON, NO MARKDOWN, NO CODE FENCES, NO PREAMBLE
=====================================================================

Return a single JSON object with EXACTLY this structure:

{{
  "title": "{vendor_name}",
  "subtitle": "Cross-Document Findings, Root Cause, and Remediation Plan",
  "exec_summary": "3-5 sentences stating the bottom line, referencing specific documents. Use \\n\\n between paragraphs if more than one.",
  "bottom_line": "One or two sentences: the single most important takeaway, written for a board audience.",
  "findings": [
    {{
      "id": "F-01",
      "title": "Short finding title (no severity or F-number in the title itself)",
      "severity": "Critical",
      "observation": "What the documents say. Cite specific sections, dates, or finding IDs where present.",
      "assessment": "The business/risk consequence — the decision this changes, not just the technical issue.",
      "traceability": [
        "Document name — what it states",
        "Document name — what it states, showing the contradiction or gap"
      ],
      "position": "One to two sentences: the recommended stance and the specific condition under which it would be considered resolved."
    }}
  ],
  "root_cause": "One to two paragraphs on the single systemic cause connecting multiple findings. Use \\n\\n between paragraphs if more than one."
}}

Rules:
- severity must be exactly one of: Critical, High, Medium, Low
- Include as many findings as are genuinely supported by evidence (typically 4-10). Do not pad with speculative findings.
- Order findings array by the decision they change (most consequential first), not by severity alone.
- traceability must contain at least 2 entries per finding, each citing a specific named document.
- Return ONLY the JSON object. No explanation before or after it. No markdown code fences."""

    return prompt


def _extract_json(raw_text: str) -> dict:
    """Robustly extract a JSON object from Claude's response, tolerating
    markdown code fences or minor surrounding text if the model adds any."""
    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)

    # If there's leading/trailing text outside the JSON object, extract the
    # outermost {...} block
    if not text.startswith("{"):
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(1)

    return json.loads(text)


def _clean_field(text) -> str:
    """Strip stray markdown table artifacts (pipe characters, '**LABEL**'
    prefixes, '| --- |' separator rows) that sometimes leak into JSON string
    values because the model defaults toward that visual style even when
    asked for plain text. This keeps the final Word document free of raw
    markdown syntax showing up as literal characters."""
    if not isinstance(text, str):
        return text

    cleaned = text.strip()

    # Drop full separator lines like "| --- |" or "|---|---|" anywhere in the text
    cleaned = re.sub(r"^\s*\|[\s\-:|]+\|\s*$", "", cleaned, flags=re.MULTILINE)

    # Strip a leading pipe and an all-caps or bold label right after it,
    # e.g. "| **POSITION** actual text |" -> "actual text"
    cleaned = re.sub(r"^\s*\|\s*(\*\*[A-Za-z ]+\*\*|[A-Z][A-Z ]+:?)\s*", "", cleaned)

    # Strip any remaining leading/trailing pipe characters and whitespace
    cleaned = cleaned.strip().strip("|").strip()

    # Remove any leftover bare **Label** or **Label:** prefix (without a pipe)
    cleaned = re.sub(r"^\*\*[A-Za-z ]+\*\*:?\s*", "", cleaned)

    return cleaned.strip()


def _sanitize_assessment(data: dict) -> dict:
    """Apply _clean_field to every text field in the structured assessment,
    including nested finding fields and traceability list entries."""
    for key in ("title", "subtitle", "exec_summary", "bottom_line", "root_cause"):
        if key in data:
            data[key] = _clean_field(data[key])

    for finding in data.get("findings", []):
        for key in ("title", "observation", "assessment", "position"):
            if key in finding:
                finding[key] = _clean_field(finding[key])
        if "traceability" in finding:
            finding["traceability"] = [_clean_field(t) for t in finding["traceability"]]

    return data



def generate_structured_assessment(vendor_name: str, business_unit: str, documents: dict) -> dict:
    """Send extracted document text to Claude and return a structured
    findings dict ready for report_generator.build_report()."""
    client = get_client()
    prompt = build_structured_assessment_prompt(vendor_name, business_unit, documents)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_text = message.content[0].text

    try:
        data = _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(
            f"Could not parse structured assessment as JSON: {e}\n\n"
            f"Raw response (first 500 chars): {raw_text[:500]}"
        )

    # Basic schema validation with safe defaults
    data.setdefault("title", vendor_name)
    data.setdefault("subtitle", "Cross-Document Findings, Root Cause, and Remediation Plan")
    data.setdefault("exec_summary", "")
    data.setdefault("bottom_line", "")
    data.setdefault("root_cause", "")
    data.setdefault("findings", [])

    valid_severities = {"Critical", "High", "Medium", "Low"}
    for f in data["findings"]:
        if f.get("severity") not in valid_severities:
            f["severity"] = "Medium"
        f.setdefault("traceability", [])

    data = _sanitize_assessment(data)

    return data