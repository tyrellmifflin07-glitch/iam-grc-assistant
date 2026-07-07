# src/ai_narrator.py
# Purpose: Use Claude API to generate audit narrative from IAM risk findings
# Scalable design: aggregates statistics and narrates top-priority findings only,
# supporting datasets from 10 users to 100,000+ users

import os
import anthropic
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Cap on individually-narrated findings sent to Claude.
# Critical and High findings are prioritized; Medium/Low are summarized statistically.
MAX_DETAILED_FINDINGS = 50

def get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client using API key from .env"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    return anthropic.Anthropic(api_key=api_key)

def build_aggregate_statistics(findings: pd.DataFrame) -> str:
    """Build an aggregate statistical summary of all findings for the prompt."""
    lines = []
    lines.append(f"TOTAL FINDINGS: {len(findings):,}")

    # By severity
    lines.append("\nFINDINGS BY SEVERITY:")
    for sev, count in findings["severity"].value_counts().items():
        lines.append(f"- {sev}: {count:,}")

    # By finding type
    lines.append("\nFINDINGS BY TYPE:")
    for ftype, count in findings["risk_finding"].value_counts().items():
        lines.append(f"- {ftype}: {count:,}")

    # By department (top 10)
    lines.append("\nTOP DEPARTMENTS BY FINDING COUNT:")
    for dept, count in findings["department"].value_counts().head(10).items():
        lines.append(f"- {dept}: {count:,}")

    # By taxonomy if present
    if "risk_taxonomy" in findings.columns:
        lines.append("\nFINDINGS BY RISK TAXONOMY:")
        for tax, count in findings["risk_taxonomy"].value_counts().items():
            lines.append(f"- {tax}: {count:,}")

    return "\n".join(lines)

def select_priority_findings(findings: pd.DataFrame) -> pd.DataFrame:
    """Select the highest-priority findings for detailed narration, capped."""
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    df = findings.copy()
    df["_sev_rank"] = df["severity"].map(severity_order).fillna(4)
    df = df.sort_values("_sev_rank")
    return df.head(MAX_DETAILED_FINDINGS).drop(columns=["_sev_rank"])

def build_prompt(findings: pd.DataFrame) -> str:
    """Build a scalable prompt: aggregate stats + top priority findings only."""
    total = len(findings)
    stats = build_aggregate_statistics(findings)
    priority = select_priority_findings(findings)

    findings_text = ""
    for _, row in priority.iterrows():
        findings_text += (
            f"- [{row['severity']}] User: {row['username']} | "
            f"Department: {row['department']} | "
            f"Role: {row['role']} | "
            f"Access Level: {row['access_level']} | "
            f"Finding: {row['risk_finding']}\n"
        )

    detailed_note = ""
    if total > MAX_DETAILED_FINDINGS:
        detailed_note = (
            f"\nNOTE: This access review identified {total:,} total findings. "
            f"The {len(priority)} highest-severity findings are detailed below for "
            f"individual analysis. Remaining findings are represented in the "
            f"aggregate statistics and should be addressed through the thematic "
            f"remediation recommendations."
        )

    prompt = f"""You are a senior IAM and GRC security auditor writing an audit report for a client after an automated access review.

===== AGGREGATE FINDINGS STATISTICS =====
{stats}
{detailed_note}

===== HIGHEST-PRIORITY FINDINGS (DETAILED) =====
{findings_text}

Write a professional audit report with these sections:

## Executive Summary
Overall risk posture based on the aggregate statistics. Reference the scale of the review and the distribution of findings.

## Thematic Risk Analysis
Analyze the PATTERNS in the aggregate data — which finding types dominate, which departments show concentration of risk, what the severity distribution indicates about control maturity. This section addresses ALL findings statistically, not individually.

## Priority Findings Detail
For each detailed finding listed above, write:
FINDING: [severity] - [username]
RISK: (concise — 2-3 sentences)
REMEDIATION: (specific action with timeline)
FRAMEWORKS: (relevant NIST 800-53, PCI-DSS, SOC 2, HIPAA, COSO, COBIT, DORA controls)

## Systemic Remediation Recommendations
Program-level recommendations that address the full population of findings — automation, process changes, and governance improvements that remediate findings at scale rather than one at a time.

Write in professional audit language suitable for a bank or healthcare client. Be concise in individual findings; be insightful in the thematic analysis."""

    return prompt

def generate_audit_narrative(findings: pd.DataFrame) -> str:
    """Send findings to Claude and return the audit narrative. Scales to any dataset size."""
    client = get_client()
    prompt = build_prompt(findings)

    print(f"[*] Sending {min(len(findings), MAX_DETAILED_FINDINGS)} priority findings "
          f"+ aggregate statistics for {len(findings):,} total findings to Claude API...")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from risk_engine import run_all_checks

    findings = run_all_checks("data/users.csv")
    print(f"[+] Running AI narrative generation on {len(findings):,} findings...\n")

    narrative = generate_audit_narrative(findings)

    print("\n===== AI-GENERATED AUDIT NARRATIVE =====\n")
    print(narrative)

    with open("reports/audit_report.md", "w") as f:
        f.write(narrative)

    print("\n[+] Audit report saved to reports/audit_report.md")