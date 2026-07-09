# add_risk_intake.py
# Purpose: Add a "Risk Intake & Workflow" tab to the AI IAM/GRC Assistant dashboard.
# Implements: Technology Risk Intake -> AI Initial Assessment -> Task Assignment ->
#             Workflow tracking -> Close Assessment / Executive Report.
#
# Run from inside the iam_grc_assistant folder:  python3 add_risk_intake.py

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

if "Risk Intake & Workflow" in original_content:
    print("[=] Risk Intake tab already present. No changes made.")
    sys.exit(0)

content = original_content

# ── Locate the tabs definition line (flexible whitespace) ──
tabs_pattern = re.compile(
    r'tab_iam,\s*tab_ai,\s*tab_gov,\s*tab_aigov\s*=\s*st\.tabs\(\['
    r'[^\]]*\]\)'
)

match = tabs_pattern.search(content)
if not match:
    print("[!] Could not find the expected tabs() definition line — aborting, no changes made.")
    print("[!] Looking for a line resembling: tab_iam, tab_ai, tab_gov, tab_aigov = st.tabs([...])")
    sys.exit(1)

new_tabs_line = (
    'tab_iam, tab_ai, tab_gov, tab_aigov, tab_intake = st.tabs(['
    '"🪪 IAM Risk Assessment", "🤖 AI Adoption Risk Advisor", '
    '"🏛️ Risk Governance", "🧠 AI Governance", "📥 Risk Intake & Workflow"])'
)

content = content[:match.start()] + new_tabs_line + content[match.end():]

intake_block = '''

with tab_intake:
    st.write(
        "End-to-end technology risk intake and remediation workflow. Submit a "
        "new technology, AI tool, cloud application, or vendor for assessment — "
        "the platform classifies risk, drafts an initial assessment, assigns "
        "remediation tasks to owners, and tracks the assessment through to closure."
    )

    st.markdown("---")
    st.subheader("📥 Step 1 — Technology Risk Intake")

    if "intake_submissions" not in st.session_state:
        st.session_state.intake_submissions = []
    if "intake_tasks" not in st.session_state:
        st.session_state.intake_tasks = []

    with st.form("intake_form"):
        ic1, ic2 = st.columns(2)
        with ic1:
            intake_name = st.text_input("Technology / Tool / Vendor Name", placeholder="e.g., Acme AI Chatbot Platform")
            intake_business_unit = st.text_input("Submitting Business Unit", placeholder="e.g., Retail Banking Operations")
        with ic2:
            intake_type = st.selectbox(
                "Submission Type",
                ["New AI Tool", "New Cloud Application", "New Vendor / Third Party", "New System / Platform", "Existing System - Material Change"]
            )
            intake_data = st.multiselect(
                "Data Sensitivity Involved",
                ["Customer PII", "Financial Data", "PHI", "Employee Data", "Public Data Only", "Credentials / Secrets"]
            )
        intake_description = st.text_area(
            "Brief Description",
            placeholder="What does this technology do, and why is the business unit requesting it?",
            height=80
        )
        submitted = st.form_submit_button("Submit for Risk Assessment")

    if submitted:
        if not intake_name.strip():
            st.warning("Please provide a technology or vendor name before submitting.")
        else:
            severity_map = {
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
            })

            task_templates = {
                "New AI Tool": [
                    ("AI Governance review and control gate sign-off required", "AI Risk Team", 21),
                    ("Bias and fairness assessment required", "Model Owner", 21),
                    ("Human-in-the-loop design review", intake_business_unit or "Business Owner", 14),
                ],
                "New Cloud Application": [
                    ("Encryption configuration not yet documented", "Cloud Engineering", 10),
                    ("MFA enforcement not confirmed", "IAM Team", 14),
                    ("Logging and monitoring integration required", "Security Operations", 14),
                ],
                "New Vendor / Third Party": [
                    ("Vendor SOC 2 report required", "Third-Party Risk", 7),
                    ("Data processing agreement review required", "Legal / Privacy Office", 14),
                    ("Subprocessor disclosure required", "Third-Party Risk", 10),
                ],
                "New System / Platform": [
                    ("Access control model not yet defined", "IAM Team", 14),
                    ("Logging and monitoring integration required", "Security Operations", 14),
                ],
                "Existing System - Material Change": [
                    ("Change impact assessment required", "Change Management", 10),
                    ("Access recertification required post-change", "IAM Team", 14),
                ],
            }
            import datetime
            for desc, owner, days in task_templates.get(intake_type, []):
                due = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.intake_tasks.append({
                    "Submission ID": submission_id,
                    "Finding": desc,
                    "Assigned To": owner,
                    "Due Date": due,
                    "Status": "Open"
                })

            st.success(f"Submission {submission_id} assessed. Risk rating: {init_severity} ({init_taxonomy}). Remediation tasks generated below.")

    if st.session_state.intake_submissions:
        st.markdown("---")
        st.subheader("🧠 Step 2 — AI Initial Assessments")
        st.dataframe(pd.DataFrame(st.session_state.intake_submissions), use_container_width=True, hide_index=True)

    if st.session_state.intake_tasks:
        st.markdown("---")
        st.subheader("✅ Step 3 — Remediation Tasks (Assigned)")
        st.caption("Edit Status directly in the table below to simulate workflow progress.")

        tasks_df = pd.DataFrame(st.session_state.intake_tasks)
        edited_tasks = st.data_editor(
            tasks_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Open", "In Progress", "Blocked", "Closed"],
                    required=True
                )
            },
            key="task_editor"
        )
        st.session_state.intake_tasks = edited_tasks.to_dict("records")

        st.markdown("---")
        st.subheader("📊 Step 4 — Workflow Status")
        wcol1, wcol2, wcol3, wcol4 = st.columns(4)
        status_counts = edited_tasks["Status"].value_counts()
        wcol1.metric("Open", int(status_counts.get("Open", 0)))
        wcol2.metric("In Progress", int(status_counts.get("In Progress", 0)))
        wcol3.metric("Blocked", int(status_counts.get("Blocked", 0)))
        wcol4.metric("Closed", int(status_counts.get("Closed", 0)))

        all_closed = (edited_tasks["Status"] == "Closed").all() and len(edited_tasks) > 0

        st.markdown("---")
        st.subheader("🔒 Step 5 — Close Assessment")
        if all_closed:
            st.success("All remediation tasks closed for current submissions. Assessment ready to close.")
        else:
            st.info("Assessment remains open until all remediation tasks are marked Closed.")

        if st.button("Generate Closure Report & Archive"):
            open_count = len(edited_tasks[edited_tasks["Status"] != "Closed"])
            closure_summary = f"""
## Technology Risk Intake — Closure Report

**Submissions Assessed:** {len(st.session_state.intake_submissions)}
**Total Remediation Tasks:** {len(edited_tasks)}
**Tasks Remaining Open:** {open_count}
**Overall Status:** {"CLOSED - All tasks complete" if open_count == 0 else "OPEN - Remediation in progress"}

This report certifies that all submitted technology, vendor, and AI adoption
requests have been classified, assessed against enterprise risk taxonomy,
assigned to accountable owners, and tracked through remediation. Audit
evidence is retained in the task assignment log above.
"""
            st.markdown(closure_summary)
            os.makedirs("reports", exist_ok=True)
            with open("reports/intake_closure_report.md", "w") as f:
                f.write(closure_summary)
            st.download_button(
                "Download Closure Report",
                data=closure_summary,
                file_name="intake_closure_report.md",
                mime="text/markdown"
            )
    else:
        st.info("Submit a technology risk intake above to begin the assessment and remediation workflow.")
'''

content = content + intake_block

with open(FILE + ".backup", "w") as f:
    f.write(original_content)

with open(FILE, "w") as f:
    f.write(content)

try:
    py_compile.compile(FILE, doraise=True)
    print("===== RISK INTAKE & WORKFLOW TAB ADDED =====")
    print("  [+] New tab: Risk Intake & Workflow")
    print("  [+] Technology Risk Intake form (name, business unit, type, data sensitivity)")
    print("  [+] AI initial assessment (taxonomy classification + risk rating)")
    print("  [+] Auto-generated remediation tasks with owner and due date")
    print("  [+] Live editable task status (Open/In Progress/Blocked/Closed)")
    print("  [+] Workflow status metrics")
    print("  [+] Closure report generation and download")
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