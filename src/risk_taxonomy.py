# src/risk_taxonomy.py
# Purpose: Classify IAM/GRC risk findings into enterprise risk taxonomy categories
# Taxonomy aligned to enterprise risk management frameworks:
# Technology Risk, Cyber Risk, Data Risk, AI Risk

import pandas as pd

# Each finding type maps to a primary and secondary taxonomy category
TAXONOMY_MAP = {
    "Terminated user with active system record": {
        "primary": "Cyber Risk",
        "secondary": "Technology Risk",
        "rationale": "Unauthorized access vector via orphaned credentials — identity lifecycle control failure"
    },
    "Contractor with privileged access": {
        "primary": "Cyber Risk",
        "secondary": "Third-Party Risk",
        "rationale": "Elevated third-party access without commensurate oversight — least privilege violation"
    },
    "Dormant account — no login in 90+ days": {
        "primary": "Cyber Risk",
        "secondary": "Technology Risk",
        "rationale": "Unmonitored credential exposure — stale access increases undetected compromise risk"
    },
    "Privileged user with no manager assigned": {
        "primary": "Technology Risk",
        "secondary": "Cyber Risk",
        "rationale": "Governance gap — privileged access without accountable oversight or approval chain"
    },
}

# Taxonomy category definitions for reporting context
TAXONOMY_DEFINITIONS = {
    "Cyber Risk": "Risk of unauthorized access, data breach, or malicious activity against systems and identities",
    "Technology Risk": "Risk arising from technology failures, misconfigurations, or governance gaps in IT operations",
    "Data Risk": "Risk related to data integrity, privacy, retention, classification, or unauthorized disclosure",
    "AI Risk": "Risk from AI model behavior, training data, automated decisions, or ungoverned AI adoption",
    "Third-Party Risk": "Risk introduced through vendors, contractors, and external service providers",
}

def classify_finding(finding_text: str) -> dict:
    """Return taxonomy classification for a given finding description."""
    for key, classification in TAXONOMY_MAP.items():
        if key.lower() in finding_text.lower():
            return classification
    return {
        "primary": "Technology Risk",
        "secondary": "—",
        "rationale": "Default classification — review required"
    }

def add_taxonomy_columns(findings: pd.DataFrame) -> pd.DataFrame:
    """Add risk taxonomy classification columns to a findings DataFrame."""
    df = findings.copy()
    df["risk_taxonomy"] = df["risk_finding"].apply(lambda x: classify_finding(x)["primary"])
    df["secondary_taxonomy"] = df["risk_finding"].apply(lambda x: classify_finding(x)["secondary"])
    df["taxonomy_rationale"] = df["risk_finding"].apply(lambda x: classify_finding(x)["rationale"])
    return df

def taxonomy_summary(findings: pd.DataFrame) -> pd.DataFrame:
    """Summarize findings count by risk taxonomy category."""
    df = add_taxonomy_columns(findings)
    summary = df.groupby("risk_taxonomy").size().reset_index(name="findings_count")
    summary = summary.sort_values("findings_count", ascending=False).reset_index(drop=True)
    return summary


if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from risk_engine import run_all_checks

    findings = run_all_checks("data/users.csv")
    classified = add_taxonomy_columns(findings)

    print("\n===== RISK TAXONOMY CLASSIFICATION =====\n")
    for _, row in classified.iterrows():
        print(f"[{row['severity']}] {row['username']} — {row['risk_finding']}")
        print(f"    Primary: {row['risk_taxonomy']} | Secondary: {row['secondary_taxonomy']}")
        print(f"    Rationale: {row['taxonomy_rationale']}\n")

    print("===== TAXONOMY SUMMARY =====")
    print(taxonomy_summary(findings).to_string(index=False))