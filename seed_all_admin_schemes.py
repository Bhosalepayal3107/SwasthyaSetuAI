"""
seed_all_admin_schemes.py — SwasthyaSetu AI
Adds all additional government healthcare schemes (Schemes 101 to 298)
under the Administrator Panel database with added_by = 'Administrator'.
"""

import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "swasthyasetu.db")

NEW_ADMIN_SCHEMES = [
    {
        "name": "Employees' State Insurance Scheme (ESI / ESIC)",
        "short_tag": "ESIC",
        "category": "Employee Healthcare",
        "govt_level": "Central Government",
        "description": "A social security and health insurance programme providing medical care, hospitalization, sickness benefits, and maternity support for eligible organized sector employees and their families.",
        "who_benefits": "Employees covered under the ESI system earning up to applicable wage limits (₹21,000/month) and their eligible family dependants.",
        "eligibility_rules": [
            "Establishment coverage under ESIC Act",
            "Monthly wage ceiling up to ₹21,000 (₹25,000 for persons with disabilities)",
            "Regular employer and employee statutory contributions",
            "Possession of valid e-Pehchan card"
        ],
        "required_documents": [
            "Aadhaar Card",
            "ESIC e-Pehchan Card / Insurance Number",
            "Employer details and wage verification",
            "Medical prescriptions and referral records"
        ],
        "benefits_text": "Comprehensive outpatient and inpatient medical care with no upper cap on expenditure, sickness cash benefits, maternity benefits, and disability pension.",
        "covered_treatments": ["General hospitalization", "Surgery", "Medicines and diagnostic tests", "Accident and emergency care", "Maternity care"],
        "official_website": "https://www.esic.gov.in/",
        "application_process": "Enrolment through employer on the ESIC portal; access healthcare at any ESIC dispensary or empanelled hospital.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 65,
        "income_limit": "Wage up to ₹21,000/month",
        "match_tags": ["esic", "esi", "employee", "insurance", "hospitalization", "worker"],
        "color": "blue"
    },
    {
        "name": "Central Government Health Scheme (CGHS)",
        "short_tag": "CGHS",
        "category": "Employee Healthcare",
        "govt_level": "Central Government",
        "description": "Comprehensive healthcare services for serving central government employees, pensioners, and other authorized beneficiary categories.",
        "who_benefits": "Eligible central government employees, pensioners, freedom fighters, and their permitted dependants.",
        "eligibility_rules": [
            "Central government employment or pensioner status",
            "Residing in covered CGHS cities",
            "Valid CGHS plastic card holder",
            "Dependent spouse, children, or parents"
        ],
        "required_documents": [
            "Aadhaar Card",
            "CGHS Card",
            "Pension Payment Order (PPO) or Employee ID",
            "Doctor's referral and medical prescription"
        ],
        "benefits_text": "Access to CGHS Wellness Centres, consultation, generic and branded medicines, diagnostic investigations, and cashless hospitalization at empanelled hospitals.",
        "covered_treatments": ["General hospitalization", "Surgery", "Medicines and diagnostic tests", "Chronic disease management", "Cancer treatment"],
        "official_website": "https://cghs.mohfw.gov.in/",
        "application_process": "Apply online at CGHS portal or visit local Additional Director / CGHS Wellness Centre.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "No income limit for eligible employees/pensioners",
        "match_tags": ["cghs", "central government", "employee", "pensioner", "wellness centre"],
        "color": "blue"
    },
    {
        "name": "Pradhan Mantri National Dialysis Programme (PMNDP)",
        "short_tag": "PMNDP",
        "category": "Kidney Care & Dialysis",
        "govt_level": "Central Government",
        "description": "A public healthcare initiative supporting hemodialysis and peritoneal dialysis services for renal patients through designated public health facilities and PPP centers.",
        "who_benefits": "Patients requiring regular dialysis accessing participating government district hospitals and medical colleges.",
        "eligibility_rules": [
            "Clinical assessment confirming chronic kidney disease (CKD stage 5) requiring dialysis",
            "Referral or prescription by certified nephrologist / physician",
            "Treatment at participating government hospital or PPP center"
        ],
        "required_documents": [
            "Aadhaar Card",
            "Nephrologist prescription and dialysis referral",
            "Kidney function test (KFT) and serum creatinine reports",
            "Hospital registration memo"
        ],
        "benefits_text": "100% free dialysis for BPL beneficiaries and heavily subsidized rates for non-BPL patients at district hospitals.",
        "covered_treatments": ["Kidney disease or dialysis", "Hemodialysis", "Peritoneal dialysis", "Nephrology care"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Approach the dialysis unit or medical superintendent at the nearest district hospital with clinical reports.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Free for BPL, subsidized for others",
        "match_tags": ["dialysis", "kidney", "renal", "pmndp", "hemodialysis", "nephrology"],
        "color": "teal"
    },
    {
        "name": "Rashtriya Arogya Nidhi (RAN)",
        "short_tag": "RAN",
        "category": "Critical Illness Financial Aid",
        "govt_level": "Central Government",
        "description": "Financial assistance initiative providing one-time grants to poor patients living below poverty line suffering from specified life-threatening diseases.",
        "who_benefits": "Patients living below poverty line (BPL) requiring specialized treatment at government super-specialty hospitals.",
        "eligibility_rules": [
            "Family must be living below the poverty line (BPL)",
            "Suffering from specified life-threatening disease (cardiac, cancer, renal failure, organ transplant)",
            "Treatment taken at AIIMS, PGIMER, or designated apex government hospitals"
        ],
        "required_documents": [
            "Income certificate from competent revenue authority (Tahsildar / SDM)",
            "Medical certificate and detailed treatment estimate from hospital",
            "BPL Ration Card / proof of poverty line status",
            "Aadhaar Card"
        ],
        "benefits_text": "Financial assistance up to ₹15 lakh (up to ₹50 lakh for rare diseases under NPRD component) released directly to the treating hospital.",
        "covered_treatments": ["Cancer treatment", "Heart surgery", "Kidney transplant", "Organ transplant", "Life-threatening diseases"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Submit application through treating government hospital Medical Superintendent to MoHFW.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Below Poverty Line (BPL)",
        "match_tags": ["ran", "bpl", "cancer", "heart", "transplant", "financial grant"],
        "color": "purple"
    },
    {
        "name": "Health Minister's Discretionary Grant (HMDG)",
        "short_tag": "HMDG",
        "category": "Medical Financial Assistance",
        "govt_level": "Central Government",
        "description": "Discretionary financial assistance for poor patients requiring financial support for medical treatment of serious illness where no other scheme is available.",
        "who_benefits": "Indigent patients whose annual family income is below ₹1,25,000 receiving treatment at government hospitals.",
        "eligibility_rules": [
            "Annual family income not exceeding ₹1,25,000",
            "Treatment in a government or autonomous medical college hospital",
            "Not eligible for reimbursement or PM-JAY / RAN"
        ],
        "required_documents": [
            "Income certificate from Tahsildar / District Magistrate",
            "Medical diagnosis and cost estimate signed by treating doctor",
            "Aadhaar / Voter ID proof",
            "Prescribed HMDG application form"
        ],
        "benefits_text": "Financial grant up to ₹1,25,000 disbursed directly to the government hospital towards surgery or specialized medical care.",
        "covered_treatments": ["Surgery", "General hospitalization", "Specialist treatment", "Medicines and diagnostic tests"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Forward application form duly certified by hospital authorities to the Ministry of Health and Family Welfare.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Annual income up to ₹1,25,000",
        "match_tags": ["hmdg", "grant", "health minister", "financial aid", "low income"],
        "color": "purple"
    },
    {
        "name": "Ayushman Bharat Digital Mission (ABDM / ABHA)",
        "short_tag": "ABDM",
        "category": "Digital Health",
        "govt_level": "Central Government",
        "description": "National digital health architecture supporting 14-digit ABHA numbers, digital health records exchange, consent management, and teleconsultations.",
        "who_benefits": "All Indian citizens seeking seamless access to longitudinal digital medical records across public and private hospitals.",
        "eligibility_rules": [
            "Any Indian citizen holding mobile number or Aadhaar",
            "Voluntary registration with consent-based record sharing"
        ],
        "required_documents": [
            "Aadhaar Card or Mobile phone with OTP capability"
        ],
        "benefits_text": "14-digit ABHA ID card, seamless storage of lab reports and prescriptions, QR-code scan & share hospital OPD registration.",
        "covered_treatments": ["Digital health records", "Teleconsultation", "Hospital OPD registration"],
        "official_website": "https://abdm.gov.in/",
        "application_process": "Register online via abha.abdm.gov.in or download the ABHA mobile app.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["abdm", "abha", "digital health", "health id", "records"],
        "color": "teal"
    },
    {
        "name": "National Health Mission (NHM)",
        "short_tag": "NHM",
        "category": "Public Healthcare",
        "govt_level": "Central Government",
        "description": "Comprehensive umbrella mission strengthening public healthcare delivery, free essential drugs, free diagnostics, and primary health infrastructure across rural and urban India.",
        "who_benefits": "Citizens accessing public healthcare, pregnant women, newborns, children, and families in rural and semi-urban communities.",
        "eligibility_rules": [
            "Universal access at all public healthcare institutions (Sub-centers, PHCs, CHCs, District Hospitals)"
        ],
        "required_documents": [
            "Hospital registration slip / OPD card",
            "Identity proof if requested"
        ],
        "benefits_text": "Free essential medicines, free diagnostic investigations, comprehensive primary healthcare, and maternal-child health interventions.",
        "covered_treatments": ["Primary healthcare", "Maternal health", "Child healthcare", "Free diagnostics", "Medicines and diagnostic tests"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Visit the nearest Primary Health Centre (PHC), Community Health Centre (CHC), or Ayushman Arogya Mandir.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nhm", "public health", "free medicines", "primary care", "rural health"],
        "color": "green"
    },
    {
        "name": "National Programme for Prevention and Control of Non-Communicable Diseases (NP-NCD / NPCDCS)",
        "short_tag": "NPCDCS",
        "category": "Non-Communicable Diseases",
        "govt_level": "Central Government",
        "description": "Public health programme focused on prevention, screening, early detection, and management of major non-communicable diseases including diabetes, hypertension, and common cancers.",
        "who_benefits": "Adults aged 30 and above, patients with diabetes, cardiovascular illness, hypertension, or cancer.",
        "eligibility_rules": [
            "Adults aged 30 years and above for population-based screening",
            "Patients diagnosed with hypertension, diabetes, stroke, or cancer"
        ],
        "required_documents": [
            "Aadhaar or identity proof",
            "Previous diagnostic reports and prescriptions"
        ],
        "benefits_text": "Free population-based NCD screening, free monthly medication for blood pressure and blood sugar, cardiac care units at district hospitals.",
        "covered_treatments": ["Diabetes screening", "Hypertension", "Cancer screening", "Heart disease treatment", "Stroke rehabilitation"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Attend community NCD screening at Ayushman Arogya Mandirs or visit NCD clinic at district hospitals.",
        "states_applicable": "All",
        "age_min": 30,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["npcdcs", "diabetes", "hypertension", "heart", "cancer", "stroke", "ncd"],
        "color": "amber"
    },
    {
        "name": "National Tuberculosis Elimination Programme (NTEP)",
        "short_tag": "NTEP",
        "category": "Tuberculosis Care",
        "govt_level": "Central Government",
        "description": "National disease control programme supporting free rapid molecular TB testing (CBNAAT / TrueNat), free anti-TB drugs, and monthly nutritional cash assistance.",
        "who_benefits": "Anyone with suspected or diagnosed pulmonary or extra-pulmonary tuberculosis, including drug-resistant TB patients.",
        "eligibility_rules": [
            "Clinical signs of TB or confirmed microbiological diagnosis"
        ],
        "required_documents": [
            "Aadhaar Card",
            "Bank account details (for Ni-kshay Poshan nutritional DBT)",
            "Diagnostic sputum / test reports"
        ],
        "benefits_text": "100% free diagnosis, free full course anti-TB medicines, plus ₹500/month direct cash assistance under Ni-kshay Poshan Yojana.",
        "covered_treatments": ["Tuberculosis", "CBNAAT testing", "DOTS treatment", "Chest and respiratory care"],
        "official_website": "https://tbcindia.mohfw.gov.in/",
        "application_process": "Visit any government health facility, designated microscopy centre, or contact local DOTS provider.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["ntep", "tb", "tuberculosis", "dots", "nikshay", "cough", "chest"],
        "color": "blue"
    },
    {
        "name": "National AIDS Control Programme (NACP)",
        "short_tag": "NACP",
        "category": "Infectious Diseases",
        "govt_level": "Central Government",
        "description": "National programme supporting confidential HIV testing, free Antiretroviral Therapy (ART), prevention of parent-to-child transmission, and counselling.",
        "who_benefits": "Individuals seeking voluntary confidential HIV testing or living with HIV/AIDS.",
        "eligibility_rules": [
            "Clinical indication or voluntary request for HIV testing / care"
        ],
        "required_documents": [
            "Confidentiality safeguards apply — hospital registration records"
        ],
        "benefits_text": "Free confidential HIV testing, pre- and post-test counselling, free lifelong ART medications, CD4 and viral load monitoring.",
        "covered_treatments": ["HIV testing", "Antiretroviral therapy", "STI management", "Counselling"],
        "official_website": "https://naco.gov.in/",
        "application_process": "Visit any government Integrated Counselling and Testing Centre (ICTC) or ART Centre.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nacp", "hiv", "aids", "art centre", "ictc", "confidential"],
        "color": "purple"
    },
    {
        "name": "Universal Immunization Programme (UIP)",
        "short_tag": "UIP",
        "category": "Vaccination & Preventive Healthcare",
        "govt_level": "Central Government",
        "description": "Public health immunization programme providing free recommended vaccines protecting children and pregnant women against 12 preventable diseases.",
        "who_benefits": "All infants, children (0-16 years), and pregnant women across India.",
        "eligibility_rules": [
            "Children and pregnant women covered by national immunization schedule"
        ],
        "required_documents": [
            "Mother and Child Protection (MCP) Card / Vaccination record"
        ],
        "benefits_text": "Free vaccines against Polio, BCG, Hepatitis B, DPT, Measles-Rubella (MR), Rotavirus, PCV, Tetanus.",
        "covered_treatments": ["Vaccination", "Child healthcare", "Preventive care"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Contact an Anganwadi centre, government health centre, or attend village health & nutrition days (VHND).",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 18,
        "income_limit": "Universal — No income limit",
        "match_tags": ["uip", "vaccine", "immunization", "polio", "child", "infant"],
        "color": "green"
    },
    {
        "name": "Janani Suraksha Yojana (JSY)",
        "short_tag": "JSY",
        "category": "Maternal Health",
        "govt_level": "Central Government",
        "description": "Safe motherhood intervention promoting institutional delivery among poor pregnant women through conditional cash assistance.",
        "who_benefits": "Pregnant women delivering in government health facilities or accredited private hospitals.",
        "eligibility_rules": [
            "Pregnant women delivering in public health facility or accredited hospital",
            "Applicable state category (LPS/HPS) and BPL/SC/ST conditions"
        ],
        "required_documents": [
            "MCP card / pregnancy registration",
            "Aadhaar Card",
            "Bank account details (for DBT)",
            "Institutional delivery certificate"
        ],
        "benefits_text": "Cash assistance (₹1,400 rural / ₹1,000 urban in low performing states) deposited directly into beneficiary's bank account.",
        "covered_treatments": ["Institutional delivery", "Maternal care", "Postnatal care"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Register pregnancy with local ASHA worker or at nearest PHC/government maternity hospital.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 50,
        "income_limit": "BPL / Universal depending on state rules",
        "match_tags": ["jsy", "maternity", "pregnant", "delivery", "cash assistance", "mother"],
        "color": "pink"
    },
    {
        "name": "Janani Shishu Suraksha Karyakram (JSSK)",
        "short_tag": "JSSK",
        "category": "Maternal and Child Healthcare",
        "govt_level": "Central Government",
        "description": "Entitles all pregnant women delivering in public health institutions and sick newborns up to 1 year to completely free medical care with zero out-of-pocket expenses.",
        "who_benefits": "All pregnant women delivering in public facilities and sick newborns / infants up to 1 year.",
        "eligibility_rules": [
            "Pregnant women accessing public health facilities",
            "Sick newborns and infants receiving inpatient or outpatient care"
        ],
        "required_documents": [
            "Aadhaar or identity proof",
            "Mother and Child Protection (MCP) card",
            "Newborn birth or admission records"
        ],
        "benefits_text": "Free normal and caesarean delivery, free drugs, free diagnostics, free blood, free diet, and free transport from home to facility and return.",
        "covered_treatments": ["Free delivery", "Caesarean section", "Sick newborn care", "Free transport", "Medicines and diagnostics"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Visit any government health facility providing maternity and newborn services.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 50,
        "income_limit": "Universal — Zero charges",
        "match_tags": ["jssk", "pregnant", "free delivery", "newborn", "c-section", "maternal"],
        "color": "pink"
    },
    {
        "name": "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
        "short_tag": "PMSMA",
        "category": "Pregnancy & Antenatal Care",
        "govt_level": "Central Government",
        "description": "Promotes comprehensive antenatal check-ups on the 9th of every month, focusing on identifying high-risk pregnancies and providing specialized medical assessment.",
        "who_benefits": "All pregnant women in their 2nd and 3rd trimesters.",
        "eligibility_rules": [
            "Pregnant women seeking antenatal care on the 9th day of the month"
        ],
        "required_documents": [
            "MCP card / antenatal registration card",
            "Existing pregnancy-related medical reports",
            "Identity card"
        ],
        "benefits_text": "Free antenatal clinical examination by gynaecologists, diagnostic tests (blood, urine, ultrasound), and management of high-risk pregnancies.",
        "covered_treatments": ["Antenatal checkup", "Ultrasound", "High-risk pregnancy care", "Maternal diagnostics"],
        "official_website": "https://pmsma.mohfw.gov.in/",
        "application_process": "Visit the nearest participating government hospital or CHC on the 9th of every month.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 50,
        "income_limit": "Universal — No income limit",
        "match_tags": ["pmsma", "pregnancy", "antenatal", "anc", "ultrasound", "mother"],
        "color": "pink"
    },
    {
        "name": "Rashtriya Bal Swasthya Karyakram (RBSK)",
        "short_tag": "RBSK",
        "category": "Child Healthcare & Early Intervention",
        "govt_level": "Central Government",
        "description": "Child health initiative screening children from birth to 18 years for 4Ds: Defects at birth, Diseases, Deficiencies, and Developmental delays including disabilities.",
        "who_benefits": "Children from birth to 18 years in rural and urban areas, Anganwadi children, and government school students.",
        "eligibility_rules": [
            "Age from birth to 18 years enrolled in schools/Anganwadis or screened at birth"
        ],
        "required_documents": [
            "Birth certificate or age proof",
            "School / Anganwadi ID or screening referral card",
            "Aadhaar Card (if available)"
        ],
        "benefits_text": "Free screening, surgical management of congenital heart defects, cleft lip/palate, club foot, and comprehensive therapies at District Early Intervention Centres.",
        "covered_treatments": ["Child healthcare", "Congenital heart disease", "Cleft lip and palate", "Club foot", "Developmental delays"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Contact school screening team, Anganwadi worker, or visit District Early Intervention Centre (DEIC).",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 18,
        "income_limit": "Universal — No income limit",
        "match_tags": ["rbsk", "child", "pediatric", "congenital defect", "cleft lip", "heart disease child"],
        "color": "green"
    },
    {
        "name": "Rashtriya Kishor Swasthya Karyakram (RKSK)",
        "short_tag": "RKSK",
        "category": "Adolescent Healthcare",
        "govt_level": "Central Government",
        "description": "National adolescent health programme addressing nutrition, sexual and reproductive health, mental health, substance misuse prevention, and non-communicable diseases.",
        "who_benefits": "Adolescents aged 10–19 years.",
        "eligibility_rules": [
            "Adolescents aged 10 to 19 years"
        ],
        "required_documents": [
            "Age proof or identity document if requested"
        ],
        "benefits_text": "Adolescent Friendly Health Clinics (AFHC), peer educator support, nutritional supplementation, mental health counselling, and menstrual hygiene support.",
        "covered_treatments": ["Adolescent counselling", "Nutrition", "Mental health", "Menstrual hygiene", "Anemia prevention"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Visit an Adolescent Friendly Health Clinic (AFHC) / Ujala clinic at government health facilities.",
        "states_applicable": "All",
        "age_min": 10,
        "age_max": 19,
        "income_limit": "Universal — No income limit",
        "match_tags": ["rksk", "adolescent", "teen", "mental health", "menstrual hygiene", "youth"],
        "color": "blue"
    },
    {
        "name": "National Programme for Health Care of the Elderly (NPHCE)",
        "short_tag": "NPHCE",
        "category": "Senior Citizen Healthcare",
        "govt_level": "Central Government",
        "description": "Public healthcare programme providing accessible, affordable, and dedicated healthcare for older adults through geriatric clinics and wards.",
        "who_benefits": "Senior citizens aged 60 years and above seeking dedicated geriatric care.",
        "eligibility_rules": [
            "Age 60 years and above"
        ],
        "required_documents": [
            "Age proof / Aadhaar Card",
            "Existing medical records and prescriptions"
        ],
        "benefits_text": "Dedicated weekly geriatric clinics at PHCs, 10-bed geriatric wards at District Hospitals, regional geriatric centres, and physiotherapy support.",
        "covered_treatments": ["Geriatric assessment", "Joint pain and arthritis", "Hypertension and diabetes", "Dementia care", "Physiotherapy"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit a government hospital or health facility offering dedicated NPHCE geriatric services.",
        "states_applicable": "All",
        "age_min": 60,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nphce", "elderly", "senior citizen", "geriatric", "aging", "chronic"],
        "color": "amber"
    },
    {
        "name": "National Programme for Control of Blindness and Visual Impairment (NPCBVI)",
        "short_tag": "NPCBVI",
        "category": "Eye Care & Vision Support",
        "govt_level": "Central Government",
        "description": "National programme supporting eye healthcare, free cataract surgeries, screening, and treatment of avoidable visual impairment.",
        "who_benefits": "People experiencing vision difficulties, cataracts, refractive errors, or corneal diseases.",
        "eligibility_rules": [
            "Clinical assessment indicating cataract, refractive error, or visual impairment"
        ],
        "required_documents": [
            "Aadhaar or identity proof",
            "Eye examination reports"
        ],
        "benefits_text": "Free cataract surgery with intraocular lens (IOL) implantation, free screening, eye banking support, and free spectacles for school children.",
        "covered_treatments": ["Eye treatment", "Cataract surgery", "Refractive error correction", "Glaucoma treatment"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Contact a participating government hospital ophthalmology department or attend free eye screening camps.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["npcbvi", "eye", "cataract", "blindness", "vision", "spectacles"],
        "color": "teal"
    },
    {
        "name": "National Mental Health Programme (NMHP)",
        "short_tag": "NMHP",
        "category": "Mental Healthcare",
        "govt_level": "Central Government",
        "description": "National initiative supporting access to mental healthcare through public facilities and community-level services.",
        "who_benefits": "People experiencing psychological distress, depression, anxiety, severe mental disorders, or requiring counselling.",
        "eligibility_rules": [
            "Individuals seeking mental health assessment, counselling, or treatment"
        ],
        "required_documents": [
            "Identity card if requested",
            "Previous psychiatric/medical records if available"
        ],
        "benefits_text": "Access to psychiatric consultations, free psychotropic medicines, psychotherapy, inpatient stabilization, and 24x7 Tele-MANAS support (14416).",
        "covered_treatments": ["Psychiatric consultation", "Depression treatment", "Anxiety management", "Mental health counselling"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit a government hospital psychiatry unit or dial Tele-MANAS toll-free helpline at 14416.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nmhp", "mental health", "depression", "anxiety", "tele-manas", "psychiatry"],
        "color": "purple"
    },
    {
        "name": "District Mental Health Programme (DMHP)",
        "short_tag": "DMHP",
        "category": "Mental Healthcare",
        "govt_level": "Central Government",
        "description": "District-level operational programme providing decentralized mental health services, crisis counselling, suicide prevention, and free medicines.",
        "who_benefits": "People seeking mental health support in participating districts across India.",
        "eligibility_rules": [
            "Resident of covered district seeking psychiatric evaluation or counselling"
        ],
        "required_documents": [
            "Identity proof and existing prescriptions where available"
        ],
        "benefits_text": "Community mental health clinics, 10-bed psychiatric ward at district hospital, suicide prevention counseling, and free psychotropic drugs.",
        "covered_treatments": ["Mental health counselling", "Psychotropic medicines", "Suicide prevention", "Community rehabilitation"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Contact the district civil hospital or district mental health team.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["dmhp", "district mental health", "counselling", "psychiatry", "community health"],
        "color": "purple"
    },
    {
        "name": "Chief Minister's Health Insurance Scheme — Nagaland (CMHIS)",
        "short_tag": "CMHIS",
        "category": "State Health Insurance",
        "govt_level": "State Government (Nagaland)",
        "description": "Nagaland's state health insurance initiative providing cashless hospitalization coverage to state government employees, pensioners, and indigenous residents.",
        "who_benefits": "State government employees, pensioners, and indigenous residents of Nagaland not covered under PM-JAY.",
        "eligibility_rules": [
            "Indigenous resident of Nagaland holding Indigenous Inhabitant Certificate (IIC) or permanent resident",
            "State government employee or pensioner of Nagaland"
        ],
        "required_documents": [
            "Indigenous Inhabitant Certificate (IIC) / Domicile Certificate",
            "Aadhaar Card",
            "Ration Card or Employee PPO book"
        ],
        "benefits_text": "Cashless hospitalization coverage up to ₹5 lakh per family per annum at empanelled hospitals.",
        "covered_treatments": ["General hospitalization", "Surgery", "Cancer treatment", "Heart disease treatment", "Accident and emergency care"],
        "official_website": "https://health.nagaland.gov.in/",
        "application_process": "Register via official Nagaland CMHIS portal or at designated district registration kiosks.",
        "states_applicable": "Nagaland",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal for Nagaland residents",
        "match_tags": ["cmhis", "nagaland", "northeast", "state insurance", "hospitalization"],
        "color": "blue"
    },
    {
        "name": "Chief Minister's Free Cancer Chemotherapy Scheme — Arunachal Pradesh",
        "short_tag": "Arunachal Chemotherapy",
        "category": "State Oncology Assistance",
        "govt_level": "State Government (Arunachal Pradesh)",
        "description": "State initiative supporting cancer patients by providing free chemotherapy drugs and treatment at empanelled tertiary hospitals.",
        "who_benefits": "Permanent resident cancer patients of Arunachal Pradesh requiring chemotherapy.",
        "eligibility_rules": [
            "Permanent resident or indigenous citizen of Arunachal Pradesh",
            "Histopathologically confirmed cancer diagnosis requiring chemotherapy",
            "Treatment at designated state or empanelled cancer centers (e.g., TRIHMS)"
        ],
        "required_documents": [
            "Arunachal Pradesh Scheduled Tribe (APST) / Permanent Resident Certificate",
            "Oncologist diagnosis, histopathology report, and chemotherapy protocol",
            "Aadhaar Card"
        ],
        "benefits_text": "Free chemotherapy drugs and day-care infusion up to ₹5 lakh per patient.",
        "covered_treatments": ["Cancer treatment", "Chemotherapy", "Oncology day-care"],
        "official_website": "https://arunachalpradesh.gov.in/",
        "application_process": "Contact the state cancer society or department of oncology at TRIHMS, Naharlagun.",
        "states_applicable": "Arunachal Pradesh",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "No income limit for eligible residents",
        "match_tags": ["arunachal", "cancer", "chemotherapy", "oncology", "apst"],
        "color": "purple"
    },
    {
        "name": "Medical Assistance for Registered Construction Workers — Arunachal Pradesh",
        "short_tag": "BOCW Arunachal",
        "category": "Worker Welfare Health Assistance",
        "govt_level": "State Government (Arunachal Pradesh)",
        "description": "Medical assistance and hospitalization financial aid associated with the Arunachal Pradesh Building and Other Construction Workers Welfare Board (APBOCWWB).",
        "who_benefits": "Registered construction workers holding active BOCW registration in Arunachal Pradesh and their families.",
        "eligibility_rules": [
            "Registered as active worker with APBOCW Welfare Board for at least 90 days",
            "Up-to-date annual contribution payment"
        ],
        "required_documents": [
            "BOCW Worker Registration Book / Shramik Card",
            "Aadhaar Card",
            "Medical bills, doctor's prescription, and hospital discharge summary",
            "Bank passbook copy"
        ],
        "benefits_text": "Medical reimbursement and major illness financial grant up to ₹50,000 for hospitalisation and treatment.",
        "covered_treatments": ["General hospitalization", "Surgery", "Accident treatment", "Medicines and diagnostic tests"],
        "official_website": "https://arunachalpradesh.gov.in/",
        "application_process": "Apply through the Registering Officer of APBOCWWB at the district labour office.",
        "states_applicable": "Arunachal Pradesh",
        "age_min": 18,
        "age_max": 60,
        "income_limit": "Registered construction workers",
        "match_tags": ["bocw", "construction worker", "arunachal", "labour board", "medical assistance"],
        "color": "amber"
    },
    {
        "name": "National Viral Hepatitis Control Programme (NVHCP)",
        "short_tag": "NVHCP",
        "category": "Infectious Disease Diagnosis & Treatment",
        "govt_level": "Central Government",
        "description": "National initiative providing free laboratory screening, viral load diagnostics, and oral direct-acting antiviral treatment for Hepatitis B and Hepatitis C.",
        "who_benefits": "People diagnosed with or at risk of Hepatitis B and Hepatitis C infections.",
        "eligibility_rules": [
            "Clinical or serological indication of Hepatitis B (HBsAg+) or Hepatitis C (Anti-HCV+)"
        ],
        "required_documents": [
            "Aadhaar or identity proof",
            "Previous blood test reports and clinical prescriptions"
        ],
        "benefits_text": "Free quantitative viral load testing (RT-PCR) and complete free course of curative Direct Acting Antivirals (DAAs) for Hepatitis C and lifelong management for Hepatitis B.",
        "covered_treatments": ["Infectious disease treatment", "Hepatitis testing", "Viral load diagnostics", "Liver care"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit the Model Treatment Centre (MTC) or State Treatment Centre at government medical colleges.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nvhcp", "hepatitis", "hepatitis b", "hepatitis c", "liver", "viral"],
        "color": "teal"
    },
    {
        "name": "National Leprosy Eradication Programme (NLEP)",
        "short_tag": "NLEP",
        "category": "Infectious Disease Treatment",
        "govt_level": "Central Government",
        "description": "National programme supporting early case detection, free Multi-Drug Therapy (MDT), disability prevention, and reconstructive surgery for leprosy.",
        "who_benefits": "Individuals with suspected signs or confirmed diagnosis of leprosy.",
        "eligibility_rules": [
            "Clinical diagnosis of paucibacillary or multibacillary leprosy"
        ],
        "required_documents": [
            "Identity card if requested; clinical records at government health facility"
        ],
        "benefits_text": "100% free WHO-standard Multi-Drug Therapy (MDT), free microcellular rubber (MCR) footwear, assistive aids, and cash assistance for reconstructive surgery.",
        "covered_treatments": ["Leprosy treatment", "Multi-drug therapy", "Reconstructive surgery", "Disability prevention"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Visit any government primary health centre, civil hospital, or district leprosy unit.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nlep", "leprosy", "mdt", "skin", "disability prevention"],
        "color": "green"
    },
    {
        "name": "National Vector Borne Disease Control Programme (NVBDCP)",
        "short_tag": "NVBDCP",
        "category": "Vector-Borne Diseases",
        "govt_level": "Central Government",
        "description": "National umbrella programme for prevention, diagnosis, and treatment of vector-borne diseases: Malaria, Dengue, Chikungunya, Japanese Encephalitis, Kala-azar, and Lymphatic Filariasis.",
        "who_benefits": "Patients suffering from or at risk of mosquito-borne and vector-borne infections.",
        "eligibility_rules": [
            "Clinical signs of vector-borne illness (fever, chills, rash, joint pain)"
        ],
        "required_documents": [
            "Hospital registration / clinical records"
        ],
        "benefits_text": "Free Rapid Diagnostic Tests (RDT), free microscopic blood examination, free Artemisinin-based Combination Therapy (ACT), and symptomatic care.",
        "covered_treatments": ["Malaria treatment", "Dengue care", "Kala-azar", "Filaria care", "Fever and infection diagnostics"],
        "official_website": "https://ncvbdc.mohfw.gov.in/",
        "application_process": "Visit the nearest PHC, government hospital, or contact local ASHA / malaria health worker.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nvbdcp", "malaria", "dengue", "chikungunya", "fever", "vector borne"],
        "color": "amber"
    },
    {
        "name": "National Programme for Prevention and Control of Deafness (NPPCD)",
        "short_tag": "NPPCD",
        "category": "Hearing Health & Audiology",
        "govt_level": "Central Government",
        "description": "Public health initiative supporting hearing loss prevention, newborn hearing screening, audiometry testing, and surgical correction of ear diseases.",
        "who_benefits": "Children and adults with suspected hearing loss, ear discharge, or speech delays.",
        "eligibility_rules": [
            "Patients with conductive or sensorineural hearing impairment, chronic suppurative otitis media (CSOM)"
        ],
        "required_documents": [
            "Audiometry test report",
            "Aadhaar or identity proof"
        ],
        "benefits_text": "Free hearing screening, pure-tone audiometry (PTA), OAE testing for newborns, free medical and surgical treatment (tympanoplasty, mastoidectomy).",
        "covered_treatments": ["Hearing screening", "Ear surgery", "Audiology assessment", "Hearing rehabilitation"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit the ENT department at any district civil hospital or government medical college.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nppcd", "hearing", "ear", "audiology", "deafness", "ent"],
        "color": "teal"
    },
    {
        "name": "National Programme for Palliative Care (NPPC)",
        "short_tag": "NPPC",
        "category": "Palliative & Supportive Care",
        "govt_level": "Central Government",
        "description": "Supports pain relief, symptom management, and holistic supportive care for patients living with serious, incurable, or terminal illnesses.",
        "who_benefits": "Patients with advanced cancer, end-stage organ failure, progressive neurological conditions, and their caregivers.",
        "eligibility_rules": [
            "Medical diagnosis of life-limiting or chronic debilitating disease requiring symptom and pain control"
        ],
        "required_documents": [
            "Medical reports and diagnostic summary",
            "Doctor's referral and prescription"
        ],
        "benefits_text": "Access to oral morphine and essential opioid analgesics for breakthrough pain, symptom relief, home care support, and psychosocial counselling.",
        "covered_treatments": ["Palliative care", "Pain management", "Supportive oncology", "Home-based healthcare"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Contact palliative care unit at district hospital or regional cancer centre.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nppc", "palliative", "pain management", "cancer support", "hospice"],
        "color": "purple"
    },
    {
        "name": "National Organ Transplant Programme (NOTP)",
        "short_tag": "NOTP",
        "category": "Organ Donation & Transplantation",
        "govt_level": "Central Government",
        "description": "National framework promoting deceased organ donation, organ retrieval, allocation protocols via NOTTO, and immunosuppressant medication support for BPL recipients.",
        "who_benefits": "Patients with end-stage organ failure (kidney, liver, heart, lung, cornea) waiting for transplant.",
        "eligibility_rules": [
            "Certified end-stage organ disease requiring organ transplantation",
            "Registered on the national waiting list through NOTTO / ROTTO / SOTTO"
        ],
        "required_documents": [
            "Transplant approval committee authorization",
            "Organ matching and tissue typing reports",
            "Aadhaar Card",
            "Income certificate (for post-transplant immunosuppressant grant)"
        ],
        "benefits_text": "Subsidized post-transplant immunosuppressant medications for BPL recipients, transparent organ allocation via NOTTO registry.",
        "covered_treatments": ["Organ transplant", "Kidney transplant", "Liver transplant", "Corneal transplant"],
        "official_website": "https://notto.mohfw.gov.in/",
        "application_process": "Register via empanelled transplant hospital on the NOTTO national registry.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Financial assistance targeted to BPL/low-income",
        "match_tags": ["notp", "notto", "organ transplant", "kidney transplant", "liver transplant", "organ donation"],
        "color": "blue"
    },
    {
        "name": "National Programme for Prevention and Management of Burn Injuries (NPPMBI)",
        "short_tag": "NPPMBI",
        "category": "Burn Care & Trauma",
        "govt_level": "Central Government",
        "description": "Strengthens specialized burn units, emergency burn care protocols, rehabilitation, and reconstructive surgery across government medical colleges.",
        "who_benefits": "Individuals suffering from acute thermal, chemical, or electrical burn injuries and burn contracture sequelae.",
        "eligibility_rules": [
            "Patients with acute or chronic burn injuries requiring hospital management"
        ],
        "required_documents": [
            "Emergency hospital admission records (emergency care is never delayed for paperwork)"
        ],
        "benefits_text": "Specialized burn ICU management, wound debridement, fluid resuscitation, skin grafting, and post-burn contracture release surgery.",
        "covered_treatments": ["Burn treatment", "Emergency trauma", "Skin grafting", "Plastic surgery"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Seek emergency admission at the nearest government medical college or district hospital burn unit.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nppmbi", "burn", "trauma", "skin graft", "plastic surgery", "emergency"],
        "color": "amber"
    },
    {
        "name": "National Programme for Prevention and Control of Fluorosis (NPPCF)",
        "short_tag": "NPPCF",
        "category": "Environmental & Public Health",
        "govt_level": "Central Government",
        "description": "Addresses endemic dental and skeletal fluorosis caused by high fluoride in groundwater through surveillance, safe drinking water education, and treatment.",
        "who_benefits": "Communities and individuals in fluoride-endemic districts suffering from dental mottling or skeletal deformities.",
        "eligibility_rules": [
            "Residing in fluoride-affected districts with clinical signs of dental or skeletal fluorosis"
        ],
        "required_documents": [
            "Water sample test report or clinical assessment record"
        ],
        "benefits_text": "Free urinary fluoride testing, nutritional supplementation (calcium, vitamin C, vitamin D), and physical rehabilitation.",
        "covered_treatments": ["Fluorosis treatment", "Dental care", "Bone and joint health", "Nutritional therapy"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Contact district fluorosis consultant or visit district civil hospital.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["nppcf", "fluorosis", "dental", "bone", "drinking water", "environment"],
        "color": "teal"
    },
    {
        "name": "National Programme for Prevention and Control of Occupational Diseases",
        "short_tag": "Occupational Health",
        "category": "Occupational Health",
        "govt_level": "Central Government",
        "description": "Public health initiative focused on the surveillance, early detection, and management of silicosis, asbestosis, pneumoconiosis, and occupational dermatoses.",
        "who_benefits": "Workers in stone crushing, mining, ceramics, foundries, textiles, and hazardous industrial sectors.",
        "eligibility_rules": [
            "Documented occupational exposure to silica dust, asbestos, or industrial hazards with respiratory symptoms"
        ],
        "required_documents": [
            "Workplace certificate or employment history",
            "Chest X-ray / High-Resolution CT scan (ILO classification)",
            "Aadhaar Card"
        ],
        "benefits_text": "Free screening at occupational health clinics, lung function testing, disability assessment, and state silicosis welfare compensation linkage.",
        "covered_treatments": ["Silicosis treatment", "Respiratory care", "Pulmonary rehabilitation", "Occupational health"],
        "official_website": "https://dghs.mohfw.gov.in/",
        "application_process": "Visit the occupational health clinic at designated government medical colleges or district labour health officer.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 70,
        "income_limit": "Industrial and mine workers",
        "match_tags": ["occupational health", "silicosis", "pneumoconiosis", "worker", "mining", "respiratory"],
        "color": "amber"
    },
    {
        "name": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)",
        "short_tag": "PMBJP",
        "category": "Affordable Medicines",
        "govt_level": "Central Government",
        "description": "Government initiative providing over 2,000 quality-assured generic medicines and 300 surgical consumables at 50% to 90% cheaper prices than branded equivalents.",
        "who_benefits": "All citizens seeking affordable high-quality medicines for chronic diseases, diabetes, cardiac care, and daily healthcare.",
        "eligibility_rules": [
            "Open to all citizens across India with valid doctor's prescription"
        ],
        "required_documents": [
            "Doctor's prescription for prescription-only medicines"
        ],
        "benefits_text": "Huge savings on monthly medicine bills with quality generic medicines tested by NABL-accredited laboratories.",
        "covered_treatments": ["Medicines and diagnostic tests", "Diabetes care", "Cardiology drugs", "Antibiotics", "Surgical consumables"],
        "official_website": "https://janaushadhi.gov.in/",
        "application_process": "Locate nearest Janaushadhi Kendra via 'Janaushadhi Sugam' mobile app or walk in with doctor prescription.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — Open to all",
        "match_tags": ["pmbjp", "janaushadhi", "generic medicines", "cheap medicine", "pharmacy"],
        "color": "green"
    },
    {
        "name": "Assistance to Disabled Persons for Purchase/Fitting of Aids and Appliances (ADIP)",
        "short_tag": "ADIP",
        "category": "Disability & Assistive Devices",
        "govt_level": "Central Government",
        "description": "Central scheme assisting eligible persons with disabilities in obtaining modern, scientifically manufactured assistive devices, wheelchairs, prosthetics, and hearing aids.",
        "who_benefits": "Persons with benchmark disabilities (40% and above) belonging to economically weaker sections.",
        "eligibility_rules": [
            "Disability certificate indicating 40% or more disability (or UDID card)",
            "Monthly income not exceeding ₹22,500 (full grant up to ₹15,000; 50% aid between ₹15,001 and ₹22,500)",
            "Has not received the same aid in the last 3 years"
        ],
        "required_documents": [
            "Disability Certificate / UDID Card",
            "Income Certificate / BPL Ration Card",
            "Aadhaar Card",
            "Passport size photograph showing disability"
        ],
        "benefits_text": "Free motorized tricycles, wheelchairs, artificial limbs, crutches, smart canes, digital hearing aids, and battery-operated prosthetics.",
        "covered_treatments": ["Assistive devices", "Artificial limbs", "Wheelchairs", "Hearing aids", "Disability rehabilitation"],
        "official_website": "https://depwd.gov.in/en/adip-scheme/",
        "application_process": "Apply online through ALIMCO ARJUN portal or attend district ALIMCO assessment & distribution camps.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Monthly income up to ₹22,500",
        "match_tags": ["adip", "disability", "udid", "wheelchair", "hearing aid", "prosthetics", "divyangjan"],
        "color": "teal"
    },
    {
        "name": "Deendayal Disabled Rehabilitation Scheme (DDRS)",
        "short_tag": "DDRS",
        "category": "Disability & Rehabilitation",
        "govt_level": "Central Government",
        "description": "Scheme grant-in-aid to voluntary organizations providing special education, vocational training, early intervention, and rehabilitation for persons with disabilities.",
        "who_benefits": "Persons with intellectual disabilities, autism, cerebral palsy, visual and hearing impairments.",
        "eligibility_rules": [
            "Persons with documented disabilities accessing services at accredited DDRS institutions"
        ],
        "required_documents": [
            "Disability Certificate / UDID Card",
            "Identity and age proof",
            "Assessment recommendation"
        ],
        "benefits_text": "Free special education, therapeutic services (speech therapy, occupational therapy), vocational training, and residential rehabilitation.",
        "covered_treatments": ["Disability rehabilitation", "Therapy services", "Special education", "Vocational training"],
        "official_website": "https://depwd.gov.in/",
        "application_process": "Enroll at nearest DDRS-supported special school or rehabilitation centre in the district.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 65,
        "income_limit": "Universal for enrolled beneficiaries",
        "match_tags": ["ddrs", "rehabilitation", "special education", "disability", "autism", "cerebral palsy"],
        "color": "blue"
    },
    {
        "name": "National Trust Welfare Schemes (Niramaya Health Insurance)",
        "short_tag": "Niramaya",
        "category": "Disability Health Insurance",
        "govt_level": "Central Government",
        "description": "Affordable health insurance cover up to ₹1,00,000 for persons with Autism, Cerebral Palsy, Mental Retardation, and Multiple Disabilities.",
        "who_benefits": "Persons affected by Autism, Cerebral Palsy, Intellectual Disability, or Multiple Disabilities.",
        "eligibility_rules": [
            "Disability certificate covering one of the four National Trust Act conditions",
            "Enrolment with valid National Trust registered organization"
        ],
        "required_documents": [
            "Disability Certificate (Autism / CP / MR / Multiple)",
            "Aadhaar Card of beneficiary and legal guardian",
            "BPL Card or Income Certificate (free premium for BPL; nominal ₹250/yr for others)",
            "Bank account details"
        ],
        "benefits_text": "Health insurance coverage up to ₹1,00,000 per year for OPD, hospitalization, corrective surgery, and therapy.",
        "covered_treatments": ["Hospitalization", "Corrective surgery", "Speech therapy", "Physiotherapy", "Medicines"],
        "official_website": "https://thenationaltrust.gov.in/",
        "application_process": "Apply through registered local organizations (NGOs) or directly on the National Trust portal.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Nominal premium based on income slab",
        "match_tags": ["niramaya", "national trust", "autism", "cerebral palsy", "intellectual disability", "insurance"],
        "color": "purple"
    },
    {
        "name": "Rashtriya Vayoshri Yojana (RVY)",
        "short_tag": "Vayoshri",
        "category": "Senior Citizen Assistive Devices",
        "govt_level": "Central Government",
        "description": "Provides physical aids and assisted-living devices for senior citizens belonging to the BPL category who suffer from age-related disabilities or infirmities.",
        "who_benefits": "Senior citizens aged 60 and above belonging to BPL households or earning less than ₹15,000/month.",
        "eligibility_rules": [
            "Age 60 years or above",
            "Belonging to BPL category or monthly family income less than ₹15,000",
            "Suffering from age-related functional disability (mobility, vision, hearing, dental)"
        ],
        "required_documents": [
            "Age proof (Aadhaar, Voter ID, birth certificate)",
            "BPL Ration Card / Income Certificate",
            "Medical certificate indicating age-related disability"
        ],
        "benefits_text": "Free assisted-living devices including walking sticks, elbow crutches, walkers, hearing aids, wheelchairs, artificial dentures, and spectacles.",
        "covered_treatments": ["Assistive living devices", "Dentures", "Spectacles", "Hearing aids", "Mobility aids"],
        "official_website": "https://socialjustice.gov.in/",
        "application_process": "Attend district assessment camps conducted by ALIMCO or register at the District Social Welfare Office.",
        "states_applicable": "All",
        "age_min": 60,
        "age_max": 120,
        "income_limit": "BPL / Income below ₹15,000/month",
        "match_tags": ["rvy", "vayoshri", "senior citizen", "elderly", "dentures", "walker", "assistive devices"],
        "color": "amber"
    },
    {
        "name": "Unique Disability ID (UDID) Card & Certification",
        "short_tag": "UDID",
        "category": "Disability Identification & Access",
        "govt_level": "Central Government",
        "description": "Single national identity card and certificate for persons with disabilities, digitizing disability data and granting seamless nationwide access to welfare benefits.",
        "who_benefits": "Any person with a certified permanent disability (locomotor, visual, hearing, intellectual, mental illness, neurological, etc.).",
        "eligibility_rules": [
            "Indian citizen with medical assessment confirming qualifying disability under RPwD Act 2016"
        ],
        "required_documents": [
            "Aadhaar Card",
            "Address proof",
            "Passport size photograph",
            "Existing medical / disability certificates"
        ],
        "benefits_text": "National UDID Smart Card, pan-India validity, doorstep verification, railway/bus travel concessions, and automatic qualification for welfare schemes.",
        "covered_treatments": ["Disability certification", "Concession verification", "Scheme access"],
        "official_website": "https://www.swavlambancard.gov.in/",
        "application_process": "Register online at swavlambancard.gov.in, select appointment at nearest District Medical Board.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — No income limit",
        "match_tags": ["udid", "swavlamban", "disability card", "certificate", "divyangjan"],
        "color": "teal"
    },
    {
        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "short_tag": "PMMVY",
        "category": "Maternity Financial Assistance",
        "govt_level": "Central Government",
        "description": "Direct Benefit Transfer (DBT) maternity scheme providing cash incentive to pregnant and lactating mothers for first child (₹5,000) and second girl child (₹6,000).",
        "who_benefits": "Pregnant women and lactating mothers from socially/economically disadvantaged sections.",
        "eligibility_rules": [
            "Pregnant women (age 19 and above) holding BPL/Antyodaya/E-Shram/PM-JAY card",
            "First live birth or second live birth (if child is a girl)",
            "Not in regular government / PSU employment"
        ],
        "required_documents": [
            "Aadhaar Card of pregnant woman and husband",
            "Mother and Child Protection (MCP) card",
            "Bank account passbook linked to Aadhaar (single account)",
            "Birth certificate of infant (for subsequent instalments)"
        ],
        "benefits_text": "Cash incentive of ₹5,000 in two instalments for first child; single instalment of ₹6,000 for second girl child.",
        "covered_treatments": ["Maternity assistance", "Nutrition support", "Postnatal care"],
        "official_website": "https://pmmvy.wcd.gov.in/",
        "application_process": "Register at the local Anganwadi Centre or apply online at pmmvy.wcd.gov.in.",
        "states_applicable": "All",
        "age_min": 19,
        "age_max": 45,
        "income_limit": "BPL, e-Shram, PM-JAY, or SC/ST households",
        "match_tags": ["pmmvy", "maternity", "pregnant", "cash benefit", "nutrition", "mother"],
        "color": "pink"
    },
    {
        "name": "Mission Saksham Anganwadi and POSHAN 2.0",
        "short_tag": "POSHAN 2.0",
        "category": "Nutrition & Child Development",
        "govt_level": "Central Government",
        "description": "National nutrition mission combating malnutrition, stunting, wasting, and anemia among children under 6 years, adolescent girls, pregnant women, and lactating mothers.",
        "who_benefits": "Children aged 6 months to 6 years, pregnant and nursing mothers, and adolescent girls in aspirational districts.",
        "eligibility_rules": [
            "Resident within the catchment area of a local Anganwadi Centre"
        ],
        "required_documents": [
            "Child's birth registration / MCP Card",
            "Aadhaar Card of mother / guardian"
        ],
        "benefits_text": "Daily Take-Home Rations (THR) / hot cooked meals, growth monitoring, micro-nutrient fortification, and referral to Nutrition Rehabilitation Centres (NRC).",
        "covered_treatments": ["Malnutrition management", "Supplementary nutrition", "Child growth monitoring"],
        "official_website": "https://wcd.gov.in/",
        "application_process": "Enroll at the neighborhood Anganwadi Centre through the Anganwadi Worker (AWW).",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 50,
        "income_limit": "Universal at Anganwadis",
        "match_tags": ["poshan", "anganwadi", "nutrition", "malnutrition", "child", "pregnant"],
        "color": "green"
    },
    {
        "name": "Scheme for Adolescent Girls (SAG)",
        "short_tag": "SAG",
        "category": "Adolescent Nutrition & Development",
        "govt_level": "Central Government",
        "description": "Centrally sponsored scheme empowering out-of-school adolescent girls aged 11–14 with nutritional support, iron-folic acid, life skills, and hygiene education.",
        "who_benefits": "Out-of-school adolescent girls aged 11 to 14 years.",
        "eligibility_rules": [
            "Girls aged 11 to 14 years who have dropped out of formal schooling"
        ],
        "required_documents": [
            "Age proof / Aadhaar Card",
            "Anganwadi registration form"
        ],
        "benefits_text": "Supplementary nutrition providing 600 calories and 18-20g protein per day, weekly iron-folic acid tablets, and mainstreaming into school.",
        "covered_treatments": ["Nutrition", "Anemia prevention", "Health education"],
        "official_website": "https://wcd.gov.in/",
        "application_process": "Register at the nearest Anganwadi centre with the help of Anganwadi Worker.",
        "states_applicable": "All",
        "age_min": 11,
        "age_max": 14,
        "income_limit": "Targeted to out-of-school adolescent girls",
        "match_tags": ["sag", "adolescent girls", "nutrition", "anemia", "anganwadi"],
        "color": "pink"
    },
    {
        "name": "Mission Indradhanush (Intensified Mission Indradhanush)",
        "short_tag": "Mission Indradhanush",
        "category": "Immunization Outreach",
        "govt_level": "Central Government",
        "description": "Special immunization drive ensuring 100% full immunization coverage for unreached, drop-out, and left-out children and pregnant women in high-risk pockets.",
        "who_benefits": "Children under 2 years and pregnant women who missed routine vaccine doses.",
        "eligibility_rules": [
            "Children under 2 years or pregnant women with overdue immunization doses"
        ],
        "required_documents": [
            "Vaccination record card / MCP card (if available, otherwise head-to-head tracking)"
        ],
        "benefits_text": "Catch-up vaccination sessions in underserved rural hamlets and urban slums, free tracking and administration of missed vaccine doses.",
        "covered_treatments": ["Vaccination", "Child healthcare", "Preventive outreach"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Attend mobile outreach immunization sessions organized in the locality or contact ASHA worker.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 5,
        "income_limit": "Universal — Free for all",
        "match_tags": ["indradhanush", "vaccine", "immunization", "catch-up", "child"],
        "color": "green"
    },
    {
        "name": "Navjaat Shishu Suraksha Karyakram (NSSK)",
        "short_tag": "NSSK",
        "category": "Newborn Care",
        "govt_level": "Central Government",
        "description": "Standardized newborn resuscitation and essential newborn care programme reducing neonatal mortality through specialized birth-point medical interventions.",
        "who_benefits": "Newborn babies born in or referred to public health facilities, especially those with birth asphyxia or hypothermia.",
        "eligibility_rules": [
            "All newborn babies delivered at public health institutions"
        ],
        "required_documents": [
            "Birth record at government maternity facility"
        ],
        "benefits_text": "Immediate neonatal resuscitation, warmth preservation, prevention of infection, and early breastfeeding support at delivery points.",
        "covered_treatments": ["Newborn care", "Neonatal resuscitation", "Pediatric emergency"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Delivered automatically by trained staff in all government labor rooms and Special Newborn Care Units (SNCUs).",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 1,
        "income_limit": "Universal — No charge",
        "match_tags": ["nssk", "newborn", "neonatal", "infant", "delivery room", "resuscitation"],
        "color": "pink"
    },
    {
        "name": "LaQshya — Labour Room Quality Improvement Initiative",
        "short_tag": "LaQshya",
        "category": "Maternal Healthcare Quality",
        "govt_level": "Central Government",
        "description": "National quality certification initiative aimed at improving the quality of care provided to women during labor and childbirth in maternity operation theatres.",
        "who_benefits": "Pregnant women and mothers undergoing delivery in certified public health facilities.",
        "eligibility_rules": [
            "Pregnant women admitted for institutional childbirth at participating government hospitals"
        ],
        "required_documents": [
            "MCP card and hospital admission slip"
        ],
        "benefits_text": "Respectful maternity care (RMC), pain relief during labor, dedicated triage, modern delivery suites, and emergency obstetric management.",
        "covered_treatments": ["Safe delivery", "Obstetric surgery", "Respectful maternity care"],
        "official_website": "https://nhm.gov.in/",
        "application_process": "Admitted to any LaQshya-certified district hospital, medical college, or Sub-District Hospital.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 50,
        "income_limit": "Universal — Zero charge",
        "match_tags": ["laqshya", "maternity", "delivery", "labour room", "quality care"],
        "color": "pink"
    },
    {
        "name": "National Oral Health Programme (NOHP)",
        "short_tag": "NOHP",
        "category": "Dental & Oral Healthcare",
        "govt_level": "Central Government",
        "description": "National initiative delivering community oral health education, dental screening, caries treatment, scaling, and oral cancer detection in public hospitals.",
        "who_benefits": "Children and adults seeking preventive, restorative, and surgical dental care.",
        "eligibility_rules": [
            "Patients presenting with dental caries, periodontal disease, tooth decay, or oral mucosal lesions"
        ],
        "required_documents": [
            "Identity proof if requested, hospital dental OPD slip"
        ],
        "benefits_text": "Free oral examinations, tooth extraction, dental fillings, scaling, oral cancer screening, and school oral health awareness.",
        "covered_treatments": ["Dental treatment", "Tooth extraction", "Oral cancer screening", "Preventive dentistry"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit the dental department or dental clinic at any government district hospital or CHC.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — Nominal / Free",
        "match_tags": ["nohp", "dental", "teeth", "oral health", "dentist", "caries"],
        "color": "teal"
    },
    {
        "name": "National Tobacco Control Programme (NTCP)",
        "short_tag": "NTCP",
        "category": "Tobacco Cessation & Preventive Health",
        "govt_level": "Central Government",
        "description": "National public health programme promoting tobacco cessation, nicotine replacement therapy (NRT) guidance, and public awareness on tobacco harms.",
        "who_benefits": "Individuals seeking to quit bidi, cigarette, gutkha, or smokeless tobacco use.",
        "eligibility_rules": [
            "Anyone seeking support to quit tobacco"
        ],
        "required_documents": [
            "No special paperwork required for counselling"
        ],
        "benefits_text": "Free behavioral counselling, nicotine cessation support, carbon monoxide breath analysis, and National Tobacco Quitline (1800-11-2356).",
        "covered_treatments": ["Tobacco cessation", "Counselling", "Addiction support", "Nicotine therapy"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Visit Tobacco Cessation Centre (TCC) at district hospital or dial National Quitline 1800-11-2356.",
        "states_applicable": "All",
        "age_min": 12,
        "age_max": 120,
        "income_limit": "Universal — Free",
        "match_tags": ["ntcp", "tobacco", "smoking", "quitline", "addiction", "cessation"],
        "color": "amber"
    },
    {
        "name": "Mission Vatsalya & Child Helpline 1098",
        "short_tag": "Mission Vatsalya",
        "category": "Child Protection & Emergency Support",
        "govt_level": "Central Government",
        "description": "Centrally sponsored umbrella scheme supporting child protection infrastructure, child care institutions, and emergency 24x7 Child Helpline 1098.",
        "who_benefits": "Children in need of care and protection, abandoned, orphaned, abused, or distressed children.",
        "eligibility_rules": [
            "Any child in distress or citizen reporting child welfare emergency"
        ],
        "required_documents": [
            "No documents required to place emergency call to 1098"
        ],
        "benefits_text": "Immediate emergency rescue, medical examination and treatment, shelter, legal support, and rehabilitation via Child Welfare Committees (CWCs).",
        "covered_treatments": ["Emergency healthcare", "Child protection", "Psychological trauma care"],
        "official_website": "https://wcd.gov.in/",
        "application_process": "Dial toll-free 1098 (24x7) or contact District Child Protection Unit (DCPU).",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 18,
        "income_limit": "Universal — Emergency free service",
        "match_tags": ["vatsalya", "child helpline", "1098", "child protection", "emergency child"],
        "color": "pink"
    },
    {
        "name": "Accessible India Campaign (Sugamya Bharat Abhiyan)",
        "short_tag": "Sugamya Bharat",
        "category": "Accessibility & Disability Inclusion",
        "govt_level": "Central Government",
        "description": "Nationwide flagship campaign ensuring barrier-free built environments, accessible public transport, and disabled-friendly hospitals.",
        "who_benefits": "Persons with disabilities, senior citizens, and people with temporary mobility limitations.",
        "eligibility_rules": [
            "Public infrastructure access initiative"
        ],
        "required_documents": [
            "No personal application needed for public accessibility"
        ],
        "benefits_text": "Wheelchair ramps, tactile pathways, accessible toilets, braille signage, and low-floor accessible transport in public hospitals.",
        "covered_treatments": ["Barrier-free healthcare", "Disability access", "Hospital accessibility"],
        "official_website": "https://depwd.gov.in/",
        "application_process": "Access facilities across government hospitals or report accessibility barriers via Sugamya Bharat App.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal",
        "match_tags": ["accessible india", "sugamya bharat", "disability access", "wheelchair ramp", "inclusion"],
        "color": "teal"
    },
    {
        "name": "National Programme for Prevention and Control of Snakebite Envenoming",
        "short_tag": "Snakebite Emergency",
        "category": "Emergency Healthcare & Toxicology",
        "govt_level": "Central Government",
        "description": "National initiative ensuring emergency availability of Anti-Snake Venom (ASV), timely protocol management, and reduction of snakebite mortality.",
        "who_benefits": "Rural communities, agricultural workers, and patients suffering from venomous snakebites.",
        "eligibility_rules": [
            "Any individual presenting with suspected or confirmed snakebite"
        ],
        "required_documents": [
            "No paperwork required for emergency medical intervention"
        ],
        "benefits_text": "Free polyvalent Anti-Snake Venom (ASV) administration, 20-minute whole blood clotting test (20WBCT), ventilator support, and emergency intensive care.",
        "covered_treatments": ["Accident and emergency care", "Snakebite envenoming", "Anti-snake venom (ASV)", "Intensive care"],
        "official_website": "https://mohfw.gov.in/",
        "application_process": "Transport patient immediately to the nearest government PHC, CHC, or civil hospital equipped with cold storage ASV.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — 100% Free emergency care",
        "match_tags": ["snakebite", "asv", "anti snake venom", "emergency", "toxicology", "rural"],
        "color": "amber"
    },
    {
        "name": "National Programme on Climate Change and Human Health (NPCCHH)",
        "short_tag": "NPCCHH",
        "category": "Climate & Environmental Health",
        "govt_level": "Central Government",
        "description": "Addresses health risks linked to heatwaves, extreme weather events, ambient air pollution, and climate-sensitive vector and water-borne diseases.",
        "who_benefits": "Vulnerable populations, outdoor manual laborers, elderly individuals, and pregnant women exposed to extreme heat or pollution.",
        "eligibility_rules": [
            "Patients suffering from heat exhaustion, heat stroke, or acute pollution-related respiratory exacerbations"
        ],
        "required_documents": [
            "Hospital casualty / emergency record"
        ],
        "benefits_text": "Dedicated heat-illness treatment wards, IV rehydration, heatwave early warnings, and public health advisories.",
        "covered_treatments": ["Heat stroke care", "Emergency hydration", "Respiratory illness", "Environmental health"],
        "official_website": "https://ncdc.mohfw.gov.in/",
        "application_process": "Seek emergency medical care at any district hospital with air-cooled heat-illness units.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — Free emergency service",
        "match_tags": ["npcchh", "climate change", "heat stroke", "air pollution", "heatwave", "emergency"],
        "color": "teal"
    },
    {
        "name": "National Programme for Prevention and Control of Leptospirosis",
        "short_tag": "Leptospirosis Control",
        "category": "Infectious & Zoonotic Disease",
        "govt_level": "Central Government",
        "description": "Public health surveillance and treatment programme for leptospirosis, especially in flood-prone and agricultural coastal regions.",
        "who_benefits": "Farmers, sanitation workers, people exposed to flood waters contaminated with rodent urine, and symptomatic patients.",
        "eligibility_rules": [
            "Clinical presentation of febrile jaundice, calf muscle tenderness, conjunctival suffusion, or post-flood exposure"
        ],
        "required_documents": [
            "Hospital registration and diagnostic test record"
        ],
        "benefits_text": "Free chemoprophylaxis (doxycycline), IgM ELISA laboratory diagnostics, and intravenous antibiotic therapy at public hospitals.",
        "covered_treatments": ["Leptospirosis treatment", "Infectious disease care", "Antibiotic therapy"],
        "official_website": "https://ncdc.mohfw.gov.in/",
        "application_process": "Visit the nearest primary health center or district hospital if symptoms appear after flood/water exposure.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — Free care",
        "match_tags": ["leptospirosis", "zoonotic", "flood fever", "rodent", "infectious disease"],
        "color": "green"
    },
    {
        "name": "National Programme for Prevention and Control of Zoonotic Diseases",
        "short_tag": "Zoonotic Diseases",
        "category": "Zoonotic Disease Prevention",
        "govt_level": "Central Government",
        "description": "National surveillance and inter-sectoral coordination addressing priority zoonotic diseases including Rabies, Scrub Typhus, Anthrax, Brucellosis, and KFD.",
        "who_benefits": "People exposed to animal bites (dog, monkey, bat) or tick/vector exposure in endemic regions.",
        "eligibility_rules": [
            "Animal bite victims (WHO Category II and III exposures) or patients with tick-borne scrub typhus"
        ],
        "required_documents": [
            "Hospital casualty record (emergency post-exposure prophylaxis is given immediately)"
        ],
        "benefits_text": "Free Anti-Rabies Vaccine (ARV) and Rabies Immunoglobulin (RIG) administration at all government anti-rabies clinics.",
        "covered_treatments": ["Rabies prophylaxis", "Anti-rabies vaccine (ARV)", "Scrub typhus care", "Zoonotic infection"],
        "official_website": "https://ncdc.mohfw.gov.in/",
        "application_process": "Wash animal bite wound immediately with soap and water for 15 minutes, visit nearest government hospital casualty for free ARV.",
        "states_applicable": "All",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — Free emergency care",
        "match_tags": ["zoonotic", "rabies", "arv", "dog bite", "animal bite", "scrub typhus"],
        "color": "amber"
    },
    {
        "name": "National Social Assistance Programme (NSAP — Disability & Widow Pension)",
        "short_tag": "NSAP Pension",
        "category": "Social Security & Disability Pension",
        "govt_level": "Central Government",
        "description": "Centrally sponsored welfare programme providing non-contributory monthly pensions to elderly, disabled persons, and widows from BPL households.",
        "who_benefits": "BPL senior citizens (IGNOAPS), BPL persons with severe disability (IGNDPS), and BPL widows (IGNWPS).",
        "eligibility_rules": [
            "BPL household verified under SECC/BPL list",
            "For IGNDPS: Age 18–79 with 80% or severe multiple disability",
            "For IGNOAPS: Age 60 and above",
            "For IGNWPS: Widows aged 40–79"
        ],
        "required_documents": [
            "BPL Card / Income Certificate",
            "Disability Certificate / UDID Card (for disability pension)",
            "Husband's Death Certificate (for widow pension)",
            "Aadhaar Card and Bank account passbook"
        ],
        "benefits_text": "Monthly direct benefit transfer (DBT) pension ranging from ₹300 to ₹1,000+ depending on state top-up, aiding medical and living subsistence.",
        "covered_treatments": ["Social subsistence", "Disability pension", "Elderly support", "Widow welfare"],
        "official_website": "https://nsap.nic.in/",
        "application_process": "Apply online via nsap.nic.in or submit application to the Block Development Officer (BDO) / Tahsildar.",
        "states_applicable": "All",
        "age_min": 18,
        "age_max": 120,
        "income_limit": "Below Poverty Line (BPL)",
        "match_tags": ["nsap", "pension", "disability pension", "widow pension", "bpl", "social security"],
        "color": "blue"
    },
    {
        "name": "Maharashtra Emergency Medical Services (MEMS — 108 Ambulance)",
        "short_tag": "MEMS 108",
        "category": "Emergency Healthcare & Transport",
        "govt_level": "State Government (Maharashtra)",
        "description": "Maharashtra state's 24x7 emergency medical response service delivering free dial 108 Basic and Advanced Life Support ambulances with onboard medical officers.",
        "who_benefits": "Anyone in Maharashtra experiencing acute medical emergencies, cardiac arrest, trauma, stroke, or obstetric emergencies.",
        "eligibility_rules": [
            "Any medical emergency within the territory of Maharashtra"
        ],
        "required_documents": [
            "Zero documentation required — just dial 108"
        ],
        "benefits_text": "100% free emergency ambulance dispatch with oxygen, ventilator, defibrillator, emergency drugs, and rapid transit to empanelled emergency hospital.",
        "covered_treatments": ["Accident and emergency care", "Cardiac emergency", "Maternity emergency transport", "Trauma care"],
        "official_website": "https://arogya.maharashtra.gov.in/",
        "application_process": "Dial 108 immediately from any mobile phone or landline in Maharashtra.",
        "states_applicable": "Maharashtra",
        "age_min": 0,
        "age_max": 120,
        "income_limit": "Universal — 100% Free",
        "match_tags": ["mems", "108 ambulance", "maharashtra", "emergency", "cardiac emergency", "trauma"],
        "color": "amber"
    }
]

def seed_admin_schemes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Ensure added_by column exists
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(schemes)").fetchall()]
    if "added_by" not in cols:
        cursor.execute("ALTER TABLE schemes ADD COLUMN added_by TEXT NOT NULL DEFAULT 'Administrator'")
        conn.commit()

    added_count = 0
    updated_count = 0

    for s in NEW_ADMIN_SCHEMES:
        name = s["name"]
        short_tag = s.get("short_tag", "")
        # Check if already exists by exact name or short tag
        existing = cursor.execute(
            "SELECT id FROM schemes WHERE name = ? OR (short_tag = ? AND short_tag != '')",
            (name, short_tag)
        ).fetchone()

        elig_rules_json = json.dumps(s.get("eligibility_rules", []))
        req_docs_json = json.dumps(s.get("required_documents", []))
        treatments_json = json.dumps(s.get("covered_treatments", []))
        match_tags_json = json.dumps(s.get("match_tags", []))

        if existing:
            # Update and mark as added_by Administrator
            cursor.execute("""
                UPDATE schemes SET
                    name = ?, short_tag = ?, category = ?, govt_level = ?,
                    description = ?, who_benefits = ?, eligibility_rules = ?,
                    required_documents = ?, benefits_text = ?, covered_treatments = ?,
                    official_website = ?, application_process = ?, states_applicable = ?,
                    age_min = ?, age_max = ?, income_limit = ?, match_tags = ?,
                    color = ?, added_by = 'Administrator', updated_at = datetime('now')
                WHERE id = ?
            """, (
                name, short_tag, s.get("category", "General"), s.get("govt_level", "Central Government"),
                s.get("description", ""), s.get("who_benefits", ""), elig_rules_json,
                req_docs_json, s.get("benefits_text", ""), treatments_json,
                s.get("official_website", ""), s.get("application_process", ""), s.get("states_applicable", "All"),
                s.get("age_min", 0), s.get("age_max", 120), s.get("income_limit", "Universal"),
                match_tags_json, s.get("color", "blue"), existing["id"]
            ))
            updated_count += 1
        else:
            # Insert brand new scheme with added_by = 'Administrator'
            cursor.execute("""
                INSERT INTO schemes (
                    name, short_tag, category, govt_level, description, who_benefits,
                    eligibility_rules, required_documents, benefits_text, covered_treatments,
                    official_website, application_process, states_applicable,
                    age_min, age_max, income_limit, match_tags, is_active, color, added_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'Administrator')
            """, (
                name, short_tag, s.get("category", "General"), s.get("govt_level", "Central Government"),
                s.get("description", ""), s.get("who_benefits", ""), elig_rules_json,
                req_docs_json, s.get("benefits_text", ""), treatments_json,
                s.get("official_website", ""), s.get("application_process", ""), s.get("states_applicable", "All"),
                s.get("age_min", 0), s.get("age_max", 120), s.get("income_limit", "Universal"),
                match_tags_json, s.get("color", "blue")
            ))
            added_count += 1

    # Also update any existing schemes without added_by to 'Administrator'
    cursor.execute("UPDATE schemes SET added_by = 'Administrator' WHERE added_by IS NULL OR added_by = ''")
    conn.commit()

    total = cursor.execute("SELECT COUNT(*) FROM schemes").fetchone()[0]
    active = cursor.execute("SELECT COUNT(*) FROM schemes WHERE is_active=1").fetchone()[0]
    conn.close()

    print(f"Admin Schemes Seeding Completed:")
    print(f" - Inserted new: {added_count}")
    print(f" - Updated/Enriched: {updated_count}")
    print(f" - Total Schemes in DB: {total} (Active: {active})")

if __name__ == "__main__":
    seed_admin_schemes()
