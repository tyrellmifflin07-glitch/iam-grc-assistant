# add_assessment_depth.py
# Purpose: Enhance the Risk Intake & Workflow tab's AI initial assessment with:
#   - Risk Appetite status (Within / Requires Review / Outside Appetite)
#   - AI Recommendation (Approve / Approve with Conditions / Escalate / Reject)
#   - Business Impact categories (Operational, Financial, Regulatory, Reputational, Customer)
#   - AI Explainability ("Why?" factors + confidence score)
#   - A small Roadmap note for future enhancements (talking point, not built)
#
# Run from inside the iam_grc_assistant folder:  python3 add_assessment_depth.py

import os
import re
import sys
import py_compile

FILE = "src/dashboard.py"

if not os.path.exists(FILE):
    print("[!] src/dashboard.py not found. Run this from inside iam_grc_assistant.")
    sys.exit(1)

with open(FILE, "r") as f:
    original_content = f.read()

if "Risk Appetite" in original_content and "AI Recommendation" in original_content:
    print("[=] Assessment depth features already present. No changes made.")
    sys.exit(0)

content = original_content

# ── STEP A: Replace the severity_map assessment block with an enriched version ──
old_block = '''            severity_map = {
                "New AI Tool": ("High", "AI Risk"),
                "New Cloud Application": ("Medium", "Technology Risk"),
                "New Vendor / Third Party": ("High", "Third-Party Risk"),
                "New System / Platform": ("Medium", "Technology Risk"),
                "Existing System - Material Change": ("Medium", "Technology Risk"),
            }
            init_severity, init_taxonomy = severity_map.get(intake_type, ("Medium", "Technology Risk"))
            if any(d in intake_data for d in ["Customer PII", "Financial Data", "PHI", "Credentials / Secrets"]):
                init_severity = "Critical" if init_severity == "High" else "High"

            submission_id = f"INT-{len(st.session_state.intake_submissions) + 1:03d}"
            st.session_state.intake_submissions.append({
                "ID": submission_id,
                "Name": intake_name,
                "Business Unit": intake_business_unit or "Not specified",
                "Type": intake_type,
                "Data": ", ".join(intake_data) if intake_data else "None specified",
                "Taxonomy": init_taxonomy,
                "Initial Risk Rating": init_severity,
                "Status": "Assessed - Tasks Generated"
            })'''

new_block = '''            severity_map = {
                "New AI Tool": ("High", "AI Risk"),
                "New Cloud Application": ("Medium", "Technology Risk"),
                "New Vendor / Third Party": ("High", "Third-Party Risk"),
                "New System / Platform": ("Medium", "Technology Risk"),
                "Existing System - Material Change": ("Medium", "Technology Risk"),
            }
            init_severity, init_taxonomy = severity_map.get(intake_type, ("Medium", "Technology Risk"))

            # ── Explainability: track which factors drove the rating ──
            explain_factors = [f"Submission type: {intake_type}"]
            sensitive_hit = any(d in intake_data for d in ["Customer PII", "Financial Data", "PHI", "Credentials / Secrets"])
            if sensitive_hit:
                init_severity = "Critical" if init_severity == "High" else "High"
                explain_factors.append("Sensitive data involved: " + ", ".join(
                    [d for d in intake_data if d in ["Customer PII", "Financial Data", "PHI", "Credentials / Secrets"]]
                ))
            if intake_type == "New Vendor / Third Party":
                explain_factors.append("Third-party vendor — no prior assessment on file")
            if intake_type == "New AI Tool":
                explain_factors.append("AI system — bias and explainability review required")
            if not intake_data or intake_data == ["Public Data Only"]:
                explain_factors.append("Limited or public-only data reduces exposure")

            confidence = 94 if sensitive_hit else 87 if intake_type in ("New AI Tool", "New Vendor / Third Party") else 78

            # ── Risk Appetite determination ──
            appetite_thresholds = {"Critical": "🔴 Outside Appetite", "High": "🟡 Requires Review",
                                    "Medium": "🟢 Within Appetite", "Low": "🟢 Within Appetite"}
            risk_appetite = appetite_thresholds.get(init_severity, "🟡 Requires Review")

            # ── AI Recommendation ──
            if init_severity == "Critical":
                recommendation = "Escalate"
            elif init_severity == "High":
                recommendation = "Approve with Conditions"
            else:
                recommendation = "Approve"

            # ── Business Impact — inferred from data types and submission type ──
            business_impact = []
            if "Customer PII" in intake_data or "PHI" in intake_data:
                business_impact.append("Customer")
                business_impact.append("Regulatory")
            if "Financial Data" in intake_data:
                business_impact.append("Financial")
            if intake_type == "New Vendor / Third Party":
                business_impact.append("Operational")
            if init_severity in ("Critical", "High"):
                business_impact.append("Reputational")
            if not business_impact:
                business_impact.append("Operational")
            business_impact = sorted(set(business_impact))

            submission_id = f"INT-{len(st.session_state.intake_submissions) + 1:03d}"
            st.session_state.intake_submissions.append({
                "ID": submission_id,
                "Name": intake_name,
                "Business Unit": intake_business_unit or "Not specified",
                "Type": intake_type,
                "Data": ", ".join(intake_data) if intake_data else "None specified",
                "Taxonomy": init_taxonomy,
                "Initial Risk Rating": init_severity,
                "Risk Appetite": risk_appetite,
                "AI Recommendation": recommendation,
                "Business Impact": ", ".join(business_impact),
                "Explainability": explain_factors,
                "Confidence": confidence,
                "Status": "Assessed - Tasks Generated"
            })'''

if old_block not in content:
    print("[!] Could not find the expected assessment block — aborting, no changes made.")
    sys.exit(1)

content = content.replace(old_block, new_block)

# ── STEP B: Replace the simple submissions table with an enriched executive-style display ──
old_display = '''    if st.session_state.intake_submissions:
        st.markdown("---")
        st.subheader("🧠 Step 2 — AI Initial Assessments")
        st.dataframe(pd.DataFrame(st.session_state.intake_submissions), use_container_width=True, hide_index=True)'''

new_display = '''    if st.session_state.intake_submissions:
        st.markdown("---")
        st.subheader("🧠 Step 2 — AI Initial Assessments")

        for sub in st.session_state.intake_submissions:
            with st.container():
                st.markdown(f"**{sub['ID']} — {sub['Name']}** ({sub['Business Unit']})")
                rcol1, rcol2, rcol3, rcol4 = st.columns(4)
                rcol1.metric("Overall Risk", sub["Initial Risk Rating"])
                rcol2.metric("Risk Appetite", sub["Risk Appetite"])
                rcol3.metric("AI Recommendation", sub["AI Recommendation"])
                rcol4.metric("Confidence", f"{sub['Confidence']}%")

                st.markdown(f"**Business Impact:** {sub['Business Impact']}  |  **Taxonomy:** {sub['Taxonomy']}")

                if sub["Risk Appetite"] == "🔴 Outside Appetite":
                    st.error(f"Overall Risk: {sub['Initial Risk Rating']}  |  Risk Appetite: Outside Appetite  |  Executive approval required before implementation.")
                elif sub["Risk Appetite"] == "🟡 Requires Review":
                    st.warning(f"Overall Risk: {sub['Initial Risk Rating']}  |  Risk Appetite: Requires Review  |  Second-line review recommended before proceeding.")
                else:
                    st.success(f"Overall Risk: {sub['Initial Risk Rating']}  |  Risk Appetite: Within Appetite  |  Standard remediation tracking applies.")

                with st.expander(f"🔍 Why this rating? (AI Explainability — {sub['Confidence']}% confidence)"):
                    for factor in sub["Explainability"]:
                        st.markdown(f"- {factor}")

                st.markdown("---")'''

if old_display not in content:
    print("[!] Could not find the expected display block — aborting, no changes made.")
    sys.exit(1)

content = content.replace(old_display, new_display)

# ── STEP C: Add a Roadmap expander at the end of the tab (talking point, not built) ──
roadmap_addition = '''

    st.markdown("---")
    with st.expander("🗺️ Roadmap — Planned Enhancements"):
        st.markdown("""
        This intake and workflow module is designed to extend into a full
        enterprise GRC platform. Planned next-phase enhancements:

        **Governance Depth**
        - Formal second-line reviewer approval step (reviewer, date, approve/reject, comments)
        - Risk exception / risk acceptance workflow with business owner sign-off and expiration tracking
        - Evidence repository per finding (SOC 2 reports, pen test results, architecture diagrams, policy exceptions)

        **Executive Reporting**
        - Dedicated one-page Executive Dashboard — assessment volume, residual risk trend, overdue tasks, average completion time
        - One-click generation of Executive Summary, Risk Register, Board Report, Remediation Plan, CAB Submission, and Risk Acceptance Form from a single assessment

        **Integrations**
        - ServiceNow / Archer for enterprise GRC record-keeping
        - Jira / Azure DevOps for engineering remediation tracking
        - Power BI for executive dashboards
        - Entra ID and CyberArk for live privileged access and identity data
        - Continuous monitoring feeds in place of point-in-time assessment

        These are intentionally sequenced as roadmap items rather than built
        tonight — a mature GRC platform is prioritized and phased, not built
        all at once.
        """)
'''

# Insert the roadmap AFTER the entire if/else block (after the else body),
# not between the if-body and its else clause.
final_marker = '''    else:
        st.info("Submit a technology risk intake above to begin the assessment and remediation workflow.")'''

if final_marker not in content:
    print("[!] Could not find the tab's closing marker — aborting, no changes made.")
    sys.exit(1)

content = content.replace(final_marker, final_marker + "\n" + roadmap_addition)

# ── Backup, write, validate ──
with open(FILE + ".backup", "w") as f:
    f.write(original_content)

with open(FILE, "w") as f:
    f.write(content)

try:
    py_compile.compile(FILE, doraise=True)
    print("===== ASSESSMENT DEPTH FEATURES ADDED =====")
    print("  [+] Risk Appetite status (Within / Requires Review / Outside Appetite)")
    print("  [+] AI Recommendation (Approve / Approve with Conditions / Escalate)")
    print("  [+] Business Impact categories (Operational, Financial, Regulatory, Reputational, Customer)")
    print("  [+] AI Explainability - Why? factors + confidence score")
    print("  [+] Roadmap expander added (talking point for future enhancements)")
    print("  [+] Syntax check: PASSED")
    print("  [+] Backup saved: " + FILE + ".backup")
    print("")
    print("Next: streamlit run src/dashboard.py")
except py_compile.PyCompileError as err:
    with open(FILE + ".backup") as f:
        restore = f.read()
    with open(FILE, "w") as f:
        f.write(restore)
    print("[!] Syntax check FAILED — original file restored automatically.")
    print(err)
    sys.exit(1)