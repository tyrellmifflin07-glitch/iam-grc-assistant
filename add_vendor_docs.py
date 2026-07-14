# add_vendor_docs.py
# Purpose: Add a "Vendor Document Risk Assessment" tab to the AI IAM/GRC Assistant.
# Accepts uploaded PDF documents (SOC reports, pen tests, architecture docs, etc.),
# extracts text, and generates a Claude-powered risk assessment grounded in the
# actual document content.
#
# Run from inside the iam_grc_assistant folder:  python3 add_vendor_docs.py

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

if "Vendor Document Risk Assessment" in original_content:
    print("[=] Vendor Document tab already present. No changes made.")
    sys.exit(0)

content = original_content

# ── Locate the tabs definition line (flexible — matches current 5-tab or earlier 4-tab forms) ──
tabs_pattern = re.compile(
    r'tab_iam,\s*tab_ai,\s*tab_gov,\s*tab_aigov(?:,\s*tab_intake)?\s*=\s*st\.tabs\(\['
    r'[^\]]*\]\)'
)

match = tabs_pattern.search(content)
if not match:
    print("[!] Could not find the expected tabs() definition line — aborting, no changes made.")
    sys.exit(1)

new_tabs_line = (
    'tab_iam, tab_ai, tab_gov, tab_aigov, tab_intake, tab_docs = st.tabs(['
    '"🪪 IAM Risk Assessment", "🤖 AI Adoption Risk Advisor", '
    '"🏛️ Risk Governance", "🧠 AI Governance", "📥 Risk Intake & Workflow", '
    '"📄 Vendor Document Assessment"])'
)

content = content[:match.start()] + new_tabs_line + content[match.end():]

# ── Add the import ──
import_marker = "from ai_risk_advisor import generate_ai_risk_assessment"
if import_marker not in content:
    print("[!] Could not find expected import line for ai_risk_advisor — aborting, no changes made.")
    sys.exit(1)

content = content.replace(
    import_marker,
    import_marker + "\nfrom vendor_doc_assessment import extract_text_from_pdf, generate_vendor_document_assessment"
)

docs_block = '''

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

                with st.spinner("Performing second-line vendor risk assessment..."):
                    assessment = generate_vendor_document_assessment(
                        vendor_name=vendor_name,
                        business_unit=vendor_business_unit if vendor_business_unit.strip() else "Not specified",
                        documents=documents
                    )

                st.markdown(assessment)

                os.makedirs("reports", exist_ok=True)
                report_path = "reports/vendor_document_assessment.md"
                with open(report_path, "w") as f:
                    f.write(assessment)

                st.success("Vendor document risk assessment complete.")

                st.download_button(
                    "Download Vendor Risk Assessment",
                    data=assessment,
                    file_name="vendor_document_assessment.md",
                    mime="text/markdown"
                )
    else:
        st.info("Upload one or more vendor documents above to begin the assessment.")
'''

content = content + docs_block

with open(FILE + ".backup", "w") as f:
    f.write(original_content)

with open(FILE, "w") as f:
    f.write(content)

try:
    py_compile.compile(FILE, doraise=True)
    print("===== VENDOR DOCUMENT ASSESSMENT TAB ADDED =====")
    print("  [+] New tab: Vendor Document Assessment")
    print("  [+] Multi-file PDF upload")
    print("  [+] Text extraction with per-document and total length caps")
    print("  [+] Claude-powered assessment grounded in actual document content")
    print("  [+] Explicit evidence-gap identification (what's missing, not just what's present)")
    print("  [+] Framework mapping consistent with rest of platform")
    print("  [+] Syntax check: PASSED")
    print("  [+] Backup saved: " + FILE + ".backup")
    print("")
    print("IMPORTANT: also run  pip3 install pypdf  before testing.")
    print("Next: streamlit run src/dashboard.py")
except py_compile.PyCompileError as err:
    with open(FILE + ".backup") as f:
        restore = f.read()
    with open(FILE, "w") as f:
        f.write(restore)
    print("[!] Syntax check FAILED — original file restored automatically.")
    print(err)
    sys.exit(1)