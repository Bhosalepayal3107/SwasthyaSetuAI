"""
scheme_catalogue.py - SwasthyaSetu AI
Structured catalogue of verified Indian government healthcare schemes and
a transparent, rule-based recommendation engine.
"""

from typing import Dict, List, Any

# Structured catalog of verified government healthcare programmes
SCHEME_CATALOGUE: List[Dict[str, Any]] = [
    {
        "id": "pmjay",
        "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        "govt_level": "Central Government",
        "state_availability": "All-India (33 States & UTs with partnering SHAs)",
        "category": "Tertiary & Secondary Inpatient Care",
        "scheme_type": "Health Assurance / Hospitalization Cover",
        "color": "blue",
        "tag": "PM-JAY",
        "description": "World's largest government-funded health assurance scheme providing comprehensive cashless hospitalization cover to vulnerable families.",
        "intended_beneficiaries": "Poor and vulnerable families identified based on Socio-Economic Caste Census (SECC 2011) rural/urban deprivation criteria, eligible ration card holders, and state-expanded beneficiary lists.",
        "verified_eligibility_conditions": [
            "Family listed in SECC 2011 database under eligible deprivation categories, OR",
            "Hold active NFSA / Priority Household (PHH) / Antyodaya (AAY) ration card recognized by state authority",
            "No restriction on family size, age, or gender",
            "Treatment must be availed at an empanelled public or private hospital (EHCP)"
        ],
        "covered_treatment": "Secondary and tertiary care hospitalization covering 1,949+ medical procedures across 27 specialties including cardiology, oncology, neurosurgery, orthopedics, general surgery, and emergency care. Includes 3 days pre-hospitalization and 15 days post-hospitalization medicines/diagnostics.",
        "benefit_info": "Cashless and paperless inpatient coverage of up to ₹5,00,000 per family per year on a floater basis across 30,000+ empanelled hospitals pan-India.",
        "required_documents": [
            "Aadhaar card or recognized identity document",
            "Ration card (AAY / PHH / valid state card) or PM-JAY Family ID",
            "Hospital admission slip / doctor's recommendation"
        ],
        "application_process": "No separate registration fee. Visit any empanelled hospital and approach the 'Ayushman Mitra' kiosk with your Aadhaar and Ration Card for instant biometric e-KYC and beneficiary card issuance.",
        "official_website": "https://pmjay.gov.in/",
        "source_of_rules": "National Health Authority (NHA), Ministry of Health and Family Welfare (MoHFW), Govt of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "vay_vandana",
        "name": "Ayushman Vay Vandana (PM-JAY Senior Citizen 70+ Universal Cover)",
        "govt_level": "Central Government",
        "state_availability": "All-India",
        "category": "Universal Senior Healthcare",
        "scheme_type": "Universal Senior Health Cover",
        "color": "purple",
        "tag": "VAY VANDANA",
        "description": "Universal health cover for all senior citizens aged 70 years and above, irrespective of family income or economic status.",
        "intended_beneficiaries": "All Indian citizens aged 70 years and above residing in states implementing AB PM-JAY.",
        "verified_eligibility_conditions": [
            "Applicant or patient must be 70 years of age or older (verified via Aadhaar date of birth)",
            "Universal coverage: No income ceiling, no ration card classification barrier",
            "Seniors already covered under family PM-JAY receive an additional top-up of ₹5 Lakh exclusively for themselves",
            "Seniors with private insurance or ESIC/CGHS can opt for Ayushman Vay Vandana card"
        ],
        "covered_treatment": "Comprehensive secondary and tertiary inpatient hospitalization, chronic age-related surgeries, joint replacements, cardiovascular treatments, oncology, and ICU care under the PM-JAY national package list.",
        "benefit_info": "Distinct health cover of up to ₹5,00,000 per year per eligible senior citizen on an individual basis (shared between couples if both are 70+). Cashless across empanelled hospitals.",
        "required_documents": [
            "Aadhaar card with verified date of birth showing age 70+",
            "Active mobile number linked to Aadhaar (for OTP e-KYC)"
        ],
        "application_process": "Self-enrollment available online on the NHA Beneficiary Portal (beneficiary.nha.gov.in) or Ayushman App using Aadhaar e-KYC, or visit any PM-JAY empanelled hospital kiosk.",
        "official_website": "https://beneficiary.nha.gov.in/",
        "source_of_rules": "Union Cabinet Expansion Decision / National Health Authority (NHA) Guidelines (Sep 2024)",
        "last_verified_date": "October 2024"
    },
    {
        "id": "mjpjay",
        "name": "Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY)",
        "govt_level": "State Government (Maharashtra)",
        "state_availability": "Maharashtra",
        "category": "Comprehensive State Health Assurance",
        "scheme_type": "State Health Insurance / Assurance",
        "color": "green",
        "tag": "MJPJAY",
        "description": "Maharashtra State flagship health insurance scheme providing cashless tertiary and secondary hospital treatment to state residents.",
        "intended_beneficiaries": "All families holding valid ration cards (Yellow, Orange/Kesari, White) or domicile certificate in Maharashtra, white ration card holders, and farmers from agrarian distress districts.",
        "verified_eligibility_conditions": [
            "Resident / domiciled in the State of Maharashtra",
            "Possession of valid Yellow, Kesari (Orange), White Ration Card, or Annapurna card issued by Govt of Maharashtra",
            "Universalized in Maharashtra: All valid ration-card holding families are covered under the expanded umbrella",
            "Treatment must be taken in empanelled network hospitals in Maharashtra"
        ],
        "covered_treatment": "1,356 medical and surgical procedures across 34 identified specialized categories including heart surgeries, cancer surgery/chemotherapy/radiotherapy, kidney transplantation & dialysis, neurosurgery, orthopedic joint surgeries, and pediatric surgeries.",
        "benefit_info": "Cashless hospitalization coverage of up to ₹5,00,000 per family per year on a family floater basis across 1,000+ empanelled hospitals in Maharashtra.",
        "required_documents": [
            "Valid Maharashtra Ration Card (Yellow, Orange, or White)",
            "Aadhaar card or voter ID for each family member",
            "Doctor's referral / diagnosis papers from treating hospital"
        ],
        "application_process": "Direct cashless facilitation at hospital. Visit the 'Arogyamitra' helpdesk at any MJPJAY empanelled government or private network hospital in Maharashtra.",
        "official_website": "https://www.jeevandayee.gov.in/",
        "source_of_rules": "State Health Assurance Society (SHAS), Public Health Department, Government of Maharashtra",
        "last_verified_date": "October 2024"
    },
    {
        "id": "ran",
        "name": "Rashtriya Arogya Nidhi (RAN)",
        "govt_level": "Central Government",
        "state_availability": "All-India",
        "category": "Critical Illness Financial Grant",
        "scheme_type": "Direct One-Time Financial Assistance Grant",
        "color": "orange",
        "tag": "RAN",
        "description": "Central government grant providing one-time financial assistance to poor patients suffering from major life-threatening diseases for treatment at government super-specialty hospitals.",
        "intended_beneficiaries": "Patients living Below the Poverty Line (BPL) suffering from life-threatening diseases requiring expensive super-specialty hospitalization.",
        "verified_eligibility_conditions": [
            "Patient family must be living Below Poverty Line (verified BPL card or valid family income certificate)",
            "Treatment must be taken strictly at designated Central/State Government Super Specialty Hospitals or AIIMS institutes",
            "Patients receiving assistance from PM-JAY or any other reimbursement scheme are generally excluded, except for uncovered specialized life-threatening procedures exceeding PM-JAY ceilings",
            "Government employees, pensioners, and their dependents are NOT eligible"
        ],
        "covered_treatment": "Major life-threatening diseases in cardiology, neurosurgery, nephrology (including kidney transplant), oncology, orthopedics, and major organ failures.",
        "benefit_info": "One-time financial grant of up to ₹15,00,000 (and up to ₹50,00,000 for rare diseases under the National Rare Disease Policy component) transferred directly to the treating government hospital.",
        "required_documents": [
            "Income certificate / BPL ration card",
            "Aadhaar card / Identity proof",
            "Detailed treatment estimate signed by Medical Superintendent / Head of Dept of designated Government Hospital",
            "Standard RAN application form filled by the government hospital"
        ],
        "application_process": "Application must be certified and submitted through the Medical Superintendent of the designated Government Hospital/AIIMS to the Ministry of Health and Family Welfare (MoHFW), Nirman Bhawan, New Delhi.",
        "official_website": "https://mohfw.gov.in/",
        "source_of_rules": "Ministry of Health and Family Welfare (MoHFW), Government of India Guidelines",
        "last_verified_date": "October 2024"
    },
    {
        "id": "cghs",
        "name": "Central Government Health Scheme (CGHS)",
        "govt_level": "Central Government",
        "state_availability": "All-India (80+ CGHS Covered Cities)",
        "category": "Government Employee & Pensioner Healthcare",
        "scheme_type": "Contributory Comprehensive Healthcare Service",
        "color": "purple",
        "tag": "CGHS",
        "description": "Comprehensive healthcare facility for Central Government employees, pensioners, and their dependent family members.",
        "intended_beneficiaries": "All Central Government employees paid from Central Civil Estimates, Central Government pensioners, sitting/ex-MPs, freedom fighters, and other notified categories.",
        "verified_eligibility_conditions": [
            "Must be an active Central Government employee or retired Central Government pensioner",
            "Must hold a valid CGHS Plastic Card with unique beneficiary ID",
            "Dependents must meet central government dependency criteria (unemployed/income below threshold)",
            "Residing in or receiving treatment in a CGHS covered city"
        ],
        "covered_treatment": "All outpatient consultation at Wellness Centres, specialist consultations, diagnostic tests, medicines, emergency hospitalization, and indoor treatment at government and empanelled private hospitals across India.",
        "benefit_info": "Comprehensive cashless inpatient treatment at empanelled private hospitals for pensioners and subsidized package rates for serving employees, plus free medicines through wellness centres.",
        "required_documents": [
            "CGHS Plastic Card / Beneficiary ID",
            "Pension Payment Order (PPO) or Employee Pay Slip",
            "Doctor prescription from CGHS Wellness Centre or empanelled specialist"
        ],
        "application_process": "Apply through the official CGHS portal (cghs.nic.in / cghs.mohfw.gov.in) through the respective Central Government department or Pensioners Association.",
        "official_website": "https://cghs.mohfw.gov.in/",
        "source_of_rules": "Directorate General of Central Government Health Scheme, MoHFW",
        "last_verified_date": "October 2024"
    },
    {
        "id": "esic",
        "name": "Employees' State Insurance Scheme (ESIC)",
        "govt_level": "Central Government / Statutory",
        "state_availability": "All-India (Notified Industrial Districts)",
        "category": "Organized Sector Social Security",
        "scheme_type": "Social Security & Occupational Health Cover",
        "color": "blue",
        "tag": "ESIC",
        "description": "Comprehensive social security and health protection scheme for organized workforce earning within statutory wage limits.",
        "intended_beneficiaries": "Employees working in non-seasonal factories and establishments with 10 or more employees whose monthly wage does not exceed ₹21,000 (₹25,000 for persons with disabilities).",
        "verified_eligibility_conditions": [
            "Must be an Insured Person (IP) registered under ESI Act, 1948",
            "Monthly wages within ₹21,000/month (₹25,000 for PwD)",
            "Employer and employee mandatory contribution must be deposited as per contribution periods",
            "Dependents (spouse, children up to 25 yrs, dependent parents) covered for medical benefit"
        ],
        "covered_treatment": "Full medical care including outpatient, inpatient, specialist consultations, diagnostic investigations, maternity care, super-specialty treatment (tie-up hospitals), sickness cash benefits, and disablement benefit.",
        "benefit_info": "Unlimited cashless medical care for insured person and family from day one of insurable employment, with no upper expenditure ceiling.",
        "required_documents": [
            "ESIC Pehchan Card / e-Pehchan card with IP number",
            "Aadhaar card of insured person and dependents",
            "Hospital referral from ESIC Dispensary/Hospital"
        ],
        "application_process": "Employer registers employee on the ESIC portal upon joining service. Beneficiary visits local ESI Dispensary / Hospital with e-Pehchan card.",
        "official_website": "https://www.esic.gov.in/",
        "source_of_rules": "Employees' State Insurance Corporation, Ministry of Labour and Employment, Govt of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "pmmvy",
        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "govt_level": "Central Government (Centrally Sponsored)",
        "state_availability": "All-India",
        "category": "Maternity Cash Benefit",
        "scheme_type": "Direct Benefit Transfer (DBT) Cash Incentive",
        "color": "pink",
        "tag": "PMMVY",
        "description": "Direct cash incentive for pregnant women and lactating mothers for wage compensation, rest, and nutritional support.",
        "intended_beneficiaries": "Pregnant women and lactating mothers (PW&LM) belonging to socially and economically disadvantaged sections for the first child, and for the second child if it is a girl child.",
        "verified_eligibility_conditions": [
            "Mother must be aged 19 years or older at the time of pregnancy",
            "Belongs to priority categories: BPL / NFSA ration card holders, e-Shram card holders, SC/ST, women with disabilities (40%+), PM-JAY beneficiaries, or family income below ₹8 lakh/year",
            "Women in regular employment with Central/State Govt or PSUs are NOT eligible",
            "Must register pregnancy at nearest Anganwadi Centre / ASHA worker"
        ],
        "covered_treatment": "Direct cash support to compensate for wage loss, ensure nutrition during pregnancy, and promote institutional delivery and child immunizations.",
        "benefit_info": "Cash incentive of ₹5,000 in two installments for the first child, and ₹6,000 in a single installment for the second child if female, transferred directly to the mother's Aadhaar-seeded bank account.",
        "required_documents": [
            "Mother and husband's Aadhaar cards",
            "Mother and Child Protection (MCP) card issued by Health Dept",
            "Mother's Aadhaar-seeded individual bank passbook",
            "Eligibility certificate (Ration card / e-Shram / income proof / caste certificate)"
        ],
        "application_process": "Apply online at pmmvy.wcd.gov.in or offline through the local Anganwadi Centre or approved government health facility.",
        "official_website": "https://pmmvy.wcd.gov.in/",
        "source_of_rules": "Ministry of Women and Child Development, Government of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "jsy_jssk",
        "name": "Janani Suraksha Yojana & Janani Shishu Suraksha Karyakram (JSY / JSSK)",
        "govt_level": "Central Government / NHM",
        "state_availability": "All-India",
        "category": "Maternity & Infant Public Hospital Care",
        "scheme_type": "Free Institutional Delivery & Cash Incentive",
        "color": "green",
        "tag": "JSY-JSSK",
        "description": "Safe motherhood intervention under National Health Mission promoting institutional delivery with completely cashless hospital care and cash assistance.",
        "intended_beneficiaries": "All pregnant women delivering in public health facilities and accredited private institutions, and sick infants up to 1 year of age.",
        "verified_eligibility_conditions": [
            "Pregnant women delivering at government hospitals (PHC/CHC/District Hospital) or accredited private institutions",
            "Universal entitlement for cashless delivery under JSSK regardless of income",
            "JSY cash assistance available for BPL/SC/ST and rural women delivering institutionally"
        ],
        "covered_treatment": "Completely free normal delivery and Caesarean section, free drugs and consumables, free essential diagnostics (blood, urine, ultrasound), free food during stay, free blood transfusion, and free transport from home to hospital and back.",
        "benefit_info": "100% cashless delivery with zero out-of-pocket expenses + JSY cash assistance of ₹1,000 to ₹1,400 (rural) or ₹1,000 (urban) directly to the mother.",
        "required_documents": [
            "Aadhaar card or voter ID",
            "Mother and Child Protection (MCP) card",
            "Bank passbook details of the mother"
        ],
        "application_process": "Approach your nearest ASHA worker, ANM, Primary Health Centre (PHC), Community Health Centre (CHC), or Government Sub-District/District Hospital upon onset of pregnancy.",
        "official_website": "https://nhm.gov.in/",
        "source_of_rules": "National Health Mission, MoHFW, Govt of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "rbsk",
        "name": "Rashtriya Bal Swasthya Karyakram (RBSK)",
        "govt_level": "Central Government / NHM",
        "state_availability": "All-India",
        "category": "Child Health & Early Intervention",
        "scheme_type": "Child Screening & Free Treatment Programme",
        "color": "mint",
        "tag": "RBSK",
        "description": "Comprehensive child health screening and early intervention services for 30 common health conditions from birth to 18 years.",
        "intended_beneficiaries": "All children aged 0 to 18 years enrolled in Anganwadi centres and Government/Government-aided schools.",
        "verified_eligibility_conditions": [
            "Child aged from birth up to 18 years",
            "Screened by dedicated Mobile Health Teams or diagnosed at government public health institutions",
            "No income ceiling for screening and corrective surgeries at District Early Intervention Centres (DEIC)"
        ],
        "covered_treatment": "30 identified health conditions categorized into 4 Ds: Defects at birth (congenital heart disease, cleft lip/palate, club foot, congenital cataracts), Deficiencies (anemia, vitamin deficiencies, severe acute malnutrition), Childhood Diseases (skin conditions, otitis media, rheumatic heart disease), and Developmental delays including disabilities.",
        "benefit_info": "Completely free diagnostic confirmation, specialized surgical corrections, physical therapy, assistive devices, and post-operative rehabilitation at tertiary care hospitals and DEIC centres.",
        "required_documents": [
            "Child's birth certificate or school ID card",
            "Parent's Aadhaar card / Ration card",
            "RBSK screening referral slip from School/Anganwadi Mobile Health Team"
        ],
        "application_process": "Screening happens directly at Anganwadi centres and schools. Parents can also directly take their child to the District Early Intervention Centre (DEIC) at the District Hospital.",
        "official_website": "https://nhm.gov.in/index1.php?lang=1&level=2&sublinkid=818&lid=221",
        "source_of_rules": "Child Health Division, Ministry of Health and Family Welfare, Govt of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "pmndp",
        "name": "Pradhan Mantri National Dialysis Programme (PMNDP)",
        "govt_level": "Central Government / NHM",
        "state_availability": "All-India (District Hospitals across 36 States/UTs)",
        "category": "Chronic Kidney Disease Support",
        "scheme_type": "Free & Subsidized Dialysis Services",
        "color": "orange",
        "tag": "PMNDP",
        "description": "National initiative under National Health Mission providing accessible and free/subsidized hemodialysis and peritoneal dialysis services in district hospitals.",
        "intended_beneficiaries": "Patients suffering from End-Stage Renal Disease (ESRD) requiring regular life-sustaining hemodialysis or peritoneal dialysis.",
        "verified_eligibility_conditions": [
            "Patients diagnosed with Chronic Kidney Disease / End-Stage Renal Disease",
            "Below Poverty Line (BPL) families receive 100% FREE dialysis services",
            "Non-BPL patients receive dialysis at deeply subsidized government-negotiated rates",
            "Services availed at empanelled District Hospital Dialysis Centres"
        ],
        "covered_treatment": "Hemodialysis sessions, dialyzer consumables, routine lab investigations, erythropoietin injections as per state guidelines, and Peritoneal Dialysis support.",
        "benefit_info": "100% free hemodialysis sessions for BPL patients; heavily subsidized rates (typically ₹700–₹1,100 vs ₹2,500+ private) for non-BPL patients.",
        "required_documents": [
            "BPL Ration Card or State Income Certificate (for free service)",
            "Aadhaar card of patient",
            "Nephrologist prescription / Dialysis recommendation sheet with viral markers (HIV, HBsAg, HCV)"
        ],
        "application_process": "Visit the Dialysis Unit at the District Hospital or Sub-District Hospital with your nephrologist prescription and BPL/identity documents.",
        "official_website": "https://pmndp.mohfw.gov.in/",
        "source_of_rules": "National Health Mission, Ministry of Health and Family Welfare, Govt of India",
        "last_verified_date": "October 2024"
    },
    {
        "id": "pmbjp",
        "name": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)",
        "govt_level": "Central Government",
        "state_availability": "All-India (10,000+ Kendras)",
        "category": "Affordable Quality Generic Medicines",
        "scheme_type": "Affordable Pharmacy / Outpatient Support",
        "color": "mint",
        "tag": "PMBJP",
        "description": "Nationwide network of Kendras providing high-quality generic medicines, surgical items, and nutraceuticals at 50% to 90% lower prices than branded equivalents.",
        "intended_beneficiaries": "Universal access: Open to all citizens seeking affordable medicines, especially patients managing chronic conditions (diabetes, hypertension, cardiac care, thyroid).",
        "verified_eligibility_conditions": [
            "Universal: No income test, no ration card, no caste or category restriction",
            "Open to anyone with a valid medical prescription (for prescription drugs)",
            "Over-the-counter health items available directly"
        ],
        "covered_treatment": "2,046 generic medicines and 300 surgical equipment items covering cardiology, diabetes, anti-infectives, gastrointestinal, oncology, pain management, respiratory, and women's health.",
        "benefit_info": "Direct reduction of 50% to 90% in outpatient medicine bills without any paperwork or pre-authorization.",
        "required_documents": [
            "Doctor's medical prescription with generic or branded medicine names",
            "No identity card required to purchase medicines"
        ],
        "application_process": "Locate nearest Janaushadhi Kendra via 'Janaushadhi Sugam' mobile app or janaushadhi.gov.in and purchase prescribed medicines directly over the counter.",
        "official_website": "https://janaushadhi.gov.in/",
        "source_of_rules": "Pharmaceuticals & Medical Devices Bureau of India (PMBI), Ministry of Chemicals & Fertilizers",
        "last_verified_date": "October 2024"
    },
    {
        "id": "tele_manas",
        "name": "Tele-MANAS (National Tele Mental Health Programme)",
        "govt_level": "Central Government",
        "state_availability": "All-India (24x7 Toll-Free: 14416 / 1800-891-4416)",
        "category": "Mental Healthcare Support",
        "scheme_type": "Free 24x7 Digital Helpline & Counseling",
        "color": "blue",
        "tag": "TELE-MANAS",
        "description": "Comprehensive, 24/7, free tele-mental health service network across India providing immediate professional counseling and psychiatric support.",
        "intended_beneficiaries": "Any individual experiencing psychological distress, anxiety, depression, suicidal thoughts, stress, addiction, or psychiatric issues, as well as family caregivers.",
        "verified_eligibility_conditions": [
            "Universal: 100% free and confidential for all individuals in India",
            "Available in 20+ regional languages",
            "No paperwork, no registration, no financial criteria required"
        ],
        "covered_treatment": "Immediate psychological first aid, tele-counseling by trained mental health counselors, clinical psychiatric consultation, and physical linkage to District Mental Health Programmes (DMHP) or tertiary centers.",
        "benefit_info": "100% free confidential mental health support round-the-clock via phone and video referral.",
        "required_documents": [
            "No documents needed. Completely accessible via telephone."
        ],
        "application_process": "Dial toll-free short code 14416 or 1800-891-4416 from any mobile or landline anywhere in India.",
        "official_website": "https://telemanas.mohfw.gov.in/",
        "source_of_rules": "MoHFW & NIMHANS (National Institute of Mental Health and Neurosciences)",
        "last_verified_date": "October 2024"
    },
    {
        "id": "hmdg",
        "name": "Health Minister's Discretionary Grant (HMDG)",
        "govt_level": "Central Government",
        "state_availability": "All-India",
        "category": "Indigent Patient Financial Assistance",
        "scheme_type": "Direct One-Time Medical Financial Grant",
        "color": "orange",
        "tag": "HMDG",
        "description": "Discretionary financial assistance to poor patients suffering from serious ailments who are not covered under regular insurance or PM-JAY.",
        "intended_beneficiaries": "Poor and indigent patients with annual family income up to ₹1,50,000 who require specialized medical treatment in Government hospitals.",
        "verified_eligibility_conditions": [
            "Annual family income must not exceed ₹1,50,000 per annum (verified by revenue authority)",
            "Treatment must be taken in a Central / State Government Hospital",
            "Financial grant is not admissible if the patient is eligible under PM-JAY or reimbursement from other sources",
            "Government employees and their dependents are not eligible"
        ],
        "covered_treatment": "Major surgery, cancer care, heart surgery, renal transplantation, eye surgery, and critical illnesses requiring inpatient intervention.",
        "benefit_info": "One-time financial assistance of up to ₹1,25,000 (depending on hospital estimate) paid directly to the treating government hospital.",
        "required_documents": [
            "Income Certificate issued by Tehsildar / District Revenue Officer showing income ≤ ₹1.5 Lakh",
            "Aadhaar card / residence proof",
            "Application proforma signed by treating doctor and countersigned by Medical Superintendent of Government Hospital",
            "Detailed treatment estimate"
        ],
        "application_process": "Submit prescribed application form through the treating Government Hospital to the Ministry of Health and Family Welfare, Government of India.",
        "official_website": "https://mohfw.gov.in/",
        "source_of_rules": "Ministry of Health and Family Welfare, Government of India",
        "last_verified_date": "October 2024"
    }
]

# Compatibility aliases for home overview cards
for s in SCHEME_CATALOGUE:
    s.setdefault("url", s.get("official_website", ""))
    s.setdefault("summary", s.get("description", ""))


def recommend_schemes(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transparent, rule-based matching engine that evaluates a user's profile
    against official government healthcare scheme criteria.

    Returns an ordered list of matched schemes enriched with:
    - match_reasons: List of clear, human-readable explanations of why it matches
    - verification_needed: List of specific conditions still requiring confirmation
    - document_readiness: Summary of documents user has vs required
    - relevance_score: Sorting priority
    """
    matches: List[Dict[str, Any]] = []

    # Extract sanitized profile data
    beneficiary = profile.get("beneficiary", "myself")
    
    # Effective age of the patient receiving treatment
    try:
        if beneficiary == "myself":
            patient_age = int(profile.get("age", 0))
        else:
            patient_age = int(profile.get("patient_age") or profile.get("age") or 0)
    except (ValueError, TypeError):
        patient_age = 0

    state = (profile.get("state") or "").strip()
    is_maharashtra = (state.lower() == "maharashtra")
    
    income_bracket = profile.get("income", "")
    low_income = income_bracket in ["Below ₹1 lakh", "₹1 lakh–₹2.5 lakh"]
    mid_income = income_bracket in ["₹2.5 lakh–₹5 lakh"]
    high_income = income_bracket in ["₹5 lakh–₹10 lakh", "Above ₹10 lakh"]

    ration_card = profile.get("ration_card", "not_sure")
    ration_card_type = profile.get("ration_card_type", "")
    has_bpl_ration = ration_card == "yes" and any(k in ration_card_type.lower() for k in ["yellow", "aay", "antyodaya", "phh", "bpl", "orange", "kesari"])

    has_ayushman_card = profile.get("ayushman_card", "no") == "yes"
    has_mjpjay_card = profile.get("mjpjay_reg", "no") == "yes"
    
    is_govt_employee = profile.get("govt_employee", "no") == "yes"
    insurance_type = profile.get("other_insurance", "no_insurance")
    
    circumstances = profile.get("circumstances", [])
    if isinstance(circumstances, str):
        circumstances = [circumstances]

    has_disability = any("disability" in c.lower() for c in circumstances)
    is_bocw_worker = any("construction" in c.lower() or "bocw" in c.lower() for c in circumstances)
    is_eshram_holder = any("unorganized" in c.lower() or "e-shram" in c.lower() for c in circumstances)

    treatments = profile.get("treatments", [])
    if isinstance(treatments, str):
        treatments = [treatments]
    treatments_lower = [t.lower() for t in treatments]

    status = profile.get("treatment_status", "")
    hospital_type = profile.get("hospital_type", "")
    docs_status = profile.get("documents", {})

    # Evaluate each scheme in catalogue
    for scheme in SCHEME_CATALOGUE:
        scheme_id = scheme["id"]
        is_match = False
        reasons: List[str] = []
        verification: List[str] = []
        score = 0

        # -------------------------------------------------------------
        # 1. AYUSHMAN VAY VANDANA (Senior Citizen 70+)
        # -------------------------------------------------------------
        if scheme_id == "vay_vandana":
            if patient_age >= 70:
                is_match = True
                score = 95
                reasons.append(f"Patient is {patient_age} years old (meets the universal age criterion of 70+ years).")
                reasons.append("Universal coverage: No income, caste, or ration-card restrictions apply.")
                if has_ayushman_card:
                    reasons.append("Eligible for a distinct top-up cover of ₹5 Lakh exclusively for seniors.")
                verification.append("Aadhaar date of birth must confirm age 70 or above.")
                verification.append("Treatment must be received at an empanelled PM-JAY network hospital.")
            elif patient_age >= 65 and profile.get("dob"):
                # Borderline/close age
                reasons.append("Approaching senior eligibility threshold (age 70 required for Vay Vandana card).")
                verification.append("Verify exact date of birth on Aadhaar card.")

        # -------------------------------------------------------------
        # 2. AYUSHMAN BHARAT PM-JAY
        # -------------------------------------------------------------
        elif scheme_id == "pmjay":
            # PM-JAY covers tertiary & secondary care across India for eligible families
            if has_ayushman_card:
                is_match = True
                score = 92
                reasons.append("You indicated you already hold or have applied for an Ayushman Bharat health card.")
                reasons.append("Provides cashless hospitalization up to ₹5,00,000 per year per family.")
            elif has_bpl_ration or low_income or is_eshram_holder or is_bocw_worker:
                is_match = True
                score = 88
                reasons.append("Your household income or ration card profile matches vulnerable family benchmarks for PM-JAY.")
                if any(t in treatments_lower for t in ["general hospitalization", "surgery", "cancer treatment", "heart disease treatment", "kidney disease or dialysis", "accident and emergency care", "eye treatment"]):
                    reasons.append("The treatment required is covered under PM-JAY's 1,949+ inpatient procedure packages.")
                verification.append("Must verify inclusion in the SECC 2011 beneficiary list or state eligible ration database.")
                verification.append("Hospital must be empanelled with PM-JAY.")
            elif not high_income and not is_govt_employee:
                # Moderate possibility
                is_match = True
                score = 65
                reasons.append("General hospitalization assistance may be available if your family is listed in state-extended Ayushman databases.")
                verification.append("Check name on official beneficiary portal (beneficiary.nha.gov.in) with Aadhaar or Ration card.")

        # -------------------------------------------------------------
        # 3. MAHATMA JYOTIRAO PHULE JAN AROGYA YOJANA (MJPJAY)
        # -------------------------------------------------------------
        elif scheme_id == "mjpjay":
            if is_maharashtra:
                is_match = True
                score = 90
                reasons.append("You reside in Maharashtra, where MJPJAY provides universal coverage for all valid ration-card holders.")
                if ration_card == "yes":
                    reasons.append(f"Your {ration_card_type or 'Maharashtra'} ration card is eligible for cashless treatment up to ₹5 Lakh.")
                else:
                    reasons.append("Any valid ration card (Yellow, Orange, or White) or Maharashtra domicile certificate qualifies.")
                if any(t in treatments_lower for t in ["surgery", "cancer treatment", "heart disease treatment", "kidney disease or dialysis", "general hospitalization"]):
                    reasons.append("Required treatment specialty is covered under MJPJAY's 1,356 cashless procedure packages.")
                verification.append("Treatment must be taken at an empanelled network hospital in Maharashtra.")
                verification.append("Approach the hospital 'Arogyamitra' helpdesk with your ration card and Aadhaar.")
            else:
                # Outside Maharashtra
                verification.append("MJPJAY is restricted to residents and hospitals in Maharashtra.")

        # -------------------------------------------------------------
        # 4. RASHTRIYA AROGYA NIDHI (RAN)
        # -------------------------------------------------------------
        elif scheme_id == "ran":
            is_critical = any(t in treatments_lower for t in ["cancer treatment", "heart disease treatment", "kidney disease or dialysis", "surgery"])
            if (low_income or has_bpl_ration) and is_critical and not is_govt_employee:
                is_match = True
                score = 80
                reasons.append("Designed specifically for BPL patients facing life-threatening medical conditions with high costs.")
                reasons.append("Provides a direct one-time financial grant up to ₹15 Lakh for critical treatment.")
                verification.append("Patient family must produce a valid BPL card or official low-income certificate.")
                verification.append("Treatment must be availed strictly at designated Central/State Government Super Specialty Hospitals or AIIMS.")
                verification.append("Estimate and application must be verified by the Government Hospital Medical Superintendent.")

        # -------------------------------------------------------------
        # 5. CENTRAL GOVERNMENT HEALTH SCHEME (CGHS)
        # -------------------------------------------------------------
        elif scheme_id == "cghs":
            if is_govt_employee:
                is_match = True
                score = 96
                reasons.append("You indicated that the applicant or family member is a Central Government employee or pensioner.")
                reasons.append("Provides comprehensive cashless outpatient, diagnostic, and inpatient treatment.")
                verification.append("Must hold an active CGHS plastic card with beneficiary ID.")
                verification.append("Valid in 80+ notified CGHS cities at wellness centres and empanelled private hospitals.")
            else:
                # Excluded if not govt employee
                pass

        # -------------------------------------------------------------
        # 6. EMPLOYEES' STATE INSURANCE SCHEME (ESIC)
        # -------------------------------------------------------------
        elif scheme_id == "esic":
            if insurance_type == "Employer-provided insurance" or is_eshram_holder or low_income or mid_income:
                if not is_govt_employee:
                    is_match = True
                    score = 70
                    reasons.append("Relevant if employed in an organized factory, commercial establishment, or enterprise covered under ESI Act.")
                    reasons.append("Covers full medical treatment with no upper expenditure ceiling for insured person and dependents.")
                    verification.append("Requires registration as an Insured Person (IP) by the employer.")
                    verification.append("Monthly wage ceiling must be within ₹21,000 (₹25,000 for persons with disabilities).")

        # -------------------------------------------------------------
        # 7. PRADHAN MANTRI MATRU VANDANA YOJANA (PMMVY)
        # -------------------------------------------------------------
        elif scheme_id == "pmmvy":
            is_maternity = any("pregnancy" in t or "maternity" in t for t in treatments_lower)
            if is_maternity or (beneficiary in ["myself", "wife"] and patient_age >= 18 and patient_age <= 45 and is_maternity):
                is_match = True
                score = 88
                reasons.append("Targeted direct cash assistance for pregnancy and lactation (wage compensation and nutrition).")
                reasons.append("Provides ₹5,000 (1st child) or ₹6,000 (2nd female child) DBT direct to mother's bank account.")
                verification.append("Mother must register pregnancy with local Anganwadi worker / ASHA.")
                verification.append("Mother must be at least 19 years old and not employed in regular Govt/PSU service.")

        # -------------------------------------------------------------
        # 8. JSY & JSSK (Maternity & Infant Care)
        # -------------------------------------------------------------
        elif scheme_id == "jsy_jssk":
            is_maternity = any("pregnancy" in t or "maternity" in t for t in treatments_lower)
            is_infant = (patient_age <= 1 and beneficiary == "child")
            if is_maternity or is_infant:
                is_match = True
                score = 89
                reasons.append("Guarantees 100% cashless delivery and treatment at government hospitals under JSSK with zero out-of-pocket expenses.")
                if is_maternity:
                    reasons.append("Includes free medicines, blood transfusion, diagnostics, food during stay, and free transport.")
                    reasons.append("Includes Janani Suraksha Yojana cash incentive of ₹1,000 to ₹1,400 for institutional delivery.")
                if is_infant:
                    reasons.append("Covers free cashless inpatient treatment and medicines for sick infants up to 1 year of age.")
                verification.append("Delivery or treatment must take place at a public health facility (PHC, CHC, Sub-District, or District Hospital).")

        # -------------------------------------------------------------
        # 9. RASHTRIYA BAL SWASTHYA KARYAKRAM (RBSK)
        # -------------------------------------------------------------
        elif scheme_id == "rbsk":
            if (patient_age <= 18 and beneficiary == "child") or any("child" in t for t in treatments_lower):
                is_match = True
                score = 86
                reasons.append(f"Child healthcare support: Patient is {patient_age} years old (eligible under the 0–18 years bracket).")
                reasons.append("Covers early detection and 100% free corrective surgeries for congenital heart defects, cleft lip/palate, club foot, neural tube defects, and developmental delays.")
                verification.append("Child must be screened via School / Anganwadi Mobile Health Team or referred to District Early Intervention Centre (DEIC).")
                verification.append("Services provided through public hospitals and empanelled tertiary surgical institutions.")

        # -------------------------------------------------------------
        # 10. PRADHAN MANTRI NATIONAL DIALYSIS PROGRAMME (PMNDP)
        # -------------------------------------------------------------
        elif scheme_id == "pmndp":
            if any("kidney" in t or "dialysis" in t for t in treatments_lower):
                is_match = True
                score = 94
                reasons.append("Matches your requirement for kidney disease care or ongoing dialysis support.")
                if low_income or has_bpl_ration:
                    reasons.append("Provides 100% FREE hemodialysis and peritoneal dialysis sessions for BPL patients.")
                else:
                    reasons.append("Provides heavily subsidized dialysis at government-negotiated rates at District Hospitals.")
                verification.append("Patient must have a medical prescription from a registered nephrologist.")
                verification.append("Must be availed at designated District Hospital Dialysis Centres.")

        # -------------------------------------------------------------
        # 11. PRADHAN MANTRI BHARTIYA JANAUSHADHI PARIYOJANA (PMBJP)
        # -------------------------------------------------------------
        elif scheme_id == "pmbjp":
            needs_meds = any(t in treatments_lower for t in ["medicines and diagnostic tests", "routine medical consultation", "diabetes and chronic diseases", "eye treatment", "other medical treatment"])
            if needs_meds:
                is_match = True
                score = 75
                reasons.append("Ideal for outpatient prescriptions, ongoing chronic disease management, and regular medicines.")
                reasons.append("Offers 2,046+ quality generic medicines at 50% to 90% savings compared to branded counterparts.")
                reasons.append("Universal accessibility: No income test or ration card required.")
                verification.append("Requires a valid doctor's prescription for prescription medicines.")
                verification.append("Locate nearest Kendra via the 'Janaushadhi Sugam' portal or app.")

        # -------------------------------------------------------------
        # 12. TELE-MANAS (Mental Healthcare)
        # -------------------------------------------------------------
        elif scheme_id == "tele_manas":
            if any("mental" in t for t in treatments_lower):
                is_match = True
                score = 96
                reasons.append("Direct match for mental healthcare, stress, depression, anxiety, or psychological distress.")
                reasons.append("24/7 free toll-free tele-counseling available in multiple regional languages via 14416.")
                reasons.append("100% confidential with direct referral to District Mental Health Specialists if required.")
                verification.append("No documentation required — service is immediately accessible via phone.")

        # -------------------------------------------------------------
        # 13. HEALTH MINISTER'S DISCRETIONARY GRANT (HMDG)
        # -------------------------------------------------------------
        elif scheme_id == "hmdg":
            is_serious = any(t in treatments_lower for t in ["cancer treatment", "heart disease treatment", "kidney disease or dialysis", "surgery", "general hospitalization"])
            if (low_income or income_bracket == "Below ₹1 lakh") and is_serious and not is_govt_employee and not has_ayushman_card:
                is_match = True
                score = 72
                reasons.append("Provides one-time financial grant up to ₹1,25,000 for poor patients not covered under regular health assurance.")
                verification.append("Annual family income must not exceed ₹1,50,000 (verified by revenue authority).")
                verification.append("Treatment must be taken strictly in a Government hospital.")
                verification.append("Hospital estimate must be countersigned by Government Hospital Medical Superintendent.")

        # -------------------------------------------------------------
        # Document Readiness Check
        # -------------------------------------------------------------
        if is_match:
            required_docs = scheme["required_documents"]
            doc_ready_count = 0
            doc_status_details = []

            for doc in required_docs:
                doc_lower = doc.lower()
                status_str = "Needs to be arranged / checked"
                
                if "aadhaar" in doc_lower and docs_status.get("aadhaar") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "ration" in doc_lower and docs_status.get("ration_card") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "income" in doc_lower and docs_status.get("income_cert") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "prescription" in doc_lower and docs_status.get("prescription") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "estimate" in doc_lower and docs_status.get("hospital_estimate") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "report" in doc_lower and docs_status.get("medical_reports") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                elif "card" in doc_lower and docs_status.get("govt_health_card") == "available":
                    status_str = "Available ✓"
                    doc_ready_count += 1
                
                doc_status_details.append({"name": doc, "status": status_str})

            matches.append({
                **scheme,
                "relevance_score": score,
                "match_reasons": reasons,
                "verification_needed": verification,
                "doc_status_details": doc_status_details,
                "docs_ready_count": doc_ready_count,
                "docs_total_count": len(required_docs)
            })

    # Sort matches by relevance score descending
    matches.sort(key=lambda s: s["relevance_score"], reverse=True)
    return matches
