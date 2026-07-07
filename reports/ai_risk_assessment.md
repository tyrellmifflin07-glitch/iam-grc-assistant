# AI Adoption Risk Assessment

**Assessment Reference:** TRM-AI-2024-RB-001
**Business Unit:** Retail Banking Operations
**Assessment Tier:** Second-Line Technology Risk
**Classification:** Internal – Restricted
**Assessment Date:** [Date]
**Prepared By:** Technology Risk Advisory, Second Line of Defence

---

## 1. Use Case Summary

Retail Banking Operations proposes to deploy a third-party SaaS-hosted AI chatbot to serve as a customer-facing service channel. The system would authenticate to, and retrieve data from, live customer accounts — including personally identifiable information (PII), account balances, and transaction history — to resolve customer enquiries in natural language.

From a risk perspective, this use case presents a materially elevated risk profile relative to a standard chatbot deployment. The combination of four compounding factors warrants heightened scrutiny:

1. **Live access to sensitive financial data** — the chatbot is not operating on anonymised or summarised data; it will process and surface real-time account-level financial records.
2. **Third-party SaaS delivery model** — the organisation does not control the underlying model, infrastructure, or data handling practices; all three are delegated to an external vendor operating in a shared cloud environment.
3. **Direct customer interaction** — the system will generate natural language responses consumed by retail customers who may act on them, creating a duty-of-care and consumer protection exposure.
4. **Automated access to core banking systems** — integration between the chatbot and account infrastructure introduces a new attack surface into what is otherwise a well-controlled environment.

This assessment does not evaluate whether the business case is commercially sound; it evaluates whether the risk profile is manageable within the organisation's stated risk appetite and regulatory obligations.

---

## 2. Risk Identification by Taxonomy

### 2.1 AI Risk

| Risk | Likelihood | Impact | Rationale |
|---|---|---|---|
| **Model hallucination producing incorrect account information** — The AI may generate plausible but factually incorrect responses about balances, transaction dates, fees, or product terms, even when retrieved data is accurate, due to model interpolation behaviour. | Medium | High | Large Language Model (LLM) architectures are architecturally prone to hallucination even in retrieval-augmented configurations. Customers acting on incorrect balance or transaction data may suffer financial harm or make erroneous payment decisions. Regulatory consumer protection obligations (e.g., FCA Consumer Duty, CFPB unfair practices standards) are directly engaged. |
| **Absence of explainability for responses** — The chatbot will not be able to articulate why it provided a particular response, making complaint investigation, audit trails, and regulatory enquiry responses operationally difficult. | High | Medium | LLM reasoning is inherently opaque. If a customer disputes advice or information provided by the chatbot, the organisation cannot reconstruct the logical path of the response. This creates evidentiary gaps in complaint handling and regulatory examination scenarios. |
| **Unintended automated decision-making** — Depending on how the chatbot is scoped, it may be perceived by customers — or function in practice — as making decisions about account status, eligibility, or dispute outcomes, rather than purely providing information. | Medium | High | If the chatbot's outputs influence, trigger, or substitute for human decisions on regulated matters (e.g., fraud alerts, account restrictions), the organisation may inadvertently operate an automated decision-making system subject to enhanced obligations under GDPR Article 22 or equivalent state privacy law provisions, without the required disclosures or human review mechanisms. |
| **Demographic or linguistic bias in response quality** — The underlying model may perform materially worse for customers using non-standard English, regional dialects, or who have lower financial literacy, resulting in inequitable service quality across the customer base. | Medium | High | Vendor-trained models are typically trained on data sets with demographic skews. Uneven response quality across customer segments constitutes a fair lending and fair banking risk, and may attract supervisory attention under Community Reinvestment Act (CRA) or Treating Customers Fairly (TCF) frameworks. |

---

### 2.2 Data Risk

| Risk | Likelihood | Impact | Rationale |
|---|---|---|---|
| **Customer PII and financial data transmitted to and processed by a third-party cloud environment** — All conversational context, including account numbers, balances, and transaction details, will transit to and be processed within vendor-controlled infrastructure. | High | High | This represents an unambiguous data sharing arrangement with a third party. Without contractual data processing agreements and verified technical controls, the organisation cannot demonstrate GLBA Safeguards Rule compliance, satisfy GDPR/state CCPA data processor obligations, or validate that data is not used for vendor model training purposes. |
| **Customer conversation data used for model training or fine-tuning by the vendor** — Many SaaS AI vendors retain conversation logs and use them to improve their models. Customer financial conversations contain highly sensitive data unsuitable for such use. | Medium | High | Unless explicitly prohibited by contract, default vendor terms frequently permit use of customer-generated data for model improvement. This would constitute unauthorised secondary processing of financial PII and potentially a GLBA violation. This risk is frequently under-assessed in AI procurement. |
| **Data residency and cross-border transfer** — Cloud-hosted SaaS solutions typically process data across multiple geographies. Customer financial data may be processed in jurisdictions outside the organisation's operational footprint without adequate transfer mechanisms. | Medium | High | GLBA requires adequate safeguards over customer information regardless of where it is processed. For organisations with EU-resident customers, GDPR Chapter V transfer restrictions apply. Many US state privacy laws impose additional residency or transfer notification requirements. Vendor sub-processors add further uncertainty. |
| **Excessive data exposure within the chatbot session** — The integration may grant the chatbot access to broader account data than is required to answer a given query, violating data minimisation principles. | High | Medium | Without field-level API controls, the chatbot may retrieve and temporarily process full account records to answer narrow questions (e.g., "what is my current balance?"). This represents both a data minimisation failure and an unnecessary enlargement of the sensitive data surface exposed to the AI system. |
| **Conversation log retention and disposal** — Chat transcripts containing PII and financial data may be retained by the vendor beyond the organisation's record retention schedule, or disposed of in ways inconsistent with the organisation's data lifecycle policy. | Medium | Medium | GLBA requires organisations to implement appropriate disposal standards for customer information. If vendor-side retention schedules are not contractually aligned and technically enforced, the organisation cannot demonstrate compliance with its own privacy programme. |

---

### 2.3 Cyber Risk

| Risk | Likelihood | Impact | Rationale |
|---|---|---|---|
| **Prompt injection attacks** — A malicious actor may craft customer inputs designed to override system instructions, bypass access controls, extract data from other customers' sessions, or cause the chatbot to perform unintended actions against backend systems. | High | High | Prompt injection is a well-documented and actively exploited attack vector against LLM-based systems. In this deployment, successful prompt injection could expose other customers' financial data, manipulate the AI into providing fraudulent account information, or — if write capabilities exist — trigger unauthorised account actions. This is the single highest-severity cyber risk in this use case. |
| **Data exfiltration via conversational output** — An attacker may elicit responses that cause the chatbot to surface account data belonging to other customers, effectively using the AI as an unintended data exfiltration vector. | Medium | High | If session isolation controls are not robust and the system has broad data access privileges, targeted prompt manipulation could cause cross-customer data leakage. This would constitute a data breach triggering notification obligations under GLBA, GDPR, and applicable state breach notification laws. |
| **Credential and API key exposure** — The integration between the chatbot and core banking systems requires service account credentials or API keys. Compromise of the vendor environment could expose these credentials, granting an attacker direct access to the core banking API. | Medium | Critical | The API integration credentials represent a high-value target. If these credentials are stored insecurely within the vendor SaaS environment, a vendor-side breach could provide a direct pathway into the organisation's account infrastructure — bypassing perimeter controls that would otherwise protect those systems. |
| **Expanded attack surface via third-party SaaS integration** — The vendor's SaaS platform represents a new external endpoint connected to internal banking infrastructure. This extends the organisation's effective attack surface to include the vendor's security posture. | High | High | The organisation's attack surface is no longer bounded by its own perimeter. Any vulnerability in the vendor's platform, its cloud provider, or its subprocessors becomes a potential vector into the organisation's systems. This is compounded by the vendor's use of cloud infrastructure over which neither the organisation nor the vendor may have full visibility. |
| **Session hijacking or authentication bypass** — Weak session management in the chatbot could allow an attacker to assume another customer's session and access their account data through the AI interface. | Low | Critical | While baseline likelihood is assessed as low (dependent on vendor implementation quality), the impact of a successful session hijack is critical given the live account data access. This risk is directly mitigated by strong authentication controls but must be validated through third-party penetration testing. |

---

### 2.4 Technology Risk

| Risk | Likelihood | Impact | Rationale |
|---|---|---|---|
| **Chatbot unavailability causing customer service disruption** — SaaS availability is dependent on the vendor's infrastructure and SLA commitments. Outages in the chatbot channel may displace customer service volumes to other channels, creating capacity and reputational risk. | Medium | Medium | If the chatbot becomes a primary customer service channel, its availability directly affects customer experience. Unlike internally hosted systems, the organisation has limited ability to remediate vendor-side outages. Recovery time and communication during outages must be explicitly addressed in the vendor SLA and in the organisation's business continuity arrangements. |
| **Integration failure between chatbot and core banking systems** — API integration points between the SaaS chatbot and the core banking platform introduce a dependency that may fail due to API versioning changes, authentication token expiry, or upstream system maintenance windows. | Medium | High | Integration failures may either render the chatbot non-functional or, more problematically, cause it to respond to customers based on stale or incomplete data. The latter scenario creates a higher risk than simple unavailability, as customers may receive and act upon incorrect account information presented with apparent confidence. |
| **Vendor lock-in and exit risk** — Dependence on a single SaaS AI vendor for a customer-facing channel creates switching costs and concentration risk. Vendor insolvency, pricing changes, or unilateral terms modifications may be difficult to remediate quickly. | Medium | Medium | AI SaaS markets remain consolidating and immature. The organisation should assess its ability to substitute an alternative solution within an operationally acceptable timeframe without material customer service disruption. Exit provisions and data portability rights must be explicitly contractualised. |
| **Change management risk from AI-driven model updates** — The vendor may update the underlying model (e.g., alter response behaviour, update training data) without advance notice, causing response quality or behaviour to change in production without the organisation's knowledge or approval. | High | High | This is a frequently overlooked risk. Unlike traditional software, AI model updates can materially alter system behaviour in ways that are not surfaced through standard change notification processes. A vendor model update could introduce new hallucination patterns, alter tone, or change how account data is interpreted and presented — all without triggering the organisation's change management controls. |

---

### 2.5 Third-Party Risk

| Risk | Likelihood | Impact | Rationale |
|---|---|---|---|
| **Inadequate vendor due diligence on AI-specific controls** — Standard third-party risk assessments may not cover AI-specific controls such as model governance, training data provenance, hallucination rates, or bias testing. Existing vendor assessment frameworks may produce an incomplete risk picture. | High | High | Third-party risk programmes in financial services are typically designed for traditional software and infrastructure vendors. AI-specific risks — model drift, training data contamination, adversarial robustness — are not captured in standard questionnaire-based assessments. This gap creates a false assurance risk. |
| **Subprocessor chain opacity** — The vendor's SaaS platform will almost certainly rely on one or more subprocessors (cloud infrastructure provider, AI model API provider). Each subprocessor represents an additional link in the data processing chain with its own security posture. | High | High | The organisation may have limited visibility into how customer data flows through the vendor's subprocessor ecosystem. If the vendor uses a third-party LLM API (e.g., an underlying model provider) as a component of its service, customer data may flow to entities not directly contracted with the organisation and not subject to its due diligence programme. |
| **Contractual gaps in AI-specific provisions** — Standard Master Service Agreements and DPAs may not include provisions specific to AI deployments, including prohibitions on training data use, model audit rights, explainability obligations, or AI-specific incident notification. | High | High | AI contracts in the financial services sector frequently lack adequate provisions for model governance, right to audit AI behaviour, incident notification for model changes, and restrictions on secondary data use. Without these provisions, the organisation has limited contractual recourse for AI-specific failure modes. |
| **Vendor financial and operational resilience** — AI SaaS vendors, particularly those operating in newer segments of the market, may carry elevated insolvency, acquisition, or operational disruption risk relative to established technology vendors. | Medium | Medium | Vendor viability should be assessed as part of concentration and third-party risk management. For a customer-facing channel handling sensitive financial data, vendor resilience must be evaluated both in terms of service continuity and in terms of data custody obligations in an insolvency or acquisition scenario. |

---

## 3. Recommended Controls

Controls are presented in priority order, addressing the highest-severity risks identified above. First-line implementation ownership is indicated for each.

---

### 3.1 Prompt Injection and AI Attack Surface (CRITICAL PRIORITY)

**Preventive Controls:**
- **Input validation and sanitisation layer:** Implement a dedicated input filtering layer between the customer interface and the AI model that detects and blocks known prompt injection patterns. This should be implemented as a pre-processing component independent of the vendor's own controls. *(First-line: Platform Engineering / Cybersecurity)*
- **System prompt hardening:** Require the vendor to demonstrate that system prompts are immutable to user input, cryptographically separated from user message context, and that the model is constrained to a defined operational scope (account enquiry only). Obtain documented evidence of this architecture. *(First-line: Vendor Management / Platform Engineering)*
- **Strict data scoping via API controls:** Implement field-level API controls that limit data returned to the chatbot to the minimum necessary fields to answer the specific query type. The chatbot should not have access to full account record sets; it should query only for the specific data element required. *(First-line: Integration / Platform Engineering)*
- **Read-only API permissions:** Enforce that all API credentials used by the chatbot are strictly read-only, with no write, transfer, or modification permissions. This should be verified at the API gateway level, not solely by relying on chatbot-side logic. *(First-line: Platform Engineering / Core Banking Integration)*

**Detective Controls:**
- **Real-time session anomaly monitoring:** Implement automated monitoring on chatbot sessions to detect patterns indicative of prompt injection (e.g., unusually long inputs, inputs containing instruction-like syntax, atypically high data volumes in responses). Alert thresholds should be defined and tested before go-live. *(First-line: Cybersecurity Operations)*
- **Third-party penetration testing with AI-specific scope:** Commission a penetration test specifically scoped to include prompt injection, session isolation, and data exfiltration via AI interaction vectors before go-live. Standard application penetration testing does not typically cover AI-specific attack techniques. *(First-line: Cybersecurity / Risk)*

---

### 3.2 Data Protection and Third-Party Data Handling (HIGH PRIORITY)

**Preventive Controls:**
- **Explicit contractual prohibition on training data use:** The Data Processing Agreement (DPA) must include an unambiguous prohibition on the vendor (and all subprocessors) using customer conversation data, query data, or retrieved account data for any model training, fine-tuning, benchmarking, or research purpose. This must be backed by a technical attestation, not solely a contractual representation. *(First-line: Legal / Vendor Management)*
- **Subprocessor identification and approval:** Require the vendor to disclose all subprocessors involved in data processing for this deployment, including the underlying AI model provider, cloud infrastructure provider, and any analytics or logging subprocessors. Each subprocessor must be evaluated and approved before deployment, with contractual flow-down of data protection obligations. *(First-line: Third-Party Risk / Privacy)*
- **Data residency constraints:** Contractually restrict all customer data processing to jurisdictions approved under the organisation's data governance policy. Obtain technical evidence (e.g., cloud region configuration, infrastructure attestation) that data does not transit or rest in non-approved jurisdictions. *(First-line: Privacy / Vendor Management)*
- **Conversation log retention limits:** Define and contractually enforce maximum retention periods for conversation logs on the vendor side, aligned with the organisation's data retention schedule. Require automated deletion and obtain periodic deletion attestations