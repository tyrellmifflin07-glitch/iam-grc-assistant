# src/dashboard.py
# Purpose: Streamlit web interface for the AI IAM/GRC Assistant

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

sys.path.append("src")

st.set_page_config(
    page_title="AI IAM/GRC Assistant",
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

st.title("🔐 AI IAM/GRC Assistant")
st.subheader("Identity Governance Risk Assessment & AI Adoption Risk Advisory")

tab_iam, tab_ai, tab_gov, tab_aigov = st.tabs(["🪪 IAM Risk Assessment", "🤖 AI Adoption Risk Advisor", "🏛️ Risk Governance", "🧠 AI Governance"])

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