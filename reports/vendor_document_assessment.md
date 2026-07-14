# Independent Risk Assessment — ClearPath Platform

**Scope:** 12 documents: system architecture (CT-SAD-001 v3.2), security architecture (CT-SEC-001 v2.1), encryption standards (CT-ENC-001 v1.5), incident response plan (CT-IRP-001 v2.0), installation/configuration guide (CT-IG-001 v3.2), penetration test report (CT-PTR-2025), SBOM (CT-SBOM-3.2.1), SOC 1 Type II FY2025 (CT-SOC1-FY2025), executive security overview Q1 2026 (CT-ESO-2026-Q1), email correspondence (CT-EMAIL-2026-03), vulnerability scan Q4 2025, user guide v3.2. Note: ClearPath_Vulnerability_Scan_Q4_2025.pdf and ClearPath_User_Guide_v3.2.pdf were partially truncated in the provided text; findings derived from these documents are based on the portions available and are noted accordingly.
**Method:** Trust-layered cross-document reconciliation
**Basis of finding:** Every finding is traceable to a named contradiction or gap between two or more source documents
**Requesting Business Unit:** IT Operations
**Classification:** Confidential — Restricted

---

## 1. Executive Summary

ClearPath's stated security posture as presented to the executive team and board in CT-ESO-2026-Q1 is materially overstated relative to what the underlying evidence documents demonstrate. Three issues are of particular concern. First, the critical IDOR vulnerability (PT-2025-003) is declared "REMEDIATED March 2026" in the executive overview, but the email correspondence (CT-EMAIL-2026-03) and the penetration test report (CT-PTR-2025) together reveal that the remediation deployed in March 2026 was a targeted hotfix to a single endpoint, not the comprehensive cross-API authorisation audit that engineering itself identified as necessary before the fix could be considered architecturally complete; the S3 isolation failure (PT-2025-007) that directly amplifies the IDOR risk remains open with no near-term remediation. Second, the platform's assurance of "no evidence of exploitation" in relation to the IDOR finding is reached through a circular chain of reasoning: the primary log sources that would evidence exploitation — CloudTrail coverage of API Gateway and Lambda — are explicitly acknowledged as absent in the incident response plan, the security architecture document, and the SOC 1 report, meaning the absence-of-evidence conclusion cannot be supported by the detection capability actually available. Third, the SOC 1 Type II report identifies a pattern of change management control failures that directly contradict the security architecture's assertion that no production changes are made outside the approved change control process, a conflict that has not been surfaced in the executive narrative with adequate specificity.

---

## Findings at a Glance

| # | Finding | Rating | Type | Escalation To |
|---|---|---|---|---|
| F-01 | IDOR remediation declared complete but architecturally incomplete; S3 amplifier remains open | Critical | False assurance | CEO, Board, External Auditors |
| F-02 | "No evidence of exploitation" conclusion is circular — drawn from log sources the platform admits are absent | Critical | Assurance integrity | CEO, General Counsel, SOC 1 Auditors |
| F-03 | Change management control failures contradict security architecture's change control assertions; three unapproved production deployments during audit period | High | Governance / Documentation integrity | Board Audit Committee, SOC 1 Auditors |
| F-04 | Four exploitable CVEs in production components deferred to June 2026 with no interim compensating controls documented | High | Unverified control | IT Operations, Platform Engineering |
| F-05 | Password maximum length cap (16 chars) contradicts NIST SP 800-63B commitment stated in the security architecture's own note, and creates documented customer harm | Medium | Reconciliation | CEO, Head of Security |
| F-06 | AES-128-CBC used for export ZIP files containing customer financial data, classified as Level 2 to avoid AES-256 requirement — classification appears circular | Medium | Documentation integrity | Head of Security, Compliance |
| F-07 | MFA not enforced by platform default; installation guide and security architecture inconsistently characterise the customer's responsibility | Medium | Governance | IT Operations, Customer Success |
| F-08 | API JWT lifetime fixed at 24 hours and non-reducible by tenants — contradicts least-privilege principle stated in security architecture | Low | Reconciliation | Platform Engineering |

---

## 2. Detailed Findings

---

### F-01 — IDOR Remediation Declared Complete but Architecturally Incomplete; S3 Amplifier Remains Open — **Critical**

**Observation:**
CT-ESO-2026-Q1 (Section 2.1) states, under the heading "Critical: Multi-Tenant Isolation Failure," that a hotfix (v3.2.1-patch1) was deployed on 14 March 2026 and "closes this vulnerability," rating the item as "REMEDIATED." The executive summary therefore presents this as a closed matter requiring no further executive attention.

The email correspondence (CT-EMAIL-2026-03, R. Chen, 8 March 2026) tells a materially different story. R. Chen confirms that the root cause is that the `/api/v2/reports/` export sub-route was migrated to the v2 API framework without tenant_id middleware being correctly applied. He proposes a targeted hotfix to that specific endpoint as an interim measure, explicitly distinguishing it from the full fix: *"The fix itself is straightforward (add the tenant check), but we want to do a broader audit of all v2 API endpoints before shipping to make sure we haven't missed any others."* This broader audit is the condition engineering itself set for considering the vulnerability class closed — it is deferred to v3.2.2 (June 2026).

CT-PTR-2025 (Finding PT-2025-003, Remediation guidance) specifically states: *"This check should be applied to all resource endpoints in /api/v2/ that accept resource ID parameters"* — confirming that the scope of the correct fix is platform-wide, not endpoint-specific.

CT-PTR-2025 (Finding PT-2025-007) rates the S3 bucket misconfiguration (clearpath-tenant-reports-prod lacking per-prefix tenant isolation) as CRITICAL (CVSS 7.5) and explicitly describes it as amplifying PT-2025-003: if the application-layer check is bypassed at any other v2 endpoint not yet audited, or via SSRF, the S3 bucket provides no independent containment. CT-ESO-2026-Q1 (Section 2.4) lists PT-2025-007 as still open, targeted for v3.3 Q4 2026 — but does not connect this explicitly to the residual risk left by the partial IDOR remediation.

The combined effect: the executive overview presents the critical multi-tenant isolation risk as closed, while the engineering record shows (a) only one endpoint was fixed, (b) an unknown number of other v2 endpoints remain unaudited, and (c) the S3 layer that would have provided defence-in-depth against any remaining endpoint-level bypass remains misconfigured for at least another six months.

**Why this matters:**
The board and any relying parties (including user entities relying on the SOC 1 report) are operating under the belief that a critical data confidentiality risk has been fully resolved. If a different v2 endpoint carries the same missing tenant_id check — which engineering has explicitly not yet ruled out — the platform remains exposed to cross-tenant financial report access. Customer notifications were explicitly withheld on the basis that remediation was expedited and complete (CT-EMAIL-2026-03, P. Westbrook, 9 March 2026). If the remediation is incomplete, this notification decision may need to be revisited, with potential regulatory implications under GDPR (72-hour notification window) and contractual SLA obligations (CT-IRP-001, Section 5).

**Traceability:**
- CT-ESO-2026-Q1, Section 2.1 — declares IDOR "REMEDIATED March 2026" and states hotfix "closes this vulnerability"
- CT-EMAIL-2026-03, R. Chen 8 March 2026 — confirms hotfix is targeted to one endpoint; broader v2 API audit deferred to v3.2.2
- CT-PTR-2025, PT-2025-003 — remediation guidance explicitly requires the fix across all /api/v2/ resource endpoints, not a single sub-route
- CT-PTR-2025, PT-2025-007 — S3 misconfiguration amplifies the IDOR risk and remains open
- CT-ESO-2026-Q1, Section 2.4 — confirms PT-2025-007 open, targeted Q4 2026, but does not connect to residual IDOR exposure
- CT-SEC-001 v2.1, Section 3.2 — states tenant isolation is enforced through "mandatory tenant_id claim validated on every request" via middleware; this is the control the pen test demonstrated was not applied to the export sub-route, and which has not been verified across all v2 endpoints

> **Position:** This finding should be re-rated as Open — Partially Mitigated until: (1) the v2 API endpoint audit is complete and no additional IDOR-susceptible endpoints are confirmed, with results documented and independently reviewed; and (2) either the S3 per-prefix isolation is implemented or a specific compensating control is documented that addresses the S3 amplification path. The executive summary should be corrected before further board or customer distribution.

---

### F-02 — "No Evidence of Exploitation" Conclusion Is Circular — Drawn from Log Sources the Platform Admits Are Absent — **Critical**

**Observation:**
CT-ESO-2026-Q1 (Section 2.1) states: *"No evidence of exploitation in the production environment was found."* CT-EMAIL-2026-03 (P. Westbrook, 9 March 2026; A. Torres, 9 March 2026) documents that the decision not to notify customers was based in part on this conclusion: *"we have no evidence of production exploitation."* INC-2026-047 is documented as a "security vulnerability, not exploitation event."

The evidentiary basis for this conclusion is critically undermined by three separate documents:

**CT-IRP-001 v2.0 (Section 6, Evidence Preservation NOTE):** Contains an explicit, unresolved note: *"Current CloudTrail coverage does not [truncated]"* — the truncation cuts off the sentence, but the surrounding context and corroborating documents make clear what it states.

**CT-EMAIL-2026-03 (T. Osei, 8 March 2026):** Explicitly flags: *"the SOC 1 auditors also flagged that we don't have CloudTrail enabled for API Gateway and Lambda. That's a bigger piece of work (JIRA: PLAT-2847). I've got a proposal ready for the Q3 logging improvement project."* This is not a minor gap: API Gateway is the front-door through which every report export request must pass. Any exploitation of PT-2025-003 in production would have generated API Gateway logs — which are not captured in CloudTrail.

**CT-SOC1-FY2025 (Section 4, CO-05/CC-18 or equivalent logging controls — as available):** The SOC 1 report identifies the CloudTrail gap as an audit finding. The executive overview (CT-ESO-2026-Q1, Section 2.4) lists *"CloudTrail logging gap – Lambda and API Gateway"* as a High-rated open finding, targeted for Q3 2026.

**CT-IRP-001 v2.0 (Section 4.3):** States that the eradication and investigation phase uses *"CloudWatch logs, Splunk SIEM events, CloudTrail logs, and application logs"* and specifically that *"AWS CloudTrail S3 access logs are used to determine if any data was accessed or exfiltrated."* This is the documented forensic methodology — but the CloudTrail coverage that the IRP depends on does not extend to API Gateway, which is the specific attack surface for PT-2025-003.

The conclusion "no evidence of exploitation" is therefore drawn from a detection capability that, by the platform's own admission across three documents, does not cover the attack surface in question. This is a textbook circular assurance: the absence-of-evidence statement is only as strong as the completeness of the detection and logging infrastructure, and that infrastructure has a documented gap precisely at the relevant layer.

**Why this matters:**
The customer non-notification decision (CT-EMAIL-2026-03), the incident classification as Tier 3 rather than Tier 2 (CT-IRP-001, Section 2), and the SOC 1 management assertion (CT-SOC1-FY2025) all rest, directly or indirectly, on the claim that no production exploitation occurred. If this claim cannot be evidentially supported because the relevant logs were not captured, then: (a) the regulatory notification obligation assessment under GDPR and contractual SLAs (CT-IRP-001, Section 5) may have been made on a false premise; (b) the SOC 1 management assertion may be materially incomplete; and (c) ClearPath may face retrospective liability if exploitation did occur and is later evidenced by other means (e.g., a customer discovering unexpected access to their data).

**Traceability:**
- CT-ESO-2026-Q1, Section 2.1 — asserts "no evidence of exploitation in the production environment"
- CT-EMAIL-2026-03, P. Westbrook / A. Torres, 9 March 2026 — customer non-notification decision based on no production exploitation evidence
- CT-EMAIL-2026-03, T. Osei, 8 March 2026 — confirms CloudTrail not enabled for API Gateway and Lambda
- CT-ESO-2026-Q1, Section 2.4 — CloudTrail gap rated High, open, targeted Q3 2026
- CT-IRP-001, Section 4.3 — forensic methodology relies on CloudTrail for data access/exfiltration determination
- CT-IRP-001, Section 6 — CloudTrail coverage limitation noted (text truncated, but corroborated by other documents)

> **Position:** The "no evidence of exploitation" conclusion should be formally retracted or re-qualified as "no exploitation detected within the limits of current logging coverage, which does not include API Gateway CloudTrail." Legal and the General Counsel should re-assess the customer notification and regulatory reporting decision in light of the actual forensic capability available. This position should be documented in INC-2026-047 before that incident record is finalised or shared with auditors.

---

### F-03 — Change Management Control Failures Contradict Security Architecture's Change Control Assertions; Three Unapproved Production Deployments During Audit Period — **High**

**Observation:**
CT-SEC-001 v2.1 (Section 3.4, Privileged Access and Segregation of Duties, and the change management sections) asserts that production changes follow a controlled, CAB-approved process and that separation of duties prevents unilateral production deployments.

CT-SOC1-FY2025 (Section 5, Exceptions) identifies three specific exceptions under the Change Management control objective for the period April 2025 to March 2026:
1. Three production deployments executed without CAB approval
2. Two emergency change post-implementation reviews completed late
3. Six change records missing UAT evidence (attributed to the ServiceNow migration period)

CT-ESO-2026-Q1 (Section 2.2) acknowledges these exceptions but characterises them as "control design compliance failures" with an automated gate targeted for September 2026. The executive framing presents this as a process gap being addressed, without surfacing the specific implication: the SOC 1 auditors identified that the stated control — CAB approval required before production deployment — was not operating effectively during the audit period. An automated gate does not exist yet; manual controls failed on at least three confirmed occasions.

The security architecture's change control assertions (CT-SEC-001 v2.1) present these controls as operating, when the SOC 1 evidence demonstrates they were not operating consistently. This creates a documentation integrity gap: anyone relying on the security architecture document as evidence of effective change control would receive a materially inaccurate picture.

There is a further specific risk: one of the three unapproved deployments may have been the v3.2.1-patch1 IDOR hotfix itself, deployed on 14 March 2026. The email correspondence (CT-EMAIL-2026-03, R. Chen, 8 March 2026) indicates the intent to deploy a targeted hotfix by 20 March 2026 on an expedited basis. The SOC 1 audit period runs to 31 March 2026. The documents do not explicitly confirm whether this deployment went through CAB, creating an unresolved question about whether the highest-priority security fix of the period was itself subject to the change control process it was meant to demonstrate.

**Why this matters:**
For a financial analytics platform relied upon by enterprise clients for ICFR purposes, change management controls are not incidental — they are a core SOC 1 control objective. User entities rely on ClearPath's change management to ensure that only authorised, tested code changes are deployed to the production environment processing their financial data. Three unapproved deployments represent a gap in this assurance. The SOC 1 report has been issued with exceptions noted, but the executive overview's framing as a "process and technical remediation" project understates the significance: until the automated gate is in place (September 2026), the manual control has demonstrated failure and there is no evidence of a detective compensating control in the interim.

**Traceability:**
- CT-SEC-001 v2.1, Section 3.4 — asserts controlled change management and separation of duties for production deployments
- CT-SOC1-FY2025, Section 5 — identifies three exceptions: three unapproved production deployments, two late emergency reviews, six missing UAT records
- CT-ESO-2026-Q1, Section 2.2 — acknowledges exceptions; characterises as process failure; automated gate targeted September 2026
- CT-EMAIL-2026-03, R. Chen, 8 March 2026 — expedited hotfix deployment proposed by 20 March 2026; CAB status not confirmed in available documents

> **Position:** The security architecture document (CT-SEC-001 v2.1) should be updated to accurately reflect that change management controls had three confirmed failures during FY2025 and that the automated enforcement gate is not yet operational. User entities relying on the SOC 1 report should be made aware through the standard SOC 1 exception disclosure that manual compensating controls remain in place until September 2026, and those compensating controls should be explicitly described.

---

### F-04 — Four Exploitable CVEs in Production Components Deferred to June 2026 with No Interim Compensating Controls Documented — **High**

**Observation:**
CT-SBOM-3.2.1 (Section 3, Notable Vulnerability Findings) identifies four CVEs assessed as "Exploitable" in the ClearPath FAP deployment context as of February 2026:

| CVE | Component | CVSS | Nature |
|---|---|---|---|
| CVE-2023-36240 | node-forge 1.3.1 | 8.1 High | RSA PKCS#1 padding oracle in integration-service certificate parsing |
| CVE-2023-45857 | axios 0.27.2 | 6.5 Med | Proxy-Auth header disclosure in integration-service outbound calls |
| CVE-2023-44271 | pillow 9.3.0 | 7.5 High | Resource exhaustion via crafted font files in report-service PDF generation |
| CVE-2023-32681 | requests 2.28.1 | 6.1 Med | Proxy-Auth header leak on redirect in api-service third-party calls |

All four are deferred to v3.2.2 (June 2026) with no interim compensating controls documented in the SBOM, the security architecture, or the executive overview.

CVE-2023-36240 (node-forge, CVSS 8.1) is of particular concern. A padding oracle vulnerability in RSA PKCS#1 operations within the integration-service could, in a worst-case scenario, be exploited to decrypt intercepted ciphertext or forge signatures — directly relevant to a platform that handles financial transaction data and authenticates via JWT tokens. CT-SBOM-3.2.1 states it is used for "certificate parsing" in integration-service, which handles OAuth 2.0 connections to third-party ERP systems. The SBOM provides no analysis of whether the code paths exercising this library are reachable from untrusted input in the integration-service's external-facing connectors.

CVE-2023-44271 (pillow, CVSS 7.5) represents a resource exhaustion risk in the report-service's PDF generation path. The report-service processes customer-uploaded data and generates reports on demand; if tenant-supplied data can influence font file processing in pillow, this could be used for denial of service against the report generation function.

CT-ESO-2026-Q1 does not mention any of these CVEs, creating an information gap between the technical evidence layer (SBOM) and the executive/board view.

**Why this matters:**
IT Operations, as the requesting unit, is responsible for understanding the residual risk posture of components currently running in production. The SBOM explicitly rates these as exploitable in context, not merely theoretical. A four-to-five month gap between identification and remediation, without documented compensating controls, represents an unverified risk window. The integration-service vulnerability (CVE-2023-36240, node-forge) is particularly material given the service's role in managing OAuth credentials for third-party ERP connections used by enterprise clients for financial reporting.

**Traceability:**
- CT-SBOM-3.2.1, Section 3 — rates CVE-2023-36240, CVE-2023-45857, CVE-2023-44271, CVE-2023-32681 as "Exploitable" in ClearPath FAP deployment context
- CT-SBOM-3.2.1, Section 5 (Remediation Plan) — all four deferred to v3.2.2 June 2026; no interim controls stated
- CT-ESO-2026-Q1 — does not reference these CVEs; executive and board have no visibility of this open risk
- CT-SEC-001 v2.1 — states WAF and network controls provide defence-in-depth but does not address library-level vulnerabilities in integration-service outbound paths, which are not fronted by WAF

> **Position:** For each of the four exploitable CVEs, ClearPath should document a specific interim compensating control or formally accept the residual risk at an appropriate authority level before the next IT Operations review cycle. For CVE-2023-36240 specifically, an assessment of whether the affected node-forge code path is reachable from untrusted external input should be completed and documented. These items should be included in the next executive security overview.

---

### F-05 — Password Maximum Length Cap Contradicts Platform's Own NIST SP 800-63B Commitment and Creates Documented Customer Harm — **Medium**

**Observation:**
CT-SEC-001 v2.1 (Section 2.2, NOTE) states: *"The maximum password length of 16 characters was introduced to maintain compatibility with the bcrypt implementation. This restriction is under review following customer feedback and security advisory NIST SP 800-63B."* The document therefore acknowledges that the current control does not meet the standard it cites.

CT-IG-001 v3.2 (Section 4.1) documents the max_password_length as fixed at 16 with a WARNING that it cannot be increased, and separately lists it as configurable only within the range 8–16.

CT-EMAIL-2026-03 (P. Westbrook, 9 March 2026) confirms that three enterprise customers in Q1 2026 reported that the 16-character maximum prevents use of their password managers, which generate longer passwords. A. Torres's response (truncated in the available text) was addressing the technical reason for the cap.

NIST SP 800-63B explicitly prohibits maximum password length restrictions below 64 characters and states that longer passwords should be permitted. CT-SEC-001 v2.1 cites this standard as relevant, making it a self-declared compliance gap rather than an externally imposed one.

The bcrypt justification stated in CT-SEC-001 v2.1 is technically unfounded: bcrypt accepts passwords of any length (truncating internally at 72 bytes, which accommodates passwords well beyond 16 characters). The documented rationale for the restriction does not withstand scrutiny, and the security architecture itself characterises it as under review — yet the installation guide presents it as a fixed, unmodifiable platform parameter with no caveat.

**Why this matters:**
A 16-character password maximum, in the context of a financial analytics platform used for ICFR purposes, is a control that actively works against password security by preventing the use of modern credential management tools. Three enterprise customers have already raised this as an operational issue. The inconsistency between the security architecture's acknowledgment of the NIST gap and the installation guide's presentation of it as a fixed design parameter means that customer IT administrators reading the installation guide have no indication that this is a known issue under remediation, potentially affecting their own security configuration decisions.

**Traceability:**
- CT-SEC-001 v2.1, Section 2.2 NOTE — acknowledges 16-char max is under review against NIST SP 800-63B
- CT-IG-001 v3.2, Section 4.1 — presents 16-char maximum as fixed platform parameter with no caveat
- CT-EMAIL-2026-03, P. Westbrook, 9 March 2026 — three enterprise customers directly affected in Q1 2026
- CT-ESO-2026-Q1, Section 3 — lists "Password policy: remove max 16-char limit" as Medium priority, v3.2.2 June 2026

> **Position:** The installation guide (CT-IG-001) should be updated to reflect that the 16-character maximum is a known limitation under active remediation, targeted for v3.2.2. The technical justification citing bcrypt compatibility should be removed from the security architecture as it is technically incorrect and creates a false impression that the restriction is architecturally necessary.

---

### F-06 — AES-128-CBC Used for Export ZIP Files Containing Customer Financial Data; Level 2 Classification Appears Circular — **Medium**

**Observation:**
CT-ENC-001 v1.5 (Section 3.2) states that export ZIP files containing customer financial data are classified as Level 2 (Internal) for encryption purposes, resulting in AES-128-CBC encryption rather than AES-256-GCM. The stated rationale is that these files are *"intended for transmission to the authorised customer organisation and are not permanently retained by ClearPath."*

The same section notes: *"A security advisory recommendation to upgrade to AES-256-GCM for all archive encryption is under review as part of the v3.3 encryption hardening roadmap (Jira: SEC-RD-031)."*

CT-ENC-001 v1.5 (Section 2, Data Classification) defines Level 3 as "Confidential (PII)" and Level 4 as "Restricted (Financial)" — both requiring AES-256-GCM. Customer financial report exports demonstrably contain Level 3 and Level 4 data: the penetration test report (CT-PTR-2025, PT-2025-003) confirms that successfully exported reports contained *"detailed financial statements including transaction histories, account balances, and entity names."* Transaction histories and account balances meet the Level 4 definition; entity names and associated data meet Level 3.

The classification of these files as Level 2 (Internal) because they are "intended for the authorised customer" is circular: the entire threat model for export files is that they may be intercepted in transit or stored insecurely by the customer before receipt. The data classification framework defines levels based on data sensitivity, not on the intended recipient. Reclassifying the container to Level 2 because it is addressed to the customer does not change the sensitivity of the financial data inside it.

Additionally, CT-ENC-001 v1.5 (Section 3.2) notes that the IV for AES-128-CBC is stored in the archive metadata file alongside the encrypted archive. Storing the IV alongside the ciphertext is standard practice, but combined with the use of CBC mode (which lacks authentication), this means that export ZIPs are vulnerable to padding oracle attacks and bit-flipping without detection — a known weakness of CBC mode that GCM mode would resolve.

**Why this matters:**
Customer financial reports are the primary sensitive output of the ClearPath platform. The encryption standard applied to them at the point of export is weaker than what the platform's own data classification framework would require if applied consistently to the data content rather than to the delivery intent. For IT Operations deploying or relying on ClearPath, this is material: customers may assume that exported financial reports carry the platform's highest encryption standard, when in fact they receive AES-128-CBC with no ciphertext authentication.

**Traceability:**
- CT-ENC-001 v1.5, Section 3.2 — classifies export ZIPs as Level 2, applies AES-128-CBC; IV stored in metadata
- CT-ENC-001 v1.5, Section 2 — Level 3 (PII) and Level 4 (Financial) require AES-256-GCM
- CT-PTR-2025, PT-2025-003 — confirms exported reports contain transaction histories, account balances, entity names — Level 3/4 data by the platform's own definitions
- CT-ESO-2026-Q1, Section 2.4 — lists "AES-128-CBC used for backup archives (not AES-256)" as Low-Medium risk, v3.3 Q4 2026

> **Position:** The Level 2 classification applied to export ZIP files should be formally reviewed and justified against the data classification definitions in CT-ENC-001 v1.5 Section 2, with specific reference to the data content confirmed by the penetration test. The risk acceptance for AES-128-CBC should be signed off at an appropriate authority level and disclosed in customer-facing security documentation, rather than addressed solely through an internal roadmap item.

---

### F-07 — MFA Not Enforced by Platform Default; Installation Guide and Security Architecture Inconsistently Characterise Customer Responsibility — **Medium**

**Observation:**
CT-SEC-001 v2.1 (Section 2.3) states MFA enrollment is "optional by default" and that tenant administrators may enforce it for their organisation.

CT-IG-001 v3.2 (Section 4.1) confirms `mfa_required` defaults to `false` and lists enabling MFA as a configurable parameter. Section 6 (Security Hardening Recommendations) lists SH-01 (Enable MFA enforcement) as "Critical" priority — but as a recommendation, not a requirement.

CT-SOC1-FY2025 documents this as a Complementary User Entity Control (CUEC): CUEC-05 or equivalent places responsibility on user entities (customers) to enforce MFA within their tenant.

CT-ESO-2026-Q1 (Section 2.4) lists "MFA not enforced by default for tenant organisations" and characterises it as "Medium – CUEC; customer responsible for enforcement," with the remediation action listed as "Customer hardening guide" rather than a platform change.

The inconsistency is between: (a) the installation guide presenting MFA enforcement as a Critical security hardening recommendation, implying customers who do not follow it are taking a significant risk; and (b) the executive and SOC 1 framing that characterises MFA non-enforcement as the customer's CUEC responsibility, which deflects the platform's accountability. There is no mechanism in the platform that alerts tenant administrators when MFA is disabled, nor any platform-level minimum MFA enforcement for high-privilege roles (e.g., Tenant Admin, Finance Manager). The SOC 1 report's CUEC framing means that if a customer suffers account compromise due to no MFA, ClearPath's control framework treats this as outside scope.

Furthermore, CT-IG-001 v3.2 (Section 4.2) notes that when SSO is used, MFA enforcement is *"deferred to the IdP"* and *"ClearPath does not apply additional MFA when SSO is the authentication method."* For customers who have configured SSO but whose IdP does not enforce MFA, the platform provides no fallback enforcement. This is not surfaced as a risk in the executive overview.

**Why this matters:**
For IT Operations at customer organisations, the distinction between "we recommend you enable MFA" and "we require MFA" is operationally significant. A Finance Manager account with no MFA, on a platform processing financial statements used for ICFR, represents a credential compromise risk that the platform's own installation guide rates as Critical. The CUEC framing in the SOC 1 report means that customers must read that document carefully to understand that MFA enforcement is their responsibility — a disclosure that is unlikely to be surfaced during standard onboarding.

**Traceability:**
- CT-IG-001 v3.2, Section 4.1 — mfa_required defaults to false; Section 6 rates MFA enablement as Critical priority recommendation
- CT-SEC-001 v2.1, Section 2.3 — MFA optional by default; tenant admin can enforce
- CT-SOC1-FY2025 — MFA enforcement documented as CUEC (customer responsibility)
- CT-ESO-2026-Q1, Section 2.4 — remediation is "Customer hardening guide," not platform change
- CT-IG-001 v3.2, Section 4.2 — SSO path defers MFA entirely to IdP with no platform fallback

> **Position:** ClearPath should implement and document a minimum MFA enforcement requirement for privileged roles (Tenant Admin