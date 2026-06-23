# src/dashboard.py
# Purpose: Streamlit web interface for the AI IAM/GRC Assistant

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

sys.path.append("src")

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

st.set_page_config(
    page_title="AI IAM/GRC Assistant",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AI IAM/GRC Assistant")
st.subheader("Identity Governance Risk Assessment & Audit Report Generator")

st.write(
    "Upload IAM user access data to detect risks, generate an executive summary, "
    "and create audit-ready Markdown and PDF reports."
)

uploaded_file = st.file_uploader("Upload IAM CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded IAM Data")
    st.dataframe(df)

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    df.to_csv("data/uploaded_users.csv", index=False)

    if st.button("Run IAM Risk Assessment"):
        with st.spinner("Running risk engine..."):
            findings = run_all_checks("data/uploaded_users.csv")

        st.subheader("Risk Findings")
        st.dataframe(findings)

        st.subheader("Compliance Framework Mapping")
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