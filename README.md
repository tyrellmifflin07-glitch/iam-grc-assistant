# AI IAM/GRC Assistant

**An AI-powered Identity & Access Management risk analysis, enterprise risk taxonomy classification, and AI adoption risk advisory tool.**

Built for cybersecurity consultants, IAM practitioners, and GRC professionals serving banks, healthcare organizations, law firms, and managed service providers.

🌐 **Live App:** [iam-grc-assistant.streamlit.app](https://iam-grc-assistant.streamlit.app)

---

## What It Does

### Tab 1 — IAM Risk Assessment

Upload IAM user access data and the tool automatically:

* Detects access risks including terminated users with active accounts, contractors with privileged access, dormant accounts, and ungoverned privileged users
* Classifies every finding across **enterprise risk taxonomies** — Cyber, Technology, Data, AI, and Third-Party Risk — aligned to ERM framework structures
* Maps every finding to specific controls across **seven frameworks**: NIST 800-53, PCI-DSS, SOC 2, HIPAA, COSO, COBIT, and DORA
* Generates AI-powered audit narratives using Claude by Anthropic — including executive summary, thematic risk analysis, priority findings detail, and systemic remediation recommendations
* Produces an executive summary with overall risk rating and priority actions
* Exports audit-ready PDF and Markdown reports for client delivery

### Tab 2 — AI Adoption Risk Advisor

Describe a proposed AI use case and receive a structured second-line risk assessment:

* Risk identification across **AI, Data, Cyber, Technology, and Third-Party** risk taxonomies with likelihood and impact ratings
* Recommended preventive and detective controls with first-line ownership assignments
* Regulatory and framework mappings including **NIST AI RMF and DORA**
* Formal second-line recommendation: Approve / Approve with Conditions / Defer Pending Remediation

---

## Scalability

Stress-tested against enterprise-scale datasets:

| Users   | Analysis Time | Findings Processed |
| ------- | ------------- | ------------------ |
| 1,000   | < 0.01s       | 232                |
| 10,000  | < 0.01s       | 2,502              |
| 50,000  | 0.02s         | 12,316             |
| 100,000 | 0.05s         | 24,925             |

The AI narrator uses intelligent aggregation — statistical summaries of the full finding population plus prioritized detail on Critical and High findings — enabling audit report generation on datasets of any size while producing executive-quality output. A test data generator (`generate_test_data.py`) is included for reproducing these benchmarks.

---

## Target Clients

| Industry              | Use Case                                                     |
| --------------------- | ------------------------------------------------------------ |
| Banks & Credit Unions | Access reviews, regulatory exam preparation, FFIEC alignment |
| Healthcare            | HIPAA workforce access controls, ePHI access governance      |
| Law Firms             | Privileged access governance, matter-based access control    |
| MSPs                  | Client IAM assessments, recurring access certification       |

---

## Tech Stack

| Layer           | Technology             |
| --------------- | ---------------------- |
| Language        | Python 3.11            |
| Data Processing | Pandas                 |
| AI Engine       | Claude API (Anthropic) |
| UI              | Streamlit              |
| PDF Export      | ReportLab              |
| Version Control | Git                    |

---

## Project Structure

```text
iam_grc_assistant/
├── data/
│   ├── users.csv
│   └── uploaded_users.csv
│
├── reports/
│   ├── executive_summary.md
│   ├── executive_summary.pdf
│   ├── audit_report.md
│   ├── audit_report.pdf
│   └── ai_risk_assessment.md
│
├── src/
│   ├── risk_engine.py          # Rule-based IAM risk detection
│   ├── risk_taxonomy.py        # Enterprise risk taxonomy classifier
│   ├── framework_mapper.py     # 7-framework control mapping
│   ├── ai_narrator.py          # Scalable AI audit narrative generation
│   ├── ai_risk_advisor.py      # AI adoption risk assessments
│   ├── executive_summary.py    # Executive summary generator
│   ├── pdf_generator.py        # PDF report export
│   └── dashboard.py            # Streamlit two-tab web interface
│
├── generate_test_data.py       # Enterprise-scale test data generator
├── .env
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/tyrellmifflin07-glitch/iam-grc-assistant.git
cd iam-grc-assistant
```

### 2. Create and Activate Virtual Environment

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 5. Run the Dashboard

```bash
streamlit run src/dashboard.py
```

Open your browser to:

```text
http://localhost:8501
```

### 6. Optional — Generate Test Data at Scale

```bash
python3 generate_test_data.py 10000
```

Creates `data/test_users_10000.csv` with realistic risk distributions for stress testing.

---

## Input Data Format

Your CSV file should include the following columns:

| Column         | Description                     |
| -------------- | ------------------------------- |
| user_id        | Unique user identifier          |
| username       | Login name                      |
| department     | Business unit                   |
| role           | Job role or title               |
| access_level   | Standard or Privileged          |
| last_login     | Date of last login (YYYY-MM-DD) |
| account_status | Active or Terminated            |
| manager        | Manager username                |

The dashboard validates uploaded files against this template and rejects non-conforming datasets with clear guidance.

---

## Risk Detection Rules

| Finding                             | Severity | Primary Taxonomy | Frameworks                                          |
| ----------------------------------- | -------- | ---------------- | --------------------------------------------------- |
| Terminated user with active account | Critical | Cyber Risk       | NIST AC-2, PCI 8.2.6, SOC 2 CC6.2, HIPAA 164.308    |
| Contractor with privileged access   | High     | Cyber Risk       | NIST AC-6, PCI 7.2.1, SOC 2 CC6.3, HIPAA 164.308    |
| Dormant account 90+ days            | Medium   | Cyber Risk       | NIST AC-2(3), PCI 8.2.6, SOC 2 CC6.2, HIPAA 164.308 |
| Privileged user with no manager     | High     | Technology Risk  | NIST AC-5, PCI 7.2.2, SOC 2 CC6.3, HIPAA 164.308    |

All findings are additionally mapped to **COSO principles, COBIT objectives, and DORA articles**, with secondary taxonomy classification and rationale.

---

## Outputs

The application generates:

* Executive Summary (Markdown + PDF)
* Audit Report with thematic risk analysis (Markdown + PDF)
* AI Adoption Risk Assessment (Markdown)
* Enterprise Risk Taxonomy Summary (in-dashboard)

All reports are saved automatically in the `reports/` directory and can be downloaded directly from the Streamlit dashboard.

---

## Portfolio Value

This project demonstrates:

* Identity and Access Management (IAM)
* Governance, Risk, and Compliance (GRC)
* Enterprise Risk Taxonomy Classification (ERM alignment)
* Second-Line AI Adoption Risk Advisory
* Access Review Automation at Enterprise Scale
* Risk-Based Access Analysis
* AI-Assisted Audit Narrative Generation
* Multi-Framework Compliance Mapping (NIST, PCI-DSS, SOC 2, HIPAA, COSO, COBIT, DORA)
* Streamlit Web Application Development
* PDF Deliverable Generation
* Git Version Control
* Secure API Integration

---

## Future Enhancements

Planned enhancements include:

* Executive risk dashboard with charts
* ZIP report downloads
* Remediation tracking and closure workflows
* Active Directory integration
* Microsoft Entra ID integration
* AWS IAM integration
* SailPoint export ingestion
* Okta export ingestion
* Automated access certification workflows

---

## Built By

**Tyrell Bey**
Cybersecurity Architect & IAM/GRC Consultant
New Castle, Delaware

🌐 [Live App](https://iam-grc-assistant.streamlit.app) · 💻 [GitHub](https://github.com/tyrellmifflin07-glitch) · 🔗 [LinkedIn](https://linkedin.com/in/tyrell-mifflin-ceh-csm-85a27583)

Certifications:

* CEH (Certified Ethical Hacker)
* CSM (Certified ScrumMaster)
* CCSP (In Progress)

Specializations:

* IAM Governance
* Governance, Risk & Compliance (GRC)
* Enterprise Risk Taxonomy & Second-Line Advisory
* Cloud Security
* NIST 800-53 · PCI-DSS · SOC 2 · HIPAA · COSO · COBIT · DORA