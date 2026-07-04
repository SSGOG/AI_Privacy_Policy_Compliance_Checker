"""
Built-in legal texts for GDPR and CCPA used as the RAG knowledge base.
Each article contains the article number, title, text, and key requirements.
"""

GDPR_ARTICLES = [
    {
        "id": "gdpr_art5_1a",
        "law": "GDPR",
        "article": "Article 5(1)(a)",
        "title": "Lawfulness, Fairness and Transparency",
        "text": (
            "Personal data shall be processed lawfully, fairly and in a transparent manner "
            "in relation to the data subject ('lawfulness, fairness and transparency')."
        ),
        "requirement": (
            "The privacy policy must clearly disclose the legal basis for processing personal data, "
            "must be written in plain language, and must not obscure or mislead the user about how "
            "their data is used."
        ),
    },
    {
        "id": "gdpr_art5_1b",
        "law": "GDPR",
        "article": "Article 5(1)(b)",
        "title": "Purpose Limitation",
        "text": (
            "Personal data shall be collected for specified, explicit and legitimate purposes and "
            "not further processed in a manner that is incompatible with those purposes."
        ),
        "requirement": (
            "The privacy policy must state the specific, explicit purposes for data collection. "
            "Data must not be used for undisclosed secondary purposes without a new legal basis."
        ),
    },
    {
        "id": "gdpr_art5_1c",
        "law": "GDPR",
        "article": "Article 5(1)(c)",
        "title": "Data Minimisation",
        "text": (
            "Personal data shall be adequate, relevant and limited to what is necessary in relation "
            "to the purposes for which they are processed ('data minimisation')."
        ),
        "requirement": (
            "The policy must confirm that only the minimum necessary data is collected. "
            "Collecting excessive or irrelevant data violates the data minimisation principle."
        ),
    },
    {
        "id": "gdpr_art5_1d",
        "law": "GDPR",
        "article": "Article 5(1)(d)",
        "title": "Accuracy",
        "text": (
            "Personal data shall be accurate and, where necessary, kept up to date; every "
            "reasonable step must be taken to ensure that personal data that are inaccurate, "
            "having regard to the purposes for which they are processed, are erased or rectified "
            "without delay ('accuracy')."
        ),
        "requirement": (
            "The policy must explain how the organisation ensures data accuracy and what "
            "mechanisms exist for users to correct inaccurate data."
        ),
    },
    {
        "id": "gdpr_art5_1e",
        "law": "GDPR",
        "article": "Article 5(1)(e)",
        "title": "Storage Limitation",
        "text": (
            "Personal data shall be kept in a form which permits identification of data subjects "
            "for no longer than is necessary for the purposes for which the personal data are "
            "processed ('storage limitation')."
        ),
        "requirement": (
            "The policy must specify data retention periods or the criteria used to determine how "
            "long data is kept. Indefinite retention without justification is non-compliant."
        ),
    },
    {
        "id": "gdpr_art5_1f",
        "law": "GDPR",
        "article": "Article 5(1)(f)",
        "title": "Integrity and Confidentiality",
        "text": (
            "Personal data shall be processed in a manner that ensures appropriate security of "
            "the personal data, including protection against unauthorised or unlawful processing "
            "and against accidental loss, destruction or damage, using appropriate technical or "
            "organisational measures ('integrity and confidentiality')."
        ),
        "requirement": (
            "The policy must describe the security measures used to protect personal data "
            "against unauthorised access, loss, or destruction."
        ),
    },
    {
        "id": "gdpr_art6",
        "law": "GDPR",
        "article": "Article 6",
        "title": "Lawfulness of Processing",
        "text": (
            "Processing shall be lawful only if and to the extent that at least one of the following "
            "applies: (a) consent of the data subject; (b) necessary for performance of a contract; "
            "(c) necessary for compliance with a legal obligation; (d) necessary to protect vital "
            "interests; (e) necessary for public interest; (f) necessary for legitimate interests."
        ),
        "requirement": (
            "The policy must clearly state which lawful basis applies to each processing activity. "
            "Vague references to 'legitimate interests' without explanation may be non-compliant."
        ),
    },
    {
        "id": "gdpr_art7",
        "law": "GDPR",
        "article": "Article 7",
        "title": "Conditions for Consent",
        "text": (
            "Where processing is based on consent, the controller shall be able to demonstrate that "
            "the data subject has consented to processing of his or her personal data. The request "
            "for consent shall be presented clearly distinguishable from other matters, in plain "
            "language. The data subject shall have the right to withdraw consent at any time."
        ),
        "requirement": (
            "The policy must explain how consent is obtained, how users can withdraw it, and that "
            "withdrawal does not affect prior processing. Bundled or pre-ticked consent is invalid."
        ),
    },
    {
        "id": "gdpr_art12",
        "law": "GDPR",
        "article": "Article 12",
        "title": "Transparent Information",
        "text": (
            "The controller shall take appropriate measures to provide any information referred to "
            "in Articles 13 and 14 and any communication under Articles 15 to 22 and 34 relating "
            "to processing to the data subject in a concise, transparent, intelligible and easily "
            "accessible form, using clear and plain language."
        ),
        "requirement": (
            "Privacy notices must be concise, transparent, intelligible, and in plain language. "
            "Overly complex, legal-jargon-heavy, or excessively long policies may violate this."
        ),
    },
    {
        "id": "gdpr_art13",
        "law": "GDPR",
        "article": "Article 13",
        "title": "Information to be Provided at Collection",
        "text": (
            "Where personal data relating to a data subject are collected from the data subject, "
            "the controller shall provide: the identity and contact details of the controller; "
            "the purposes and legal basis; the recipients or categories of recipients; "
            "data retention periods; and the existence of all data subject rights."
        ),
        "requirement": (
            "At the time of data collection, the privacy policy must disclose: controller identity "
            "and contact, purposes and legal basis, data recipients, retention periods, and user "
            "rights (access, rectification, erasure, portability, objection)."
        ),
    },
    {
        "id": "gdpr_art15",
        "law": "GDPR",
        "article": "Article 15",
        "title": "Right of Access",
        "text": (
            "The data subject shall have the right to obtain from the controller confirmation as "
            "to whether or not personal data concerning him or her are being processed, and, where "
            "that is the case, access to the personal data and information about the processing."
        ),
        "requirement": (
            "The policy must inform users of their right to access their personal data and explain "
            "how to exercise this right (e.g., submitting a Subject Access Request)."
        ),
    },
    {
        "id": "gdpr_art16",
        "law": "GDPR",
        "article": "Article 16",
        "title": "Right to Rectification",
        "text": (
            "The data subject shall have the right to obtain from the controller without undue "
            "delay the rectification of inaccurate personal data concerning him or her."
        ),
        "requirement": (
            "The policy must acknowledge the user's right to have inaccurate personal data corrected "
            "and must explain the procedure for submitting a correction request."
        ),
    },
    {
        "id": "gdpr_art17",
        "law": "GDPR",
        "article": "Article 17",
        "title": "Right to Erasure ('Right to be Forgotten')",
        "text": (
            "The data subject shall have the right to obtain from the controller the erasure of "
            "personal data concerning him or her without undue delay where: the data is no longer "
            "necessary; consent is withdrawn; there is no legitimate basis; or the data was "
            "unlawfully processed."
        ),
        "requirement": (
            "The policy must clearly state the user's right to request deletion of their data "
            "and under what circumstances this right applies or is limited."
        ),
    },
    {
        "id": "gdpr_art20",
        "law": "GDPR",
        "article": "Article 20",
        "title": "Right to Data Portability",
        "text": (
            "The data subject shall have the right to receive the personal data concerning him or "
            "her in a structured, commonly used and machine-readable format and have the right to "
            "transmit those data to another controller."
        ),
        "requirement": (
            "If processing is based on consent or contract and is automated, the policy must "
            "inform users of their right to receive and transfer their data in a portable format."
        ),
    },
    {
        "id": "gdpr_art21",
        "law": "GDPR",
        "article": "Article 21",
        "title": "Right to Object",
        "text": (
            "The data subject shall have the right to object, on grounds relating to his or her "
            "particular situation, at any time to processing of personal data concerning him or her "
            "which is based on legitimate interests or public interest, including profiling."
        ),
        "requirement": (
            "The policy must inform users of their right to object to processing, including "
            "direct marketing, and explain how to exercise this right."
        ),
    },
    {
        "id": "gdpr_art25",
        "law": "GDPR",
        "article": "Article 25",
        "title": "Data Protection by Design and Default",
        "text": (
            "The controller shall implement appropriate technical and organisational measures "
            "designed to implement the data-protection principles in an effective manner and to "
            "integrate the necessary safeguards into the processing."
        ),
        "requirement": (
            "The policy should reflect that privacy is built into systems by design, that only "
            "necessary data is collected by default, and that privacy-enhancing technologies are used."
        ),
    },
    {
        "id": "gdpr_art32",
        "law": "GDPR",
        "article": "Article 32",
        "title": "Security of Processing",
        "text": (
            "The controller and processor shall implement appropriate technical and organisational "
            "measures to ensure a level of security appropriate to the risk, including: "
            "pseudonymisation and encryption; the ability to ensure ongoing confidentiality, "
            "integrity, availability; and a process for regularly testing and evaluating measures."
        ),
        "requirement": (
            "The policy must describe the security measures protecting personal data, such as "
            "encryption, pseudonymisation, access controls, and regular security testing."
        ),
    },
    {
        "id": "gdpr_art33",
        "law": "GDPR",
        "article": "Article 33",
        "title": "Notification of Personal Data Breach",
        "text": (
            "In the case of a personal data breach, the controller shall without undue delay and, "
            "where feasible, not later than 72 hours after having become aware of it, notify the "
            "personal data breach to the supervisory authority."
        ),
        "requirement": (
            "The policy should describe the data breach notification procedure, including the "
            "72-hour notification timeline to supervisory authorities and communication to users."
        ),
    },
    {
        "id": "gdpr_art44",
        "law": "GDPR",
        "article": "Article 44",
        "title": "International Data Transfers",
        "text": (
            "Any transfer of personal data to a third country or an international organisation "
            "shall take place only if the controller and processor comply with the conditions "
            "laid down in Chapter V."
        ),
        "requirement": (
            "If data is transferred outside the EEA, the policy must disclose this and explain "
            "the safeguards in place (e.g., Standard Contractual Clauses, adequacy decisions)."
        ),
    },
]

CCPA_SECTIONS = [
    {
        "id": "ccpa_1798_100",
        "law": "CCPA",
        "article": "§ 1798.100",
        "title": "Right to Know About Personal Information Collected, Disclosed, or Sold",
        "text": (
            "A consumer shall have the right to request that a business that collects a consumer's "
            "personal information disclose to that consumer the categories and specific pieces of "
            "personal information the business has collected about the consumer."
        ),
        "requirement": (
            "The privacy policy must disclose the categories of personal information collected "
            "and explain how consumers can request access to their specific data."
        ),
    },
    {
        "id": "ccpa_1798_105",
        "law": "CCPA",
        "article": "§ 1798.105",
        "title": "Right to Delete Personal Information",
        "text": (
            "A consumer shall have the right to request that a business delete any personal "
            "information about the consumer which the business has collected from the consumer."
        ),
        "requirement": (
            "The policy must acknowledge the consumer's right to request deletion of their "
            "personal information and explain the procedure for submitting such a request."
        ),
    },
    {
        "id": "ccpa_1798_110",
        "law": "CCPA",
        "article": "§ 1798.110",
        "title": "Right to Know — Categories of Information",
        "text": (
            "A consumer shall have the right to request that a business that collects personal "
            "information about the consumer disclose to the consumer: the categories of personal "
            "information collected; the categories of sources; the business purpose; the categories "
            "of third parties with whom shared."
        ),
        "requirement": (
            "The policy must list the categories of personal information collected, the sources "
            "of collection, the business or commercial purposes, and categories of third-party "
            "recipients."
        ),
    },
    {
        "id": "ccpa_1798_115",
        "law": "CCPA",
        "article": "§ 1798.115",
        "title": "Right to Know — Information Sold or Disclosed",
        "text": (
            "A consumer shall have the right to request that a business that sells personal "
            "information, or that discloses it for a business purpose, disclose to that consumer "
            "the categories of personal information that the business sold and the categories of "
            "third parties to whom the personal information was sold."
        ),
        "requirement": (
            "If the business sells personal information, the policy must disclose the categories "
            "of data sold and the categories of third parties to whom it is sold."
        ),
    },
    {
        "id": "ccpa_1798_120",
        "law": "CCPA",
        "article": "§ 1798.120",
        "title": "Right to Opt-Out of Sale of Personal Information",
        "text": (
            "A consumer shall have the right, at any time, to direct a business that sells personal "
            "information about the consumer to third parties not to sell the consumer's personal "
            "information. This right may be referred to as the right to opt-out."
        ),
        "requirement": (
            "If the business sells personal information, the policy must include a clear 'Do Not "
            "Sell My Personal Information' link and explain how consumers can exercise this right."
        ),
    },
    {
        "id": "ccpa_1798_121",
        "law": "CCPA",
        "article": "§ 1798.121",
        "title": "Right to Limit Use of Sensitive Personal Information",
        "text": (
            "A consumer shall have the right, at any time, to direct a business that collects "
            "sensitive personal information about the consumer to limit its use of the consumer's "
            "sensitive personal information to that use which is necessary to perform the services "
            "or provide the goods reasonably expected by an average consumer."
        ),
        "requirement": (
            "If sensitive personal information (e.g., health, financial, biometric, precise "
            "geolocation) is collected, the policy must explain the consumer's right to limit its use."
        ),
    },
    {
        "id": "ccpa_1798_125",
        "law": "CCPA",
        "article": "§ 1798.125",
        "title": "Right to Non-Discrimination",
        "text": (
            "A business shall not discriminate against a consumer because the consumer exercised "
            "any of the consumer's rights under this title, including by denying goods or services, "
            "charging different prices, or providing a different quality of goods or services."
        ),
        "requirement": (
            "The policy must state that consumers will not be discriminated against for exercising "
            "their CCPA rights, including no denial of services or differential pricing."
        ),
    },
    {
        "id": "ccpa_1798_130",
        "law": "CCPA",
        "article": "§ 1798.130",
        "title": "Methods for Submitting Requests",
        "text": (
            "A business shall make available to consumers two or more designated methods for "
            "submitting requests for information, including, at a minimum, a toll-free telephone "
            "number, and if the business maintains an internet website, a website address."
        ),
        "requirement": (
            "The policy must provide at least two methods for consumers to submit rights requests, "
            "such as a toll-free number and a web form or email address."
        ),
    },
    {
        "id": "ccpa_1798_135",
        "law": "CCPA",
        "article": "§ 1798.135",
        "title": "Privacy Policy Requirements",
        "text": (
            "A business that is required to comply with this title shall, at or before the point "
            "of collection, inform consumers as to the categories of personal information to be "
            "collected and the purposes for which the categories of personal information shall "
            "be used."
        ),
        "requirement": (
            "The policy must inform consumers at or before data collection about the categories "
            "of personal information collected and the purposes for each category."
        ),
    },
    {
        "id": "ccpa_1798_140_sensitive",
        "law": "CCPA",
        "article": "§ 1798.140(ae)",
        "title": "Sensitive Personal Information Definition",
        "text": (
            "Sensitive personal information means personal information that reveals a consumer's "
            "social security number, driver's license number, financial account information, "
            "precise geolocation, racial or ethnic origin, religious beliefs, health information, "
            "biometric data, sexual orientation, or contents of personal communications."
        ),
        "requirement": (
            "The policy must separately identify and disclose when sensitive personal information "
            "is collected and must explain the specific purposes for which it is used."
        ),
    },
    {
        "id": "ccpa_1798_106",
        "law": "CCPA",
        "article": "§ 1798.106",
        "title": "Right to Correct Inaccurate Personal Information",
        "text": (
            "A consumer shall have the right to request a business that maintains inaccurate "
            "personal information about the consumer to correct that inaccurate personal "
            "information, taking into account the nature of the personal information and the "
            "purposes of the processing of the personal information."
        ),
        "requirement": (
            "The policy must acknowledge the consumer's right to request correction of inaccurate "
            "personal information and must explain how to submit a correction request."
        ),
    },
    {
        "id": "ccpa_1798_150",
        "law": "CCPA",
        "article": "§ 1798.150",
        "title": "Civil Actions — Data Security",
        "text": (
            "Any consumer whose nonencrypted and nonredacted personal information is subject to "
            "an unauthorized access and exfiltration, theft, or disclosure as a result of the "
            "business's violation of the duty to implement and maintain reasonable security "
            "procedures and practices may institute a civil action."
        ),
        "requirement": (
            "The policy must describe the security measures in place to protect personal "
            "information from unauthorised access, breach, or theft."
        ),
    },
]

# Combine all articles
ALL_LEGAL_TEXTS = GDPR_ARTICLES + CCPA_SECTIONS

# Law-to-articles mapping
LAW_ARTICLES = {
    "GDPR": GDPR_ARTICLES,
    "CCPA": CCPA_SECTIONS,
}

# Compliance hypothesis templates per law
COMPLIANCE_TEMPLATES = {
    "GDPR": {
        "fully_compliant": (
            "This clause fully satisfies GDPR data protection requirements by explicitly "
            "addressing the applicable obligation."
        ),
        "partially_compliant": (
            "This clause partially addresses GDPR requirements but is incomplete or vague "
            "about some important aspects."
        ),
        "non_compliant": (
            "This clause fails to meet GDPR requirements, is missing required information, "
            "or contradicts data protection obligations."
        ),
    },
    "CCPA": {
        "fully_compliant": (
            "This clause fully satisfies CCPA consumer privacy rights requirements."
        ),
        "partially_compliant": (
            "This clause partially addresses CCPA requirements but omits important disclosures "
            "or procedures."
        ),
        "non_compliant": (
            "This clause fails to meet CCPA requirements or is missing required consumer "
            "rights disclosures."
        ),
    },
}
