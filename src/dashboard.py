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

tab_iam, tab_ai = st.tabs(["🪪 IAM Risk Assessment", "🤖 AI Adoption Risk Advisor"])

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