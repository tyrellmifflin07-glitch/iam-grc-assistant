# src/ai_risk_advisor.py
# Purpose: Second-line risk advisory for AI adoption use cases
# Generates structured AI risk assessments using the Claude API

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

def get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client using API key from .env"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")
    return anthropic.Anthropic(api_key=api_key)

def build_ai_risk_prompt(
    use_case: str,
    data_types: list,
    deployment_model: str,
    vendor_involved: str,
    business_unit: str
) -> str:
    """Build a structured prompt for AI adoption risk assessment."""

    data_types_text = ", ".join(data_types) if data_types else "Not specified"

    prompt = f"""You are a senior second-line technology risk advisor performing an AI adoption risk assessment for a regulated financial services organization.

A business unit has proposed the following AI use case:

PROPOSED AI USE CASE: {use_case}
BUSINESS UNIT: {business_unit}
DATA TYPES INVOLVED: {data_types_text}
DEPLOYMENT MODEL: {deployment_model}
THIRD-PARTY VENDOR INVOLVED: {vendor_involved}

Produce a structured second-line risk assessment with the following sections:

## AI Adoption Risk Assessment

### 1. Use Case Summary
Brief restatement of the proposed AI adoption and its risk-relevant characteristics.

### 2. Risk Identification by Taxonomy
Identify specific risks in each applicable category:
- **AI Risk** — model behavior, hallucination, bias, explainability, automated decision-making
- **Data Risk** — privacy, data residency, training data exposure, retention, classification
- **Cyber Risk** — prompt injection, data exfiltration, credential exposure, attack surface
- **Technology Risk** — availability, integration failures, vendor lock-in, change management
- **Third-Party Risk** — vendor governance, subprocessor chains, contractual controls (if applicable)

For each risk, state: the risk, likelihood (High/Medium/Low), impact (High/Medium/Low), and rationale.

### 3. Recommended Controls
Specific, actionable controls for the highest-priority risks. Include both preventive and detective controls. Reference control design principles a first-line team could implement.

### 4. Regulatory & Framework Considerations
Map the key risks to relevant expectations under: NIST AI RMF, NIST 800-53, DORA (ICT and third-party risk articles), COBIT, SOC 2, and applicable data protection considerations (GLBA/HIPAA where relevant to the data types).

### 5. Second-Line Recommendation
Provide one of: APPROVE / APPROVE WITH CONDITIONS / DEFER PENDING REMEDIATION — with a concise rationale and any conditions.

Write in professional second-line risk advisory language suitable for a governance forum. Be specific to the use case described, not generic."""

    return prompt

def generate_ai_risk_assessment(
    use_case: str,
    data_types: list,
    deployment_model: str,
    vendor_involved: str,
    business_unit: str
) -> str:
    """Send AI use case details to Claude and return a structured risk assessment."""
    client = get_client()
    prompt = build_ai_risk_prompt(use_case, data_types, deployment_model, vendor_involved, business_unit)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


if __name__ == "__main__":
    # Test run with a sample use case
    sample = generate_ai_risk_assessment(
        use_case="Deploy an AI chatbot for customer service that can access customer account balances and transaction history to answer questions",
        data_types=["Customer PII", "Financial account data", "Transaction history"],
        deployment_model="Third-party SaaS (cloud-hosted)",
        vendor_involved="Yes",
        business_unit="Retail Banking Operations"
    )
    print(sample)