# AI IAM/GRC Assistant

**An AI-powered Identity & Access Management risk analysis and compliance reporting tool.**

Built for cybersecurity consultants, IAM practitioners, and GRC professionals serving banks, healthcare organizations, law firms, and managed service providers.

---

## What It Does

Upload IAM user access data and the tool automatically:

* Detects access risks including terminated users with active accounts, contractors with privileged access, dormant accounts, and ungoverned privileged users
* Maps findings to controls across NIST 800-53, PCI-DSS, SOC 2, and HIPAA
* Generates AI-powered audit narratives using Claude by Anthropic
* Produces an executive summary with overall risk rating and priority actions
* Exports audit-ready PDF and Markdown reports for client delivery

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
│   └── audit_report.pdf
│
├── src/
│   ├── risk_engine.py
│   ├── ai_narrator.py
│   ├── executive_summary.py
│   ├── pdf_generator.py
│   └── dashboard.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/iam_grc_assistant.git
cd iam_grc_assistant
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

Upload a CSV file and click:

```text
Run IAM Risk Assessment
```

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

---

## Risk Detection Rules

| Finding                             | Severity | Frameworks                                          |
| ----------------------------------- | -------- | --------------------------------------------------- |
| Terminated user with active account | Critical | NIST AC-2, PCI 8.2.6, SOC 2 CC6.2, HIPAA 164.308    |
| Contractor with privileged access   | High     | NIST AC-6, PCI 7.2.1, SOC 2 CC6.3, HIPAA 164.308    |
| Dormant account 90+ days            | Medium   | NIST AC-2(3), PCI 8.2.6, SOC 2 CC6.2, HIPAA 164.308 |
| Privileged user with no manager     | High     | NIST AC-5, PCI 7.2.2, SOC 2 CC6.3, HIPAA 164.308    |

---

## Outputs

The application generates:

* Executive Summary (Markdown)
* Audit Report (Markdown)
* Executive Summary (PDF)
* Audit Report (PDF)

All reports are saved automatically in the `reports/` directory and can be downloaded directly from the Streamlit dashboard.

---

## Portfolio Value

This project demonstrates:

* Identity and Access Management (IAM)
* Governance, Risk, and Compliance (GRC)
* Access Review Automation
* Risk-Based Access Analysis
* AI-Assisted Audit Narrative Generation
* Compliance Reporting
* Streamlit Web Application Development
* PDF Deliverable Generation
* Git Version Control
* Secure API Integration

---

## Future Enhancements

Planned enhancements include:

* Structured compliance control mapping
* Executive risk dashboard with charts
* ZIP report downloads
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
Wilmington, Delaware

Certifications:

* CEH (Certified Ethical Hacker)
* CSM (Certified ScrumMaster)
* CCSP (In Progress)

Specializations:

* IAM Governance
* Governance, Risk & Compliance (GRC)
* Cloud Security
* NIST 800-53
* PCI-DSS
* SOC 2
* HIPAA
