# add_docx_export.py
# Purpose: Wire the styled Word document export into the Vendor Document
# Assessment tab, so the cross-document analysis can be downloaded as a
# polished .docx (headers, tables, shaded Position callouts) in addition
# to the existing markdown download.
#
# Run from inside the iam_grc_assistant folder:  python3 add_docx_export.py

import os
import sys
import py_compile

FILE = "src/dashboard.py"

if not os.path.exists(FILE):
    print("[!] src/dashboard.py not found. Run this from inside iam_grc_assistant.")
    sys.exit(1)

with open(FILE, "r") as f:
    original_content = f.read()

if "report_docx_export" in original_content:
    print("[=] Docx export already wired in. No changes made.")
    sys.exit(0)

content = original_content

import_marker = "from vendor_doc_assessment import extract_text_from_pdf, generate_vendor_document_assessment"
if import_marker not in content:
    print("[!] Could not find expected vendor_doc_assessment import — aborting, no changes made.")
    sys.exit(1)

content = content.replace(
    import_marker,
    import_marker + "\nfrom report_docx_export import markdown_report_to_docx"
)

old_download = '''                st.download_button(
                    "Download Vendor Risk Assessment",
                    data=assessment,
                    file_name="vendor_document_assessment.md",
                    mime="text/markdown"
                )'''

if old_download not in content:
    print("[!] Could not find expected download button block — aborting, no changes made.")
    sys.exit(1)

new_download = '''                st.download_button(
                    "Download Vendor Risk Assessment (Markdown)",
                    data=assessment,
                    file_name="vendor_document_assessment.md",
                    mime="text/markdown"
                )

                docx_path = "reports/vendor_document_assessment.docx"
                try:
                    markdown_report_to_docx(assessment, docx_path, title=f"Independent Risk Assessment — {vendor_name}")
                    with open(docx_path, "rb") as f:
                        docx_bytes = f.read()
                    st.download_button(
                        "Download Vendor Risk Assessment (Word)",
                        data=docx_bytes,
                        file_name=f"{vendor_name.replace(' ', '_')}_Risk_Assessment.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.warning(f"Word export unavailable: {e}")'''

content = content.replace(old_download, new_download)

with open(FILE + ".backup", "w") as f:
    f.write(original_content)

with open(FILE, "w") as f:
    f.write(content)

try:
    py_compile.compile(FILE, doraise=True)
    print("===== DOCX EXPORT WIRED IN =====")
    print("  [+] Vendor assessments can now be downloaded as styled Word documents")
    print("  [+] Markdown download preserved alongside new Word download")
    print("  [+] Syntax check: PASSED")
    print("  [+] Backup saved: " + FILE + ".backup")
    print("")
    print("IMPORTANT: also run  pip3 install python-docx  before testing.")
    print("Next: streamlit run src/dashboard.py")
except py_compile.PyCompileError as err:
    with open(FILE + ".backup") as f:
        restore = f.read()
    with open(FILE, "w") as f:
        f.write(restore)
    print("[!] Syntax check FAILED — original file restored automatically.")
    print(err)
    sys.exit(1)