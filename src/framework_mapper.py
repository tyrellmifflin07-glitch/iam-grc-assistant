# src/framework_mapper.py
# Purpose: Map IAM risk findings to specific compliance framework controls
# Frameworks: NIST 800-53, PCI-DSS, SOC 2, HIPAA, COSO, COBIT, DORA

FRAMEWORK_CONTROLS = {
    "Terminated user with active system record": {
        "NIST 800-53": [
            "AC-2: Account Management — remove/disable accounts upon termination",
            "PS-4: Personnel Termination — revoke access same day as separation"
        ],
        "PCI-DSS": [
            "Req 8.1.4: Remove/disable inactive user accounts within 90 days",
            "Req 8.2.6: Immediately revoke access for terminated users"
        ],
        "SOC 2": [
            "CC6.2: Logical access removed when no longer needed",
            "CC6.3: User deregistration procedures including termination"
        ],
        "HIPAA": [
            "45 CFR §164.308(a)(3)(ii)(C): Termination procedures for ePHI access",
            "45 CFR §164.312(a)(2)(i): Unique user identification and access control"
        ],
        "COSO": [
            "CC Principle 10: Control activities over access removal",
            "CC Principle 12: Deployment of policies for personnel changes"
        ],
        "COBIT": [
            "DSS05.04: Manage user identity and logical access",
            "DSS06.03: Manage roles, responsibilities, and access privileges"
        ],
        "DORA": [
            "Art. 9: ICT access management — timely revocation of access rights"
        ]
    },
    "Contractor with privileged access": {
        "NIST 800-53": [
            "AC-2: Account Management — least privilege for all accounts",
            "AC-6: Least Privilege — minimum access rights required",
            "IA-2: MFA required for privileged accounts"
        ],
        "PCI-DSS": [
            "Req 7.2.1: Access rights based on job classification",
            "Req 8.2.2: Individual accountability for privileged activity"
        ],
        "SOC 2": [
            "CC6.3: Access granted based on authorized roles",
            "CC6.6: Logical access restrictions for third parties"
        ],
        "HIPAA": [
            "45 CFR §164.308(a)(3): Workforce access management",
            "45 CFR §164.308(b): Business associate access provisions"
        ],
        "COSO": [
            "CC Principle 10: Control activities — segregation and least privilege",
            "CC Principle 16: Third-party control evaluation"
        ],
        "COBIT": [
            "APO10.04: Manage vendor risk and third-party access",
            "DSS05.04: Manage user identity and logical access"
        ],
        "DORA": [
            "Art. 28: ICT third-party risk management — contractor oversight",
            "Art. 9: Privileged access controls for external parties"
        ]
    },
    "Dormant account — no login in 90+ days": {
        "NIST 800-53": [
            "AC-2(3): Automated disabling of inactive accounts",
            "AC-2(4): Automated audit of account management actions"
        ],
        "PCI-DSS": [
            "Req 8.2.6: Disable inactive accounts within 90 days"
        ],
        "SOC 2": [
            "CC6.2: Access removed or modified when no longer necessary",
            "CC6.3: Periodic review and recertification of user access"
        ],
        "HIPAA": [
            "45 CFR §164.308(a)(5)(ii)(C): Login monitoring",
            "45 CFR §164.312(a)(2)(i): Unique user identification"
        ],
        "COSO": [
            "CC Principle 10: Ongoing control activities over access review"
        ],
        "COBIT": [
            "DSS05.04: Periodic review of access rights and dormancy",
            "MEA01.03: Monitor control effectiveness"
        ],
        "DORA": [
            "Art. 9: Access rights reviewed at regular intervals"
        ]
    },
    "Privileged user with no manager assigned": {
        "NIST 800-53": [
            "AC-2: Account Management — defined approvers for privileged accounts",
            "AC-5: Separation of Duties — no single point of control",
            "AC-6: Least Privilege — oversight required for elevated access"
        ],
        "PCI-DSS": [
            "Req 7.2.2: Access approval by authorized personnel",
            "Req 8.2.2: Individual accountability maintained"
        ],
        "SOC 2": [
            "CC6.3: Access approved by authorized roles",
            "CC5.2: Management defines accountability for privileged access"
        ],
        "HIPAA": [
            "45 CFR §164.308(a)(2): Assigned security responsibility",
            "45 CFR §164.308(a)(3): Workforce access management and oversight"
        ],
        "COSO": [
            "CC Principle 3: Management establishes structures and reporting lines",
            "CC Principle 10: Accountability in control activities"
        ],
        "COBIT": [
            "APO01.02: Organizational structure — defined accountability",
            "DSS06.03: Roles, responsibilities, and access privileges"
        ],
        "DORA": [
            "Art. 5: ICT governance — clear roles and accountability for access"
        ]
    }
}

def map_finding_to_frameworks(finding_text: str) -> dict:
    """Return control mappings for a given finding description."""
    for key in FRAMEWORK_CONTROLS:
        if key.lower() in finding_text.lower():
            return FRAMEWORK_CONTROLS[key]
    return {}

MAX_TABLE_ROWS = 50

def generate_control_mapping_table(findings) -> str:
    """Generate a markdown table of findings mapped to framework controls.
    Capped at MAX_TABLE_ROWS highest-severity rows for UI performance at scale."""
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    df = findings.copy()
    df["_sev_rank"] = df["severity"].map(severity_order).fillna(4)
    df = df.sort_values("_sev_rank")

    total = len(df)
    display_df = df.head(MAX_TABLE_ROWS)

    lines = []
    lines.append("## Compliance Framework Control Mapping\n")
    if total > MAX_TABLE_ROWS:
        lines.append(f"*Showing the {MAX_TABLE_ROWS} highest-severity findings of {total:,} total. "
                     f"Full mapping available in the exported audit report.*\n")
    lines.append("| Finding | User | Severity | NIST 800-53 | PCI-DSS | SOC 2 | HIPAA | COSO | COBIT | DORA |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for _, row in display_df.iterrows():
        controls = map_finding_to_frameworks(row['risk_finding'])

        def first_control(framework):
            items = controls.get(framework, ["—"])
            return items[0].split(":")[0] if items and items[0] != "—" else "—"

        lines.append(
            f"| {row['risk_finding'][:40]} "
            f"| {row['username']} "
            f"| {row['severity']} "
            f"| {first_control('NIST 800-53')} "
            f"| {first_control('PCI-DSS')} "
            f"| {first_control('SOC 2')} "
            f"| {first_control('HIPAA')} "
            f"| {first_control('COSO')} "
            f"| {first_control('COBIT')} "
            f"| {first_control('DORA')} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from risk_engine import run_all_checks

    findings = run_all_checks("data/users.csv")
    table = generate_control_mapping_table(findings)
    print(table)