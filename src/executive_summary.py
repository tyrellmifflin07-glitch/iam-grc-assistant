# src/executive_summary.py
# Purpose: Generate a concise executive summary from IAM risk findings

from risk_engine import run_all_checks

def generate_executive_summary(findings):
    total = len(findings)

    severity_counts = findings["severity"].value_counts().to_dict()

    critical = severity_counts.get("Critical", 0)
    high = severity_counts.get("High", 0)
    medium = severity_counts.get("Medium", 0)
    low = severity_counts.get("Low", 0)

    if critical > 0:
        overall_risk = "Critical"
    elif high > 0:
        overall_risk = "High"
    elif medium > 0:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"

    summary = f"""
# Executive IAM Risk Summary

## Overall Risk Rating
**{overall_risk}**

## Findings Overview
- Total Findings: {total}
- Critical Findings: {critical}
- High Findings: {high}
- Medium Findings: {medium}
- Low Findings: {low}

## Key Business Risks
This access review identified identity and access management risks that may expose the organization to unauthorized access, audit findings, compliance gaps, and potential misuse of sensitive systems.

## Priority Actions
1. Immediately remediate Critical findings.
2. Review and approve or remove High-risk privileged access.
3. Validate dormant accounts and disable access that is no longer required.
4. Strengthen Joiner-Mover-Leaver controls.
5. Establish recurring access certification reviews.

## Compliance Impact
These findings may impact control expectations under NIST 800-53, PCI-DSS, SOC 2, HIPAA, and general IAM governance standards.

## Executive Recommendation
Leadership should treat this as a priority IAM governance issue and assign ownership for remediation, evidence collection, and recurring access review monitoring.
"""

    return summary


if __name__ == "__main__":
    findings = run_all_checks("data/users.csv")

    summary = generate_executive_summary(findings)

    print(summary)

    with open("reports/executive_summary.md", "w") as f:
        f.write(summary)

    print("\n[+] Executive summary saved to reports/executive_summary.md")