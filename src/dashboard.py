# src/dashboard.py
# Purpose: Streamlit web interface for the AI IAM/GRC Assistant

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

sys.path.append("src")

st.set_page_config(
    page_title="MiffTech · AI IAM/GRC Assistant",
    page_icon="🔐",
    layout="wide"
)

# API key check on startup
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    st.error("""
    ⚠️ ANTHROPIC_API_KEY not found.

    Please create a .env file in your project root with the following:

    ANTHROPIC_API_KEY=sk-ant-your-key-here

    Then restart the dashboard.
    """)
    st.stop()

from risk_engine import run_all_checks
from executive_summary import generate_executive_summary
from ai_narrator import generate_audit_narrative
from pdf_generator import markdown_to_pdf
from framework_mapper import generate_control_mapping_table
from risk_taxonomy import add_taxonomy_columns, taxonomy_summary
from ai_risk_advisor import generate_ai_risk_assessment
from vendor_doc_assessment import extract_text_from_pdf, generate_structured_assessment
from report_generator import build_report

required_columns = [
    "user_id",
    "username",
    "department",
    "role",
    "access_level",
    "last_login",
    "account_status",
    "manager",
]

# ── MIFFTECH BRANDING ──
import os as _os
_logo_path = "assets/logo.png"

st.markdown("""
<style>
    /* MiffTech brand styling */
    .mifftech-header {
        background-color: #2B2F33;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        border-bottom: 3px solid #E8B830;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    h1, h2, h3 {
        color: #1B3A5C;
    }
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #3D8BD4;
    }
    .stTabs [aria-selected="true"] {
        color: #3D8BD4 !important;
        font-weight: 700;
    }
    [data-testid="stMetricValue"] {
        color: #3D8BD4;
    }
    .mifftech-footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 2px solid #E8B830;
        color: #666;
        font-size: 0.85rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

_hcol1, _hcol2 = st.columns([1, 5])
with _hcol1:
    if _os.path.exists(_logo_path):
        st.image(_logo_path, width=220)
with _hcol2:
    st.title("AI IAM/GRC Assistant")
    st.markdown("**Identity Governance Risk Assessment & AI Adoption Risk Advisory**")
    st.caption("MiffTech Risk AI & Consulting · Second-Line Risk Intelligence Platform")

tab_iam, tab_ai, tab_gov, tab_aigov, tab_intake, tab_docs = st.tabs(["🪪 IAM Risk Assessment", "🤖 AI Adoption Risk Advisor", "🏛️ Risk Governance", "🧠 AI Governance", "📥 Risk Intake & Workflow", "📄 Vendor Document Assessment"])

with tab_iam:
    st.write(
        "Upload IAM user access data to detect risks, classify findings across "
        "enterprise risk taxonomies, map to seven compliance frameworks, and "
        "generate audit-ready Markdown and PDF reports."
    )

    uploaded_file = st.file_uploader("Upload IAM CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Data Preview")
        st.dataframe(df)

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error("Invalid CSV format. This file does not match the IAM access review template.")
            st.write("### Missing Required Columns")
            st.write(missing_columns)
            st.write("### Required CSV Columns")
            st.write(required_columns)
            st.info("Please upload an IAM access review CSV, not a property, customer, finance, or unrelated dataset.")
            st.stop()

        st.success("CSV format validated successfully.")

        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

        df.to_csv("data/uploaded_users.csv", index=False)

        if st.button("Run IAM Risk Assessment"):
            with st.spinner("Running risk engine..."):
                findings = run_all_checks("data/uploaded_users.csv")

            st.subheader("Risk Findings")
            findings = add_taxonomy_columns(findings)
            st.dataframe(findings)

            st.subheader("Enterprise Risk Taxonomy Summary")
            st.markdown(
                "Findings classified across **Cyber, Technology, Data, AI, and "
                "Third-Party** risk categories — aligned to enterprise risk "
                "management (ERM) taxonomy structures:"
            )
            st.dataframe(taxonomy_summary(findings))

            st.subheader("Compliance Framework Mapping")
            st.markdown(
                "Each finding mapped across **NIST 800-53, PCI-DSS, SOC 2, HIPAA, "
                "COSO, COBIT, and DORA**:"
            )
            control_table = generate_control_mapping_table(findings)
            st.markdown(control_table)

            with st.spinner("Generating executive summary..."):
                executive_summary = generate_executive_summary(findings)

            st.subheader("Executive Summary")
            st.markdown(executive_summary)

            with st.spinner("Generating AI audit report..."):
                audit_report = generate_audit_narrative(findings)

            st.subheader("Audit Report")
            st.markdown(audit_report)

            executive_md_path = "reports/executive_summary.md"
            audit_md_path = "reports/audit_report.md"
            executive_pdf_path = "reports/executive_summary.pdf"
            audit_pdf_path = "reports/audit_report.pdf"

            with open(executive_md_path, "w") as f:
                f.write(executive_summary)

            with open(audit_md_path, "w") as f:
                f.write(audit_report)

            with st.spinner("Generating PDF reports..."):
                markdown_to_pdf(executive_md_path, executive_pdf_path)
                markdown_to_pdf(audit_md_path, audit_pdf_path)

            st.success("Assessment complete. Markdown and PDF reports are ready.")

            st.download_button(
                label="Download Executive Summary Markdown",
                data=executive_summary,
                file_name="executive_summary.md",
                mime="text/markdown"
            )

            st.download_button(
                label="Download Audit Report Markdown",
                data=audit_report,
                file_name="audit_report.md",
                mime="text/markdown"
            )

            with open(executive_pdf_path, "rb") as f:
                executive_pdf = f.read()

            with open(audit_pdf_path, "rb") as f:
                audit_pdf = f.read()

            st.download_button(
                label="Download Executive Summary PDF",
                data=executive_pdf,
                file_name="executive_summary.pdf",
                mime="application/pdf"
            )

            st.download_button(
                label="Download Audit Report PDF",
                data=audit_pdf,
                file_name="audit_report.pdf",
                mime="application/pdf"
            )


with tab_ai:
    st.write(
        "Second-line risk advisory for proposed AI adoptions. Describe the AI use "
        "case and receive a structured risk assessment across AI, Data, Cyber, "
        "Technology, and Third-Party risk taxonomies — with recommended controls "
        "and framework mappings."
    )

    st.markdown("---")

    ai_use_case = st.text_area(
        "Describe the proposed AI use case",
        placeholder="Example: Deploy an AI chatbot for customer service that can access customer account balances and transaction history to answer questions",
        height=120
    )

    col1, col2 = st.columns(2)

    with col1:
        ai_business_unit = st.text_input(
            "Business unit proposing the adoption",
            placeholder="e.g., Retail Banking Operations"
        )
        ai_deployment = st.selectbox(
            "Deployment model",
            [
                "Third-party SaaS (cloud-hosted)",
                "Cloud-hosted — own tenant (AWS/Azure/GCP)",
                "On-premises / self-hosted",
                "Embedded in existing vendor product",
                "API integration into internal application"
            ]
        )

    with col2:
        ai_data_types = st.multiselect(
            "Data types the AI will access or process",
            [
                "Customer PII",
                "Financial account data",
                "Transaction history",
                "Employee data",
                "Protected health information (PHI)",
                "Legal / privileged documents",
                "Internal policies and procedures",
                "Public data only",
                "Source code",
                "Authentication credentials or secrets"
            ]
        )
        ai_vendor = st.radio(
            "Is a third-party vendor involved?",
            ["Yes", "No"],
            horizontal=True
        )

    if st.button("Generate AI Risk Assessment"):
        if not ai_use_case.strip():
            st.warning("Please describe the AI use case before generating an assessment.")
        else:
            with st.spinner("Performing second-line AI risk assessment..."):
                ai_assessment = generate_ai_risk_assessment(
                    use_case=ai_use_case,
                    data_types=ai_data_types,
                    deployment_model=ai_deployment,
                    vendor_involved=ai_vendor,
                    business_unit=ai_business_unit if ai_business_unit.strip() else "Not specified"
                )

            st.markdown(ai_assessment)

            os.makedirs("reports", exist_ok=True)
            ai_report_path = "reports/ai_risk_assessment.md"
            with open(ai_report_path, "w") as f:
                f.write(ai_assessment)

            st.success("AI risk assessment complete.")

            st.download_button(
                label="Download AI Risk Assessment (Markdown)",
                data=ai_assessment,
                file_name="ai_risk_assessment.md",
                mime="text/markdown"
            )


with tab_gov:
    st.write(
        "Second-line risk governance views — the Three Lines of Defense model "
        "and the enterprise Risk Appetite dashboard used for ongoing assessment "
        "and recalibration of risk posture."
    )

    st.markdown("---")
    st.subheader("🏛️ Three Lines of Defense")
    st.markdown(
        "Risk management responsibility distributed across three organizational "
        "lines, each with distinct ownership and accountability:"
    )

    lod1, lod2, lod3 = st.columns(3)

    with lod1:
        st.markdown("### 1️⃣ First Line")
        st.markdown("**Own & Manage Risk**")
        st.markdown("""
        Business units and technology teams that own risks and controls in
        their day-to-day operations.

        **Functions:**
        - Business unit management
        - IT operations & engineering
        - Application owners
        - Control execution & self-testing

        **In this platform:**
        - Runs IAM access reviews
        - Remediates flagged accounts
        - Executes control activities
        """)

    with lod2:
        st.markdown("### 2️⃣ Second Line")
        st.markdown("**Oversee & Challenge**")
        st.markdown("""
        Independent risk and compliance functions that set frameworks,
        monitor risk posture, and challenge the first line.

        **Functions:**
        - Enterprise risk management
        - Information security risk oversight
        - Compliance & policy governance
        - Risk appetite monitoring

        **In this platform:**
        - Risk taxonomy classification
        - AI adoption risk advisory
        - Framework mapping & appetite tracking
        """)

    with lod3:
        st.markdown("### 3️⃣ Third Line")
        st.markdown("**Independent Assurance**")
        st.markdown("""
        Internal audit providing independent, objective assurance to the
        board and audit committee.

        **Functions:**
        - Internal audit
        - Independent control testing
        - Board & audit committee reporting
        - Assurance over 1st and 2nd lines

        **In this platform:**
        - Audit-ready report exports
        - Evidence trails & finding detail
        - Executive & board-level narratives
        """)

    st.markdown("---")
    st.subheader("📊 Enterprise Risk Appetite Dashboard")
    st.markdown(
        "Current risk posture against board-approved appetite thresholds by "
        "risk taxonomy. Supports ongoing assessment and recalibration of the "
        "global risk appetite across business units."
    )

    appetite_data = {
        "Risk Category": [
            "Cyber Risk",
            "Technology Risk",
            "Data Risk",
            "AI Risk",
            "Third-Party / Vendor Risk",
            "Operational Resilience"
        ],
        "Appetite Status": [
            "🟢 Within Appetite",
            "🟡 Near Threshold",
            "🟢 Within Appetite",
            "🔴 Above Appetite",
            "🟢 Within Appetite",
            "🟡 Near Threshold"
        ],
        "Current Exposure": ["Moderate", "Elevated", "Moderate", "High", "Moderate", "Elevated"],
        "Trend": ["→ Stable", "↑ Increasing", "→ Stable", "↑ Increasing", "↓ Decreasing", "→ Stable"],
        "Key Driver": [
            "Access controls maturing; terminated-user remediation on track",
            "Dormant account volume approaching tolerance threshold",
            "Data classification program operating effectively",
            "Ungoverned AI adoption ahead of control framework maturity",
            "Vendor review cycle current; contractor access controls improving",
            "CloudTrail regional gap under remediation"
        ]
    }
    df_appetite = pd.DataFrame(appetite_data)
    st.dataframe(df_appetite, use_container_width=True, hide_index=True)

    acol1, acol2, acol3 = st.columns(3)
    acol1.metric("Within Appetite", "3", delta="categories")
    acol2.metric("Near Threshold", "2", delta="monitor closely", delta_color="off")
    acol3.metric("Above Appetite", "1", delta="action required", delta_color="inverse")

    st.markdown("#### Recalibration Notes")
    st.markdown("""
    - **AI Risk** exceeds current appetite — driven by business-unit AI adoption
      outpacing governance controls. Recommended action: mandatory AI adoption
      risk assessments (see AI Adoption Risk Advisor tab) before deployment
      approval, and establishment of an AI governance registry.
    - **Technology Risk** approaching threshold — dormant account population
      requires automated lifecycle controls to prevent breach of tolerance.
    - Appetite statements reviewed quarterly with the Risk Committee; thresholds
      recalibrated annually or upon material change in business profile.
    """)

with tab_aigov:
    st.write(
        "AI Governance registry — inventory of AI models and use cases in the "
        "organization with ownership, risk ratings, and required control gates. "
        "Supports responsible AI adoption oversight across business units."
    )

    st.markdown("---")
    st.subheader("🧠 AI Model & Use Case Registry")

    aigov_data = {
        "Model / Use Case": [
            "Customer Service Chatbot",
            "Transaction Fraud Scoring",
            "Document Summarization (Legal)",
            "IAM Risk Analysis Engine",
            "Marketing Content Generator",
            "Credit Decision Support"
        ],
        "Business Owner": [
            "Retail Banking Ops",
            "Fraud Operations",
            "Legal Department",
            "Information Security",
            "Marketing",
            "Credit Risk"
        ],
        "Risk Rating": ["High", "High", "Medium", "Medium", "Low", "Critical"],
        "Human Review Required": ["Yes", "Yes", "Yes", "Yes", "No", "Yes — Mandatory"],
        "Bias Assessment": ["✅ Complete", "✅ Complete", "🔄 In Progress", "✅ Complete", "➖ N/A", "🔄 In Progress"],
        "Privacy Review": ["✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete", "✅ Complete", "🔄 In Progress"],
        "Status": ["🟢 Approved", "🟢 Approved", "🟡 Conditional", "🟢 Approved", "🟢 Approved", "🔴 Pending Review"]
    }
    df_aigov = pd.DataFrame(aigov_data)
    st.dataframe(df_aigov, use_container_width=True, hide_index=True)

    gcol1, gcol2, gcol3, gcol4 = st.columns(4)
    gcol1.metric("Registered Models", "6")
    gcol2.metric("Approved", "4")
    gcol3.metric("Conditional", "1")
    gcol4.metric("Pending Review", "1")

    st.markdown("---")
    st.subheader("AI Governance Control Gates")
    st.markdown("""
    Every AI adoption must clear the following gates before production approval:

    | Gate | Owner | Requirement |
    |---|---|---|
    | Use Case Risk Assessment | Second Line (this platform — AI Risk Advisor tab) | Structured risk assessment across all taxonomies |
    | Data Privacy Review | Privacy Office | PII/PHI handling, retention, and residency validated |
    | Bias & Fairness Assessment | Model Owner + Second Line | Demographic performance parity documented |
    | Human-in-the-Loop Design | Business Owner | Human review requirements defined for consequential decisions |
    | Vendor & Subprocessor Review | Third-Party Risk | Training-data prohibitions and audit rights contracted |
    | Ongoing Monitoring Plan | First Line | Model drift, output quality, and incident escalation defined |

    **Framework alignment:** NIST AI Risk Management Framework (AI RMF) ·
    DORA Art. 28 (third-party AI services) · GDPR Art. 22 (automated
    decision-making) · Model Risk Management guidance (SR 11-7 principles)
    """)


# ── MIFFTECH FOOTER ──
st.markdown("""
<div class="mifftech-footer">
    <strong>MiffTech Risk AI & Consulting</strong> · Tyrell Mifflin, CEH · CSM · CCSP (Expected 2026)<br>
    IAM Governance · GRC Engineering · AI Risk Advisory · New Castle, DE<br>
    <a href="https://iam-grc-assistant.streamlit.app">Live Platform</a> ·
    <a href="https://github.com/tyrellmifflin07-glitch">GitHub</a> ·
    <a href="https://linkedin.com/in/tyrell-mifflin-ceh-csm-85a27583">LinkedIn</a>
</div>
""", unsafe_allow_html=True)

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

                st.markdown("---")

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



with tab_docs:
    st.write(
        "Upload vendor or technology documentation — SOC reports, penetration "
        "test results, security architecture diagrams, SBOMs, incident response "
        "plans, encryption standards — and receive a second-line risk assessment "
        "grounded in what the documents actually contain, with explicit callouts "
        "of what evidence is missing."
    )

    st.markdown("---")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        vendor_name = st.text_input("Vendor / Technology Name", placeholder="e.g., ClearPath Platform")
    with dcol2:
        vendor_business_unit = st.text_input("Requesting Business Unit", placeholder="e.g., IT Operations")

    uploaded_docs = st.file_uploader(
        "Upload vendor documents (PDF)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_docs:
        st.markdown(f"**{len(uploaded_docs)} document(s) uploaded:**")
        for doc in uploaded_docs:
            st.markdown(f"- {doc.name}")

        if st.button("Generate Vendor Risk Assessment"):
            if not vendor_name.strip():
                st.warning("Please provide a vendor or technology name before generating the assessment.")
            else:
                with st.spinner(f"Extracting text from {len(uploaded_docs)} document(s)..."):
                    documents = {}
                    for doc in uploaded_docs:
                        file_bytes = doc.read()
                        extracted = extract_text_from_pdf(file_bytes, doc.name)
                        documents[doc.name] = extracted

                with st.expander("📄 Extracted Document Preview (first 300 characters per file)"):
                    for name, text in documents.items():
                        st.markdown(f"**{name}**")
                        st.text(text[:300] + ("..." if len(text) > 300 else ""))
                        st.markdown("---")

                with st.spinner("Performing second-line cross-document risk assessment..."):
                    try:
                        assessment = generate_structured_assessment(
                            vendor_name=vendor_name,
                            business_unit=vendor_business_unit if vendor_business_unit.strip() else "Not specified",
                            documents=documents
                        )
                    except ValueError as e:
                        st.error(f"Assessment generation failed: {e}")
                        assessment = None

                if assessment:
                    st.subheader(assessment.get("title", vendor_name))
                    st.caption(assessment.get("subtitle", ""))

                    st.markdown("### Executive Summary")
                    for para in assessment.get("exec_summary", "").split("\n\n"):
                        if para.strip():
                            st.write(para.strip())

                    if assessment.get("bottom_line"):
                        st.info(f"**Bottom line:** {assessment['bottom_line']}")

                    findings = assessment.get("findings", [])
                    if findings:
                        st.markdown("### Findings at a Glance")
                        glance_rows = [
                            {"ID": f.get("id", ""), "Finding": f.get("title", ""), "Severity": f.get("severity", "")}
                            for f in findings
                        ]
                        st.dataframe(pd.DataFrame(glance_rows), use_container_width=True, hide_index=True)

                        st.markdown("### Detailed Findings")
                        for f in findings:
                            sev = f.get("severity", "Medium")
                            sev_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(sev, "⚪")
                            with st.expander(f"{sev_icon} {f.get('id', '')} — {f.get('title', '')} — {sev}"):
                                if f.get("observation"):
                                    st.markdown(f"**Observation:** {f['observation']}")
                                if f.get("assessment"):
                                    st.markdown(f"**Assessment:** {f['assessment']}")
                                if f.get("traceability"):
                                    st.markdown("**Traceability:**")
                                    for t in f["traceability"]:
                                        st.markdown(f"- {t}")
                                if f.get("position"):
                                    st.warning(f"**Position:** {f['position']}")

                    if assessment.get("root_cause"):
                        st.markdown("### Root Cause")
                        for para in assessment["root_cause"].split("\n\n"):
                            if para.strip():
                                st.write(para.strip())

                    st.success("Cross-document risk assessment complete.")

                    docx_bytes = build_report(
                        title=assessment.get("title", vendor_name),
                        subtitle=assessment.get("subtitle", "Cross-Document Findings, Root Cause, and Remediation Plan"),
                        prepared_by="Tyrell Mifflin — MiffTech Risk AI & Consulting",
                        exec_summary=assessment.get("exec_summary", ""),
                        findings=findings,
                        root_cause=assessment.get("root_cause", ""),
                        bottom_line=assessment.get("bottom_line"),
                    )

                    st.download_button(
                        "📄 Download Full Report (Word)",
                        data=docx_bytes,
                        file_name=f"{vendor_name.replace(' ', '_')}_Risk_Assessment.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    import json as _json
                    st.download_button(
                        "Download Raw Findings (JSON)",
                        data=_json.dumps(assessment, indent=2),
                        file_name="vendor_assessment_data.json",
                        mime="application/json"
                    )

    else:
        st.info("Upload one or more vendor documents above to begin the assessment.")
