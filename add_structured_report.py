# add_structured_report.py
# Purpose: Replace the markdown-based vendor assessment flow in the
# "Vendor Document Assessment" tab with a structured JSON pipeline that
# feeds directly into report_generator.build_report() for a polished,
# reliably-styled Word document — no markdown parsing required.
#
# PREREQUISITE: report_generator.py must already be placed in src/ before
# running this script.
#
# Run from inside the iam_grc_assistant folder:  python3 add_structured_report.py

import os
import sys
import py_compile

FILE = "src/dashboard.py"
GEN_FILE = "src/report_generator.py"

if not os.path.exists(FILE):
    print("[!] src/dashboard.py not found. Run this from inside iam_grc_assistant.")
    sys.exit(1)

if not os.path.exists(GEN_FILE):
    print("[!] src/report_generator.py not found. Place report_generator.py in")
    print("    src/ BEFORE running this script.")
    sys.exit(1)

with open(FILE, "r") as f:
    original_content = f.read()

if "generate_structured_assessment" in original_content:
    print("[=] Structured report pipeline already wired in. No changes made.")
    sys.exit(0)

content = original_content

# ── Replace the import line ──
old_import = "from vendor_doc_assessment import extract_text_from_pdf, generate_vendor_document_assessment"
if old_import not in content:
    print("[!] Could not find expected vendor_doc_assessment import — aborting, no changes made.")
    sys.exit(1)

new_import = (
    "from vendor_doc_assessment import extract_text_from_pdf, generate_structured_assessment\n"
    "from report_generator import build_report"
)
content = content.replace(old_import, new_import)

# ── Remove the old docx-export import if present (from the previous approach) ──
content = content.replace(
    "\nfrom report_docx_export import markdown_report_to_docx", ""
)

# ── Replace the entire "Generate Vendor Risk Assessment" button block ──
old_block_marker_start = 'if st.button("Generate Vendor Risk Assessment"):'
if old_block_marker_start not in content:
    print("[!] Could not find the 'Generate Vendor Risk Assessment' button — aborting, no changes made.")
    sys.exit(1)

# Find the block from the button to the matching "else:" that closes the
# "if uploaded_docs:" statement (i.e. up to but not including that else).
start_idx = content.index(old_block_marker_start)
else_marker = '''    else:
        st.info("Upload one or more vendor documents above to begin the assessment.")'''
if else_marker not in content:
    print("[!] Could not find the tab's closing else block — aborting, no changes made.")
    sys.exit(1)
end_idx = content.index(else_marker)

new_block_raw = '''if st.button("Generate Vendor Risk Assessment"):
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
            for para in assessment.get("exec_summary", "").split("\\n\\n"):
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
                for para in assessment["root_cause"].split("\\n\\n"):
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

'''

# Re-indent every line of the block to match the original 8-space nesting level.
# The first line keeps NO extra prefix because the original 8 spaces of
# indentation before "if st.button(...)" are already preserved in
# content[:start_idx] (start_idx points at the "if", not before the spaces).
BASE_INDENT = "        "  # 8 spaces, matching the original button line's indentation
raw_lines = new_block_raw.split("\n")
indented_lines = [raw_lines[0]]  # no extra indent on the first line
for line in raw_lines[1:]:
    if line.strip() == "":
        indented_lines.append("")
    else:
        indented_lines.append(BASE_INDENT + line)
new_block = "\n".join(indented_lines)

content = content[:start_idx] + new_block + content[end_idx:]

with open(FILE + ".backup", "w") as f:
    f.write(original_content)

with open(FILE, "w") as f:
    f.write(content)

try:
    py_compile.compile(FILE, doraise=True)
    print("===== STRUCTURED REPORT PIPELINE WIRED IN =====")
    print("  [+] Vendor Document Assessment now uses structured JSON output")
    print("  [+] On-screen display: exec summary, findings, root cause")
    print("  [+] Word doc export uses report_generator.build_report() directly")
    print("  [+] No markdown parsing - eliminates the previous rendering bugs")
    print("  [+] Raw JSON download also available for debugging/reuse")
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