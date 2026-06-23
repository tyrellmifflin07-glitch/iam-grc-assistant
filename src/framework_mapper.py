# src/framework_mapper.py
# Purpose: Map IAM risk findings to specific compliance framework controls

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
        ]
    }
}

def map_finding_to_frameworks(finding_text: str) -> dict:
    """Return control mappings for a given finding description."""
    for key in FRAMEWORK_CONTROLS:
        if key.lower() in finding_text.lower():
            return FRAMEWORK_CONTROLS[key]
    return {}

def generate_control_mapping_table(findings) -> str:
    """Generate a markdown table of findings mapped to framework controls."""
    lines = []
    lines.append("## Compliance Framework Control Mapping\n")
    lines.append("| Finding | User | Severity | NIST 800-53 | PCI-DSS | SOC 2 | HIPAA |")
    lines.append("|---|---|---|---|---|---|---|")

    for _, row in findings.iterrows():
        controls = map_finding_to_frameworks(row['risk_finding'])

        nist = controls.get("NIST 800-53", ["—"])[0].split(":")[0]
        pci = controls.get("PCI-DSS", ["—"])[0].split(":")[0]
        soc2 = controls.get("SOC 2", ["—"])[0].split(":")[0]
        hipaa = controls.get("HIPAA", ["—"])[0].split(":")[0]

        lines.append(
            f"| {row['risk_finding'][:40]} "
            f"| {row['username']} "
            f"| {row['severity']} "
            f"| {nist} "
            f"| {pci} "
            f"| {soc2} "
            f"| {hipaa} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from risk_engine import run_all_checks

    findings = run_all_checks("data/users.csv")
    table = generate_control_mapping_table(findings)
    print(table)