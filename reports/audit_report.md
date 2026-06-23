# IAM Access Risk Audit Report
**Prepared by:** Senior IAM & GRC Security Auditor
**Classification:** Confidential – Internal Audit Use Only
**Review Scope:** Automated Access Review – Identity & Access Management Controls

---

## Executive Summary

The following findings were identified during an automated access review of current system account records. Four (4) access risk findings were detected across the Finance and Human Resources departments, ranging in severity from Critical to Medium. These findings indicate deficiencies in access lifecycle management controls, including inadequate offboarding procedures, excessive privilege provisioning for non-permanent staff, and insufficient dormant account management policies. Immediate remediation is required for Critical and High findings, with timely action required for Medium findings to reduce residual risk exposure.

---

## Detailed Findings

---

### FINDING: [CRITICAL] – mgarcia

**RISK:**
User account `mgarcia`, classified as an Analyst within the Finance Department, has been identified as a terminated employee whose system record and access credentials remain active within the environment. The continued existence of an active account belonging to a former employee represents a critical identity lifecycle management failure. Terminated users no longer have a legitimate business need for system access, and their credentials — if unrevoked — can be exploited either by the former employee themselves or by a malicious third party who may have obtained the credentials. The Finance Department's exposure is particularly significant given the sensitivity of financial data, including payment records, general ledger access, and potentially regulated customer financial information.

**IMPACT:**
The business impact of this finding is severe. An active terminated user account creates a direct pathway for unauthorized access to financial systems, which could result in data exfiltration, fraudulent transactions, or deliberate manipulation of financial records. From a compliance perspective, this finding constitutes a violation of mandatory access control requirements across multiple regulatory frameworks. Regulated industries, including banking and healthcare, are required to immediately revoke access upon employee termination. Failure to do so exposes the organization to regulatory penalties, audit findings, and potential breach liability. This finding also undermines the integrity of the organization's access certification process, as the account should have been flagged and disabled at the point of offboarding.

**REMEDIATION:**
1. **Immediate Action (within 24 hours):** Disable and lock the `mgarcia` account across all connected systems, applications, and directories, including Active Directory, SSO platforms, VPN, and any Finance-specific applications.
2. **Credential Revocation:** Invalidate all associated API keys, tokens, certificates, and passwords tied to this account.
3. **Access Log Review:** Conduct a retroactive review of all authentication and activity logs for the `mgarcia` account from the date of termination to present to determine whether any unauthorized access occurred. Escalate to the Security Operations Center (SOC) if suspicious activity is identified.
4. **Process Review:** Conduct a root cause analysis of the offboarding workflow to determine why this account was not deprovisioned at termination. Implement automated account deactivation triggers integrated with the HR Information System (HRIS) to enforce same-day or next-business-day deprovisioning upon confirmed termination.
5. **Audit Sweep:** Perform an organization-wide audit of all active accounts to identify additional terminated users with residual access.

**FRAMEWORKS:**
- **NIST 800-53 Rev. 5:** AC-2 (Account Management) – Requires organizations to disable accounts upon termination and manage the information system account lifecycle; PS-4 (Personnel Termination) – Requires immediate revocation of access following employee termination.
- **PCI-DSS v4.0:** Requirement 7.2 – Access to system components must be appropriately defined and assigned; Requirement 8.3.4 – User accounts must be removed or disabled promptly upon termination.
- **SOC 2 (Trust Services Criteria):** CC6.2 – Logical access controls must include processes for removing access when no longer required; CC6.3 – Role-based access must be reviewed and revoked upon change in employment status.
- **HIPAA Security Rule:** 45 CFR §164.308(a)(3)(ii)(C) – Termination procedures must include revocation of access to electronic Protected Health Information (ePHI) upon employee departure.

---

### FINDING: [HIGH] – rlee

**RISK:**
User account `rlee`, identified as a Contractor within the Finance Department, has been found to hold Privileged access within the organization's systems. The provisioning of privileged-level access to a contractor represents a significant violation of the principle of least privilege and the broader principle of need-to-know access. Contractors are non-permanent, third-party personnel who, by nature of their engagement, should be provisioned with the minimum level of access necessary to perform their defined scope of work. Privileged access — which typically includes elevated system rights, administrative capabilities, or access to sensitive financial data and configurations — should be explicitly justified, time-limited, and subject to heightened oversight. No evidence of documented business justification or compensating controls for this elevated access level was identified in the access review.

**IMPACT:**
The assignment of privileged access to a contractor introduces substantial risk across several dimensions. Operationally, contractors with privileged access have the ability to modify system configurations, access sensitive financial records, or exfiltrate data without the same level of organizational accountability that applies to permanent employees. From an insider threat perspective, contractors present an elevated risk profile due to their limited organizational loyalty and the potential for simultaneous engagement with competing entities. Regulatorily, provisioning excessive access to third-party personnel without documented authorization and oversight constitutes a compliance gap under multiple frameworks governing financial and healthcare data security. In the event of a breach or audit, the absence of documented justification for this access level would be viewed as a systemic control deficiency.

**REMEDIATION:**
1. **Immediate Review (within 48 hours):** Conduct a formal access review with `rlee`'s sponsoring manager and the relevant contract owner to determine whether privileged access is operationally justified. If no valid business justification exists, immediately downgrade access to Standard level.
2. **Privilege Reduction:** If limited elevated access is genuinely required for specific tasks, apply Just-In-Time (JIT) privileged access management (PAM) principles — provisioning elevated rights only for defined maintenance windows or tasks, with automatic expiration.
3. **Formal Authorization:** Require documented and signed approval from the Finance Department Head and the Information Security team for any contractor holding privileged access. Store authorization records in the GRC system of record.
4. **Enhanced Monitoring:** Implement session monitoring and logging for all privileged activity performed under this account until access is remediated. Route logs to the SIEM for anomaly detection.
5. **Contractor Access Policy Review:** Review the organization's third-party access provisioning policy to ensure privileged access cannot be assigned to contractors without a mandatory approval workflow and time-bound access restrictions.

**FRAMEWORKS:**
- **NIST 800-53 Rev. 5:** AC-2 (Account Management) – Requires establishment of conditions for group and role membership; AC-6 (Least Privilege) – Requires that users are granted only the minimum access necessary; AC-17 (Remote Access) – Applies to contractor access governance; SA-9 (External System Services) – Governs the security requirements placed on third-party providers.
- **PCI-DSS v4.0:** Requirement 7.2 – Access to cardholder data environments must be restricted to individuals with a legitimate business need; Requirement 8.2.3 – Individual user IDs for third parties must be managed with appropriate access controls.
- **SOC 2 (Trust Services Criteria):** CC6.3 – Access is granted based on authorized roles with the principle of least privilege enforced; CC9.2 – Vendor and contractor access must be assessed for risk and managed accordingly.
- **HIPAA Security Rule:** 45 CFR §164.308(a)(4) – Information access management requires that access to ePHI be granted based on minimum necessary standards, including for business associates and contractors.

---

### FINDING: [MEDIUM] – tjones

**RISK:**
User account `tjones`, assigned to the Human Resources Department with a Manager-level role and Standard access, has been identified as a dormant account, with no recorded login activity for a period exceeding ninety (90) days. While the account has not been provisioned with privileged access, dormant accounts — regardless of access level — represent an exploitable attack surface within the identity environment. An account that has been inactive for an extended period may indicate that the user has transitioned roles, is on extended leave, or is no longer actively performing the functions for which access was originally granted. HR systems typically house highly sensitive employee personally identifiable information (PII), compensation data, disciplinary records, and potentially protected health information, making unmonitored access particularly concerning.

**IMPACT:**
Dormant accounts that are not subject to periodic review and deactivation represent a latent security risk. These accounts are frequently targeted in credential stuffing, brute force, and account takeover attacks precisely because they are less likely to be monitored and because legitimate users are unlikely to detect unauthorized access promptly. From a business perspective, unauthorized access to HR systems could result in the exposure of employee PII, creating regulatory liability under data protection laws. Furthermore, the existence of dormant accounts indicates a gap in the organization's access recertification cadence, which is a finding that will be noted in regulatory examinations and third-party audits as evidence of inadequate access governance.

**REMEDIATION:**
1. **Account Status Verification (within 5 business days):** Confirm with `tjones`'s direct supervisor and HR leadership whether the user is still actively employed in a capacity that requires system access.
2. **Suspension of Access:** If no active business need is confirmed, suspend the account pending formal review. If the user is confirmed active but access is no longer required for their current role, initiate deprovisioning.
3. **User Notification:** If the account belongs to an active employee, notify `tjones` and their manager to confirm the account's necessity and require re-authentication within a defined window.
4. **Automated Dormancy Controls:** Implement automated policies within the Identity Governance and Administration (IGA) platform to flag and disable accounts after 45–60 days of inactivity, with manager notification at the 30-day threshold.
5. **Access Recertification:** Include dormant account detection in the quarterly access recertification cycle to ensure timely identification and remediation of inactive accounts across all departments.

**FRAMEWORKS:**
- **NIST 800-53 Rev. 5:** AC-2 (Account Management) – Requires organizations to monitor system accounts and disable inactive accounts; IA-4 (Identifier Management) – Requires that identifiers for inactive accounts be managed and revoked where appropriate.
- **PCI-DSS v4.0:** Requirement 8.2.6 – Inactive user accounts must be removed or disabled within 90 days of inactivity.
- **SOC 2 (Trust Services Criteria):** CC6.2 – Logical access controls must include a process to remove or disable access that is no longer needed or used; CC6.6 – Access is reviewed on a periodic basis to confirm continued appropriateness.
- **HIPAA Security Rule:** 45 CFR §164.308(a)(3) – Workforce access management procedures must ensure that access to ePHI is reviewed and revoked when no longer appropriate.

---

### FINDING: [MEDIUM] – hkim

**RISK:**
User account `hkim`, assigned to the Finance Department with a Contractor role and Standard access level, has similarly been identified as a dormant account with no login activity recorded in excess of ninety (90) days. The dormancy of a contractor account carries additional risk implications beyond those associated with a permanent employee's inactive account. Contractor engagements are typically time-bound and scope-limited, meaning that a ninety-day period of inactivity may indicate that the contractor's engagement has concluded or their assigned work has been completed, and access should have been revoked at the end of the engagement period. The Finance Department context amplifies this concern, as access to financial systems — even at a standard level — may include visibility into sensitive financial transactions, reporting tools, and regulated data assets.

**IMPACT:**
An inactive contractor account that remains provisioned represents a compounded risk: the access was granted for a temporary, scoped purpose, yet it persists beyond the apparent conclusion of the engagement. This failure suggests a gap in the third-party access lifecycle management process, specifically in the deprovisioning controls that should be triggered at contract end or upon prolonged inactivity. From a compliance standpoint, this finding reinforces concerns about the organization's overall access governance maturity, particularly as it relates to third-party and vendor account management. In regulated industries, inadequate controls over contractor access lifecycles are a recurring theme in regulatory enforcement actions and can indicate systemic weaknesses in the access management program.

**REMEDIATION:**
1. **Immediate Contract Status Verification (within 5 business days):** Confirm with the contracting team and Finance Department whether `hkim`'s engagement is still active and whether the contractor requires continued system access.
2. **Account Suspension:** Suspend the `hkim` account immediately pending confirmation of active engagement. If the contractor's engagement has ended, proceed with full account deprovisioning and credential revocation.
3. **Access Log Review:** Review system access logs for the `hkim` account to confirm the nature and extent of access during the active period and verify no anomalous activity occurred during the inactive period.
4. **Contractor Offboarding Controls:** Establish automated deprovisioning workflows tied to contract end dates stored in the vendor management system. Accounts should be automatically disabled on the day the contract period expires, with escalation procedures for contract extensions.
5. **Third-Party Access Audit:** Conduct a comprehensive audit of all active contractor accounts within the Finance Department to identify additional instances of potentially outdated or unjustified access.

**FRAMEWORKS:**
- **NIST 800-53 Rev. 5:** AC-2 (Account Management) – Requires lifecycle management of accounts, including those associated with contractors and temporary personnel; PS-4 (Personnel Termination) and PS-5 (Personnel Transfer) – Applicable to contractor offboarding and access revocation upon contract conclusion; SA-9 (External System Services) – Governs controls placed on third-party service providers accessing organizational systems.
- **PCI-DSS v4.0:** Requirement 8.2.6 – Inactive accounts must be disabled within 90 days; Requirement 12.8 – Organizations must maintain policies to manage third-party service providers, including access governance.
- **SOC 2 (Trust Services Criteria):** CC6.2 – Logical access must be reviewed and removed when no longer required; CC9.2 – Vendor and contractor relationships must be assessed for associated risks, including access control risks.
- **HIPAA Security Rule:** 45 CFR §164.308(a)(4)(ii)(B) – Access authorization procedures must address the management of access for contractors and business associates; 45 CFR §164.308(a)(3)(ii)(C) – Termination procedures apply equally to contractors upon conclusion of their engagement.

---

## Summary Risk Register

| Finding | User | Department | Severity | Primary Risk | Immediate Action Required |
|---|---|---|---|---|---|
| Terminated User – Active Account | mgarcia | Finance | 🔴 Critical | Unauthorized post-termination access | Disable account within 24 hours |
| Contractor with Privileged Access | rlee | Finance | 🟠 High | Excessive privilege – third party | Access review and downgrade within 48 hours |
| Dormant Account – Employee | tjones | HR | 🟡 Medium | Inactive account – attack surface | Account review within 5 business days |
| Dormant Account – Contractor | hkim | Finance | 🟡 Medium | Inactive contractor account | Contract verification and suspension within 5 days |

---

## Auditor Recommendations – Systemic Controls

In addition to the individual finding remediations noted above, the auditor recommends the following systemic improvements to prevent recurrence:

1. **Integrate HRIS with IAM:** Establish automated, event-driven deprovisioning workflows that trigger account disablement upon HR status changes, including terminations and contract expirations.
2. **Implement an IGA Platform:** Deploy or mature an Identity Governance and Administration solution to automate access certifications, dormancy detection, and role-appropriate provisioning.
3. **Enforce Least Privilege for All Third Parties:** Establish a mandatory approval workflow for any contractor or vendor account provisioning that includes scope justification, time-limited access, and senior management sign-off.
4. **Conduct Quarterly Access Certifications:** Implement a formal, documented access recertification process conducted no less than quarterly, with results retained for audit purposes.
5. **Privileged Access Management (PAM):** Deploy a PAM solution to govern, monitor, and record all privileged access sessions, with particular controls around non-employee accounts.

---

*This report is intended for authorized personnel only. All findings should be remediated in accordance with the organization's risk management framework and escalated to the appropriate governance body where required.*