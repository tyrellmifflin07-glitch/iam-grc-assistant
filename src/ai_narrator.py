# src/ai_narrator.py
# Purpose: Use Claude API to generate audit narrative from IAM risk findings

import os
import anthropic
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client using API key from .env"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    return anthropic.Anthropic(api_key=api_key)

def build_prompt(findings: pd.DataFrame) -> str:
    """Convert findings DataFrame into a structured prompt for Claude."""
    findings_text = ""
    for _, row in findings.iterrows():
        findings_text += (
            f"- [{row['severity']}] User: {row['username']} | "
            f"Department: {row['department']} | "
            f"Role: {row['role']} | "
            f"Access Level: {row['access_level']} | "
            f"Finding: {row['risk_finding']}\n"
        )

    prompt = f"""You are a senior IAM and GRC security auditor writing an audit report for a client.

Below are IAM access risk findings detected during an automated access review:

{findings_text}

For each finding, write a professional audit narrative that includes:
1. A clear description of the risk and why it is a concern
2. The business and compliance impact
3. A specific remediation recommendation
4. The relevant compliance framework controls (use NIST 800-53, PCI-DSS, SOC 2, and HIPAA where applicable)

Format each finding as:
FINDING: [severity] - [username]
RISK: ...
IMPACT: ...
REMEDIATION: ...
FRAMEWORKS: ...

Write in professional audit language suitable for a bank or healthcare client."""

    return prompt

def generate_audit_narrative(findings: pd.DataFrame) -> str:
    """Send findings to Claude and return the audit narrative."""
    client = get_client()
    prompt = build_prompt(findings)

    print("[*] Sending findings to Claude API...")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

if __name__ == "__main__":
    from risk_engine import run_all_checks

    findings = run_all_checks("data/users.csv")
    print(f"[+] Running AI narrative generation on {len(findings)} findings...\n")

    narrative = generate_audit_narrative(findings)

    print("\n===== AI-GENERATED AUDIT NARRATIVE =====\n")
    print(narrative)

    with open("reports/audit_report.md", "w") as f:
        f.write(narrative)

    print("\n[+] Audit report saved to reports/audit_report.md")