"""
scheme_recommender.py — SwasthyaSetu AI
Smart Progressive Healthcare Scheme Recommendation Engine.

Evaluates user demographic, location, socioeconomic, and medical need inputs
against active government healthcare schemes stored in the database.
Produces structured recommendations with status labels:
- Potential Match
- More Information Needed (with single targeted contextual question)
- Eligibility Not Yet Verified
- Not a Match Based on Available Information
"""

import json
from db import get_all_schemes


def recommend_schemes_for_user(user: dict, profile: dict = None) -> list:
    """
    Generate tailored healthcare scheme recommendations using currently available
    user profile details. Does not require a 100% completed profile.
    """
    if not user:
        return []

    profile = profile or {}
    all_schemes = get_all_schemes(active_only=True)
    results = []

    # Extract user & profile attributes safely
    user_state = (user.get("state") or "").strip().lower()
    user_district = (user.get("district") or "").strip().lower()
    user_name = user.get("name", "")

    # Profile details
    user_age = profile.get("age")
    user_gender = (profile.get("gender") or "").strip().lower()
    beneficiary = (profile.get("beneficiary_type") or "myself").strip().lower()
    income = (profile.get("income_range") or "").strip().lower()
    ration_card = (profile.get("ration_card_category") or "").strip().lower()
    has_health_card = (profile.get("has_health_card") or "").strip().lower()
    other_coverage = (profile.get("other_coverage") or "").strip().lower()
    occupation = (profile.get("occupation") or "").strip().lower()
    welfare_reg = (profile.get("welfare_board_reg") or "").strip().lower()
    special_cat = (profile.get("special_category") or "").strip().lower()

    # Healthcare needs (list of strings)
    needs = profile.get("healthcare_needs", [])
    if isinstance(needs, str):
        try:
            needs = json.loads(needs)
        except Exception:
            needs = [needs]
    user_needs = [n.lower() for n in needs]

    # Treatment context (dict)
    ctx = profile.get("treatment_context", {})
    if isinstance(ctx, str):
        try:
            ctx = json.loads(ctx)
        except Exception:
            ctx = {}

    # Documents available (dict)
    docs_avail = profile.get("document_availability", {})
    if isinstance(docs_avail, str):
        try:
            docs_avail = json.loads(docs_avail)
        except Exception:
            docs_avail = {}

    for s in all_schemes:
        score = 0
        reasons = []
        missing_question = None
        status = "Eligibility Not Yet Verified"

        name = s.get("name", "")
        name_lower = name.lower()
        desc_lower = (s.get("description") or "").lower()
        who_lower = (s.get("who_benefits") or "").lower()
        cat_lower = (s.get("category") or "").lower()
        combined_text = f"{name_lower} {desc_lower} {who_lower} {cat_lower}"

        # Parse scheme rules & documents
        try:
            elig_rules = json.loads(s.get("eligibility_rules", "[]") or "[]")
        except Exception:
            elig_rules = []
        try:
            req_docs = json.loads(s.get("required_documents", "[]") or "[]")
        except Exception:
            req_docs = []
        try:
            match_tags = json.loads(s.get("match_tags", "[]") or "[]")
        except Exception:
            match_tags = []

        states_applicable = (s.get("states_applicable") or "All").strip()
        states_app_lower = states_applicable.lower()

        # -------------------------------------------------------------
        # 1. State / Jurisdiction Check (Hard exclusion for other states)
        # -------------------------------------------------------------
        if states_app_lower not in ["all", "all india", "universal"]:
            applicable_list = [st.strip().lower() for st in states_applicable.split(",")]
            if user_state and not any(user_state in st or st in user_state for st in applicable_list):
                continue  # Skip: State-specific scheme for a different state
            elif user_state:
                score += 55
                reasons.append(f"Premier state healthcare programme for residents of {user.get('state')}")

        # -------------------------------------------------------------
        # 2. Healthcare Needs Matching (Primary Driver)
        # -------------------------------------------------------------
        need_match = False
        treatment_map = {
            "hospital": ["hospitalisation", "hospitalization", "surgery", "inpatient", "tertiary", "pm-jay", "mjpjay"],
            "surgery": ["surgery", "hospitalisation", "hospitalization", "inpatient", "pm-jay", "mjpjay"],
            "cancer": ["cancer", "oncology", "malignant"],
            "heart": ["heart", "cardiac", "cardio", "bypass", "stent"],
            "kidney": ["kidney", "renal", "dialysis"],
            "dialysis": ["dialysis", "kidney", "renal", "pmndp"],
            "pregnancy": ["pregnancy", "maternity", "delivery", "mother", "maternal", "surakshit", "pmmvy"],
            "maternity": ["maternity", "pregnancy", "delivery", "mother", "maternal", "surakshit", "pmmvy"],
            "child": ["child", "pediatric", "infant", "newborn", "rbsk", "indradhanush"],
            "vaccination": ["vaccination", "immunization", "indradhanush"],
            "medicine": ["medicine", "pharmacy", "janaushadhi", "drug"],
            "diagnostic": ["diagnostic", "test", "laboratory", "x-ray", "screening"],
            "mental": ["mental", "tele-manas", "psychiatric", "depression"],
            "tb": ["tuberculosis", "tb", "nikshay", "infectious"],
            "eye": ["eye", "vision", "cataract", "cornea", "glasses"],
            "disability": ["disability", "divyang", "assistive", "adip", "niramaya"],
            "senior": ["senior", "elderly", "vay vandana", "old age", "geriatric"],
            "financial": ["ran", "rashtriya arogya nidhi", "financial assistance", "expensive", "relief fund", "bpl"],
            "expensive": ["ran", "rashtriya arogya nidhi", "financial assistance", "expensive", "relief fund", "life-threatening"],
        }

        matched_user_needs = []
        for user_need in user_needs:
            for key, keywords in treatment_map.items():
                if key in user_need:
                    if any(kw in combined_text for kw in keywords):
                        matched_user_needs.append(key)
                        need_match = True
                        break

        if need_match:
            score += 55
            distinct_needs = list(set(matched_user_needs))[:2]
            reasons.append(f"Directly addresses your care need for {', '.join(distinct_needs).title()}")
        elif "exploring" in " ".join(user_needs) or not user_needs:
            # User is just exploring; baseline candidate
            score += 10

        # General hospitalization / assurance coverage for major schemes
        if any("hospital" in un or "surgery" in un or "insurance" in un for un in user_needs):
            if "hospitalization" in combined_text or "hospitalisation" in combined_text or "assurance" in cat_lower or "pm-jay" in name_lower or "mjpjay" in name_lower:
                score += 25
                if not any("hospitalization" in r.lower() for r in reasons):
                    reasons.append("Covers inpatient hospitalization and specialized care")

        # Specific RAN & PM-JAY emergency & financial coverage boost
        if ("ran" in name_lower or "rashtriya arogya nidhi" in name_lower):
            if any("financial" in un or "expensive" in un or "hospital" in un or "surgery" in un for un in user_needs):
                score += 35
                reasons.append("Provides emergency financial assistance for super-specialty treatment")

        if ("pm-jay" in name_lower or "pradhan mantri jan arogya" in name_lower):
            if any("hospital" in un or "surgery" in un or "financial" in un for un in user_needs):
                score += 35
                reasons.append("Cashless secondary and tertiary hospitalisation coverage up to ₹5 lakh per family")

        # Clinical follow-up questions from Section 7 (Prioritized before generic questions)
        if any("dialysis" in un or "kidney" in un for un in user_needs) and ("dialysis" in combined_text or "pmndp" in combined_text or "kidney" in combined_text):
            if not ctx.get("dialysis_prescribed"):
                missing_question = {
                    "key": "dialysis_prescribed",
                    "text": "Has dialysis been prescribed by a doctor?",
                    "options": ["Yes", "No", "Not sure"]
                }
        elif any("pregnancy" in un or "maternity" in un for un in user_needs) and ("pregnancy" in combined_text or "maternity" in combined_text or "pmmvy" in combined_text):
            if not ctx.get("pregnancy_stage"):
                missing_question = {
                    "key": "pregnancy_stage",
                    "text": "Are you registered at your local Anganwadi / Health Centre (MCP card issued)?",
                    "options": ["Yes", "No", "Not sure"]
                }
        elif (any("disability" in un for un in user_needs) or special_cat == "person with disability") and ("disability" in combined_text or "adip" in combined_text):
            if not ctx.get("disability_cert_status"):
                missing_question = {
                    "key": "disability_cert_status",
                    "text": "Do you hold an accepted disability certificate or UDID card?",
                    "options": ["Yes", "No", "In progress"]
                }

        # -------------------------------------------------------------
        # 3. Demographic & Age Matching
        # -------------------------------------------------------------
        if user_age is not None:
            if user_age >= 70:
                if "70" in name_lower or "vay vandana" in name_lower:
                    score += 40
                    reasons.append("Universal health assurance card for senior citizens aged 70+ irrespective of income")
                elif "senior" in combined_text or "elderly" in combined_text:
                    score += 15
                    reasons.append("Senior citizen benefits available under this programme")
            elif user_age < 18:
                if "child" in combined_text or "rbsk" in name_lower:
                    score += 25
                    reasons.append("Covers child health screening and pediatric services")
        elif special_cat == "senior citizen":
            if "70" in name_lower or "vay vandana" in name_lower or "senior" in combined_text:
                score += 25
                reasons.append("Designed for senior citizens")

        # -------------------------------------------------------------
        # 4. Gender & Maternal Circumstance Matching
        # -------------------------------------------------------------
        if user_gender == "female" or special_cat == "pregnant woman":
            if any(term in name_lower for term in ["maternity", "matru", "janani", "surakshit", "pmmvy", "jsy"]):
                score += 30
                reasons.append("Maternal healthcare scheme offering cashless delivery and financial incentives")
        elif user_gender == "male":
            if any(term in name_lower for term in ["matru", "maternity", "surakshit matritva"]):
                continue  # Skip: Maternal only

        # -------------------------------------------------------------
        # 5. Occupation & Employment Matching
        # -------------------------------------------------------------
        if occupation == "salaried employee":
            if "cghs" in name_lower and ("govt" in other_coverage or "central" in who_lower):
                score += 45
                reasons.append("Central government employees and pensioners are eligible for CGHS")
            elif "esic" in name_lower or "employees' state" in name_lower:
                score += 30
                reasons.append("Covers organized sector employees covered under ESIC")
        elif occupation == "construction worker":
            if "bocw" in combined_text or "construction" in combined_text:
                score += 40
                reasons.append("Registered construction workers qualify for welfare board medical assistance")
                if welfare_reg != "yes":
                    missing_question = {
                        "key": "welfare_board_reg",
                        "text": "Are you registered with the Building & Other Construction Workers (BOCW) Board?",
                        "options": ["Yes", "No", "Not sure"]
                    }
        elif occupation == "farmer":
            if "farmer" in who_lower or "shetkari" in who_lower:
                score += 25
                reasons.append("Special coverage provisions for farming families")

        if special_cat == "person with disability":
            if "disability" in combined_text or "adip" in name_lower or "niramaya" in name_lower:
                score += 40
                reasons.append("Disability-specific health assurance and assistive equipment support")

        # -------------------------------------------------------------
        # 6. Socioeconomic / Ration Card / Income Matching
        # -------------------------------------------------------------
        is_bpl_likely = any(rc in ration_card for rc in ["yellow", "antyodaya", "aay", "phh", "priority"]) or "below" in income or "1 lakh" in income
        if "bpl" in who_lower or "low-income" in who_lower or "poor" in who_lower:
            if is_bpl_likely:
                score += 20
                reasons.append("Matches your household income/ration card criteria")
            elif ration_card in ["not sure", "prefer not to say", ""] and income in ["prefer not to say", ""]:
                # Missing info that could clarify match
                if not missing_question:
                    missing_question = {
                        "key": "ration_card_category",
                        "text": "Do you hold a Yellow, Antyodaya (AAY), or Priority (PHH) Ration Card?",
                        "options": ["Yes (Yellow / AAY / PHH)", "No (White / Above Poverty Line)", "Not sure"]
                    }

        # -------------------------------------------------------------
        # 7. Existing Health Card Check
        # -------------------------------------------------------------
        if has_health_card == "yes":
            if "pm-jay" in name_lower or "ayushman" in name_lower or "mjpjay" in name_lower:
                score += 15
                reasons.append("You already hold a government health card accepted at empanelled network hospitals")
        elif has_health_card in ["no", "not sure", ""]:
            if ("pm-jay" in name_lower or "mjpjay" in name_lower) and not missing_question:
                missing_question = {
                    "key": "has_health_card",
                    "text": "Do you already possess an Ayushman Card (PM-JAY) or state health card?",
                    "options": ["Yes", "No", "Not sure"]
                }

        # Universal national schemes always provide a safe baseline candidate
        if any(term in desc_lower for term in ["universal", "all residents", "all patients", "everyone"]):
            score += 15
            if not reasons:
                reasons.append("Open to all residents regardless of income ceiling")

        # -------------------------------------------------------------
        # 8. Status Label Assignment
        # -------------------------------------------------------------
        if score >= 45:
            status = "Potential Match"
        elif missing_question is not None or (score >= 25 and not need_match):
            status = "More Information Needed"
        elif score >= 20:
            status = "Eligibility Not Yet Verified"
        else:
            status = "Not a Match Based on Available Information"

        # Discard irrelevant or non-matching schemes
        if score < 15 or status == "Not a Match Based on Available Information":
            continue

        score = min(100, score)

        if not reasons:
            reasons = [f"Applicable for {user.get('state', 'your state')} residents seeking healthcare support"]

        cond_list = elig_rules[:4] if elig_rules else ["Confirm eligibility with local government healthcare authority"]
        doc_list = req_docs[:5] if req_docs else ["Aadhaar Card", "Prescription / Doctor's note"]

        results.append({
            "id": s["id"],
            "name": name,
            "short_tag": s.get("short_tag") or name[:16],
            "category": s.get("category", "General"),
            "govt_level": s.get("govt_level", "Central Government"),
            "description": s.get("description", ""),
            "match_status": status,
            "why_it_matches": reasons[:4],
            "important_conditions": cond_list,
            "eligibility_rules": cond_list,
            "documents_required": doc_list,
            "required_documents": doc_list,
            "missing_info_question": missing_question,
            "official_website": s.get("official_website", "https://mohfw.gov.in/"),
            "application_process": s.get("application_process", "Visit the nearest empanelled hospital or scheme desk"),
            "states_applicable": s.get("states_applicable", "All India"),
            "relevance_score": score
        })

    # Sort candidates by relevance score descending
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:40]  # Return top relevant matches

