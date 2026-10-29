"""
ai_assistant.py - SwasthyaSetu AI Conversational Engine
Provides intelligent, multi-turn, context-aware conversational guidance
for Indian healthcare schemes, eligibility, required documents, hospital beds,
and emergency health assistance.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from db import get_all_schemes, get_empanelled_hospitals


def _normalize(text: str) -> str:
    """Normalize input text for matching."""
    return re.sub(r"[^\w\s]", " ", (text or "").lower()).strip()


def extract_context(history: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Extract topic context from previous conversation turns."""
    ctx = {
        "last_scheme": None,
        "last_condition": None,
        "last_intent": None
    }
    if not history:
        return ctx

    for turn in reversed(history[-4:]):
        text = _normalize(turn.get("text", ""))
        if not ctx["last_scheme"]:
            if "pmjay" in text or "ayushman" in text:
                ctx["last_scheme"] = "pmjay"
            elif "mjpjay" in text or "jyotirao" in text or "phule" in text:
                ctx["last_scheme"] = "mjpjay"
            elif "ran" in text or "arogya nidhi" in text:
                ctx["last_scheme"] = "ran"
            elif "vay vandana" in text or "senior" in text or "70" in text:
                ctx["last_scheme"] = "vay_vandana"
            elif "maternity" in text or "jssk" in text or "pmsma" in text or "pregnancy" in text:
                ctx["last_scheme"] = "maternity"
            elif "dialysis" in text:
                ctx["last_scheme"] = "dialysis"

        if not ctx["last_condition"]:
            for cond in ["cancer", "heart", "dialysis", "kidney", "surgery", "pregnancy", "delivery", "neuro", "brain", "tb", "tuberculosis", "cataract"]:
                if cond in text:
                    ctx["last_condition"] = cond
                    break

    return ctx


def detect_user_language(text: str, session_lang: Optional[str] = None) -> str:
    """Detect if query or session is in Marathi, Hindi, or English."""
    if not text:
        return session_lang if session_lang in ["hi", "mr"] else "en"

    # Marathi detection patterns (Devanagari keywords or Latin transliteration)
    marathi_patterns = [
        r"आहे", r"नाही", r"काय", r"कसे", r"करावे", r"मिळेल", r"माहिती", r"द्या",
        r"रुग्णालय", r"मोफत", r"पाहिजे", r"कागदपत्रे", r"दाखला", r"तपासणी",
        r"उपचार", r"मदत", r"नमस्कार", r"योजना", r"हॉस्पिटल", r"बेड"
    ]
    for pat in marathi_patterns:
        if re.search(pat, text):
            return "mr"

    # Hindi detection patterns
    hindi_patterns = [
        r"है", r"हैं", r"क्या", r"कैसे", r"करें", r"मिलेगा", r"चाहिए",
        r"अस्पताल", r"मुफ्त", r"दस्तावेज़", r"दस्तावेज", r"इलाज", r"मदद",
        r"नमस्ते", r"बताइए", r"बताओ", r"कार्ड"
    ]
    for pat in hindi_patterns:
        if re.search(pat, text):
            return "hi"

    # Check Devanagari script presence
    devanagari_count = len(re.findall(r"[\u0900-\u097f]", text))
    if devanagari_count >= 2:
        return session_lang if session_lang in ["hi", "mr"] else "hi"

    # Transliterated Marathi
    if any(w in text.lower() for w in ["kasa", "ahe", "pahije", "sangaa", "rugnalay", "mofat", "yojana"]):
        return "mr"
    # Transliterated Hindi
    if any(w in text.lower() for w in ["kaise", "chahiye", "batao", "kya", "madad", "hoga"]):
        return "hi"

    return session_lang if session_lang in ["hi", "mr"] else "en"


def generate_assistant_reply(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    session_lang: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main conversational agent for SwasthyaSetu AI.
    Processes user query and conversation history, returns conversational text,
    suggested prompt chips, and quick navigational links.
    Supports English, Hindi (hi), and Marathi (mr).
    """
    clean_msg = _normalize(user_message)
    context = extract_context(history)
    lang = detect_user_language(user_message, session_lang)

    # User profile context if available
    user_name = (user_profile.get("name") or "Beneficiary").split()[0] if user_profile else None
    user_state = user_profile.get("state") or "Maharashtra" if user_profile else None
    user_district = user_profile.get("district") or "Chhatrapati Sambhajinagar" if user_profile else None

    # Default result structure
    reply_text = ""
    chips = []
    links = []

    # -------------------------------------------------------------------------
    # 1. EMERGENCY & CRITICAL QUERIES
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["emergency", "ambulance", "urgent", "accident", "heart attack", "critical", "casualty", "108"]) or \
       any(k in user_message for k in ["तातडी", "आपत्कालीन", "रुग्णवाहिका", "ॲम्ब्युलन्स", "अपघात", "इमरजेंसी", "एम्बुलेंस"]):
        if lang == "mr":
            reply_text = (
                "🚨 **तात्काळ आपत्कालीन वैद्यकीय मदत**\n\n"
                "तातडीच्या उपचारासाठी त्वरित खालील **टोल-फ्री आपत्कालीन क्रमांकांवर** संपर्क साधा:\n\n"
                "• **108** — मोफत आपत्कालीन रुग्णवाहिका सेवा (24x7 संपूर्ण भारतात)\n"
                "• **102** — गरोदर माता व नवजात बालकांसाठी मोफत रुग्णवाहिका\n"
                "• **112** — सर्वसमावेशक राष्ट्रीय आपत्कालीन क्रमांक\n\n"
                "📍 **तातडीने काय करावे:**\n"
                "जवळच्या शासकीय रुग्णालयाच्या अपघात विभागात (Casualty) जा (उदा. **GMCH घाटी रुग्णालय**).\n\n"
                "💡 **महत्त्वाची माहिती:** आयुष्मान भारत (PM-JAY) आणि महात्मा ज्योतिराव फुले जन आरोग्य योजना (MJPJAY) अंतर्गत आपत्कालीन भरतीला प्राधान्य दिले जाते. "
                "भरती झाल्यावर 24 ते 48 तासांच्या आत आरोग्यमित्र डेस्कवर रेशन कार्ड किंवा आधार कार्ड दाखवून 100% कॅशलेस उपचार मिळवा."
            )
            chips = ["ICU बेड्स असलेली रुग्णालये शोधा", "आपत्कालीन प्रवेशासाठी कागदपत्रे", "PM-JAY योजना माहिती"]
            links = [{"text": "संलग्न रुग्णालये आणि बेड उपलब्धता तपासा", "url": "/hospitals"}]
        elif lang == "hi":
            reply_text = (
                "🚨 **आपातकालीन चिकित्सा सहायता (Emergency)**\n\n"
                "यदि किसी को तुरंत आपातकालीन चिकित्सा सहायता चाहिए, तो इन **टोल-फ्री नंबरों** पर तुरंत कॉल करें:\n\n"
                "• **108** — मुफ्त आपातकालीन एम्बुलेंस सेवा (24x7 पूरे भारत में)\n"
                "• **102** — गर्भवती महिलाओं और नवजात शिशुओं के लिए मुफ्त एम्बुलेंस\n"
                "• **112** — राष्ट्रीय आपातकालीन हेल्पलाइन\n\n"
                "📍 **अस्पताल में तुरंत क्या करें:**\n"
                "निकटतम सरकारी अस्पताल (जैसे **GMCH घाटी अस्पताल**) के इमरजेंसी/कैजुअल्टी वार्ड में जाएं।\n\n"
                "💡 **राहत की बात:** PM-JAY और MJPJAY के तहत आपातकालीन मामलों में पहले इलाज शुरू होता है! "
                "मरीज के परिजन 24 से 48 घंटे के भीतर आरोग्यमित्र डेस्क पर आधार या राशन कार्ड दिखाकर पूरी तरह कैशलेस उपचार प्राप्त कर सकते हैं।"
            )
            chips = ["ICU बेड वाले निकटतम अस्पताल", "आपातकालीन भर्ती हेतु आवश्यक दस्तावेज़", "PM-JAY योजना विवरण"]
            links = [{"text": "अस्पतालों की सूची और लाइव बेड देखें", "url": "/hospitals"}]
        else:
            reply_text = (
                "🚨 **URGENT EMERGENCY ASSISTANCE**\n\n"
                "If someone needs immediate emergency medical attention, call these **toll-free emergency helplines** right away:\n\n"
                "• **108** — Free Emergency Medical Ambulance Service (24x7 pan-India)\n"
                "• **102** — Free Ambulance for Pregnant Mothers & Newborns\n"
                "• **112** — All-in-One National Emergency Helpline\n\n"
                "📍 **Immediate Hospital Action:**\n"
                "Go straight to the Casualty/Emergency Department of the nearest government hospital (e.g., **Government Medical College & Hospital / घाटी रुग्णालय**).\n\n"
                "💡 **Good news:** Under Ayushman Bharat (PM-JAY) and MJPJAY, emergency admissions are treated first! "
                "Your family can present your Aadhaar or Ration Card at the **Aarogyamitra desk** within 24 to 48 hours of admission to get 100% cashless treatment."
            )
            chips = ["Find nearby hospital with ICU beds", "What documents for emergency admission?", "PM-JAY scheme coverage"]
            links = [{"text": "View Empanelled Hospitals & Bed Status", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 2. GREETINGS & INTRODUCTION
    # -------------------------------------------------------------------------
    if any(clean_msg == k or clean_msg.startswith(k + " ") for k in ["hi", "hello", "namaste", "hey", "good morning", "good evening", "good afternoon", "halo", "namaskar"]) or \
       any(k in user_message for k in ["नमस्ते", "नमस्कार", "हेलो"]):
        if lang == "mr":
            greeting_lead = f"नमस्कार {user_name}! 🙏" if user_name else "नमस्कार! 🙏 SwasthyaSetu AI मध्ये आपले स्वागत आहे."
            location_note = f" तुम्ही **{user_district}, {user_state}** येथून संपर्क साधत आहात." if user_profile and user_district else ""
            reply_text = (
                f"{greeting_lead}{location_note}\n\n"
                "मी तुमचा **AI आरोग्य योजना मार्गदर्शक** आहे. मी खालील विषयांवर तुम्हाला संपूर्ण मार्गदर्शन करू शकतो:\n\n"
                "1. **योग्य योजना शोधणे:** तुमचे वय, उत्पन्न व आजारानुसार योग्य सरकारी आरोग्य योजनांची माहिती.\n"
                "2. **मोफत व कॅशलेस उपचार:** कॅन्सर, हृदयविकार, डायलिसिस, प्रसूती यांसाठी ₹5 लाखांपर्यंतचे मोफत संरक्षण.\n"
                "3. **रुग्णालये व बेड्स:** जवळची संलग्न रुग्णालये आणि उपलब्ध ICU / जनरल बेड्सची थेट माहिती.\n"
                "4. **कागदपत्रांची यादी:** आयुष्मान कार्ड व आरोग्यमित्र नोंदणीसाठी आवश्यक कागदपत्रांची यादी.\n\n"
                "आज मी तुम्हाला व तुमच्या कुटुंबाला कशी मदत करू शकतो?"
            )
            chips = [
                "मी कोणत्या योजनांसाठी पात्र आहे?",
                "डायलिसिस मोफत आहे का?",
                "आयुष्मान कार्डसाठी कोणती कागदपत्रे लागतात?",
                "ICU बेड असलेली रुग्णालये शोधा"
            ]
            links = [
                {"text": "योजना शोधक सुरू करा", "url": "/schemes"},
                {"text": "रुग्णालये व बेड्स तपासा", "url": "/hospitals"}
            ]
        elif lang == "hi":
            greeting_lead = f"नमस्ते {user_name}! 🙏" if user_name else "नमस्ते! 🙏 SwasthyaSetu AI में आपका स्वागत है।"
            location_note = f" मैं देख पा रहा हूँ कि आप **{user_district}, {user_state}** से हैं।" if user_profile and user_district else ""
            reply_text = (
                f"{greeting_lead}{location_note}\n\n"
                "मैं आपका **AI स्वास्थ्य योजना सहायक** हूँ। मैं निम्नलिखित कार्यों में आपकी पूरी मदद कर सकता हूँ:\n\n"
                "1. **सही योजनाएं खोजना:** आपकी आयु, आय और बीमारी के अनुसार उपयुक्त सरकारी स्वास्थ्य योजनाएं।\n"
                "2. **मुफ्त व कैशलेस उपचार:** कैंसर, हार्ट सर्जरी, किडनी डायलिसिस, प्रसूति आदि के लिए ₹5 लाख तक का कैशलेस कवर।\n"
                "3. **अस्पताल और लाइव बेड:** पैनल में शामिल निकटतम अस्पताल और उपलब्ध ICU/जनरल बेड की स्थिति।\n"
                "4. **ज़रूरी दस्तावेज़:** आयुष्मान कार्ड और अस्पताल में भर्ती के लिए आवश्यक दस्तावेज़ों की चेकलिस्ट।\n\n"
                "आज मैं आपकी क्या सहायता कर सकता हूँ?"
            )
            chips = [
                "मैं किन योजनाओं के लिए पात्र हूँ?",
                "क्या डायलिसिस मुफ्त है?",
                "PM-JAY के लिए कौन से दस्तावेज़ चाहिए?",
                "ICU बेड वाले अस्पताल खोजें"
            ]
            links = [
                {"text": "योजना खोजक खोलें", "url": "/schemes"},
                {"text": "अस्पताल और बेड स्थिति देखें", "url": "/hospitals"}
            ]
        else:
            greeting_lead = f"Namaste {user_name}! 🙏" if user_name else "Namaste! 🙏 Welcome to SwasthyaSetu AI."
            location_note = f" I see you're in **{user_district}, {user_state}**." if user_profile and user_district else ""
            reply_text = (
                f"{greeting_lead}{location_note}\n\n"
                "I am your dedicated **AI Healthcare Scheme Guide**. I can help you with:\n\n"
                "1. **Discovering Schemes:** Finding government health schemes matching your age, income, and health condition.\n"
                "2. **Cashless Surgery & Treatments:** Checking coverage for cancer, cardiology, kidney dialysis, maternity, and more.\n"
                "3. **Hospital Finder & Live Beds:** Checking empanelled hospitals and available ICU/General beds.\n"
                "4. **Required Documents:** Step-by-step checklist for Ayushman card / Aarogyamitra registration.\n\n"
                "How can I assist your family today?"
            )
            chips = [
                "Which schemes am I eligible for?",
                "Find hospitals with ICU beds",
                "What documents are needed for PM-JAY?",
                "Is cancer or dialysis covered?"
            ]
            links = [
                {"text": "Launch Scheme Finder", "url": "/schemes"},
                {"text": "Hospital & Bed Finder", "url": "/hospitals"}
            ]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 3. WHO ARE YOU / IDENTITY
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["who are you", "what can you do", "help me", "what is this", "what do you do", "about you"]):
        reply_text = (
            "I am **SwasthyaSetu AI**, an intelligent digital healthcare assistant created to ensure every Indian citizen "
            "gets access to their rightful government healthcare benefits.\n\n"
            "I navigate major central and state schemes including **Ayushman Bharat (PM-JAY)**, **Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY)**, "
            "**Rashtriya Arogya Nidhi (RAN)**, **Ayushman Vay Vandana (70+ Seniors)**, and **Janani Shishu Suraksha Karyakram (JSSK)**.\n\n"
            "Feel free to ask questions in plain English or Hinglish about specific treatments, hospitals, documents, or eligibility!"
        )
        chips = ["Am I eligible for PM-JAY?", "Check hospital bed availability", "Check required documents"]
        links = [{"text": "Explore All Schemes", "url": "/schemes"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 4. LIVE HOSPITAL & BED AVAILABILITY QUERIES
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["hospital", "bed", "icu", "oxygen", "clinic", "doctor", "admit", "ghati", "gmch", "dhoot"]):
        try:
            hospitals = get_empanelled_hospitals()
        except Exception:
            hospitals = []

        if hospitals:
            hosp_snippets = []
            for h in hospitals[:3]:
                hosp_snippets.append(
                    f"🏥 **{h['name']}**\n"
                    f"   • Type: {h['hospital_type']} ({h['distance_km']} km away)\n"
                    f"   • Bed Availability: **{h['general_beds_available']} General Beds**, **{h['icu_beds_available']} ICU Beds**, **{h['oxygen_beds_available']} Oxygen Beds**\n"
                    f"   • Empanelled Schemes: {', '.join(h['schemes_empanelled'][:3])}\n"
                    f"   • Helpline: 📞 {h['phone']} (Emergency: {h['emergency_helpline']})"
                )

            reply_text = (
                f"Here are the accredited empanelled network hospitals nearest to you with **live bed availability**:\n\n"
                + "\n\n".join(hosp_snippets) +
                "\n\n📍 All hospitals are equipped with an on-site **Ayushman Mitra / Aarogyamitra helpdesk** to assist you with free scheme admissions."
            )
        else:
            reply_text = (
                "You can search and filter through our accredited empanelled hospitals, prioritized from closest to farthest distance, "
                "with live counts for General, ICU, and Oxygen beds."
            )

        chips = ["How do I get admitted under PM-JAY?", "What documents to take to hospital?", "Are medicines free at the hospital?"]
        links = [{"text": "Open Live Hospital Finder & Map", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 5. SPECIFIC SCHEMES
    # -------------------------------------------------------------------------
    # A) PM-JAY (Ayushman Bharat)
    if any(k in clean_msg for k in ["pmjay", "pm jay", "ayushman bharat", "ayushman card", "5 lakh", "500000"]):
        reply_text = (
            "📋 **Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY)**\n\n"
            "• **Coverage:** Up to **₹5,00,000 per family per year** on a floater basis.\n"
            "• **Cashless & Paperless:** Valid across 30,000+ public and private empanelled hospitals across India.\n"
            "• **Procedures Covered:** 1,949+ medical packages covering cardiology, cancer surgeries, chemotherapy, neurosurgery, orthopedics, ICU, pre-hospitalization (3 days) and post-hospitalization medicines (15 days).\n"
            "• **Who is Eligible:** Families identified in the SECC 2011 deprivation list, active Antyodaya (AAY) or Priority Household (PHH) ration card holders, and state-expanded beneficiary lists.\n"
            "• **How to Apply:** No fee required. Carry your **Aadhaar card** and **Ration card** to any empanelled hospital's **Ayushman Mitra** kiosk for instant biometric verification and Ayushman card creation."
        )
        chips = ["Which hospitals accept PM-JAY?", "What documents are required?", "Am I eligible?"]
        links = [
            {"text": "View PM-JAY Documents Checklist", "url": "/documents?scheme_id=pmjay"},
            {"text": "Find PM-JAY Empanelled Hospitals", "url": "/hospitals?scheme_id=pmjay"}
        ]
        return {"text": reply_text, "chips": chips, "links": links}

    # B) MJPJAY (Maharashtra Mahatma Jyotirao Phule Jan Arogya Yojana)
    if any(k in clean_msg for k in ["mjpjay", "jyotirao", "phule", "maharashtra scheme", "yellow ration", "orange ration"]):
        reply_text = (
            "🏛️ **Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY - Maharashtra)**\n\n"
            "• **Coverage:** Cashless tertiary and secondary healthcare coverage up to **₹5,00,000 per family per year** (expanded universal health coverage in Maharashtra).\n"
            "• **Beneficiaries:** Covers Yellow ration card, Orange ration card (income up to ₹1 Lakh/yr), Antyodaya Anna Yojana (AAY), Annapurna card holders, as well as farmers in identified distressed agricultural districts.\n"
            "• **Treatments:** 1,356 identified surgical and medical procedures across 34 specialized categories including renal dialysis, bypass surgeries, oncology, pediatric surgery, polytrauma, and ICU treatments.\n"
            "• **How to access:** Visit any empanelled network hospital in Maharashtra and meet the **Aarogyamitra** at the scheme counter with your ration card and photo ID."
        )
        chips = ["MJPJAY hospitals in Sambhajinagar", "Documents needed for MJPJAY", "Is dialysis free under MJPJAY?"]
        links = [
            {"text": "Check MJPJAY Documents", "url": "/documents?scheme_id=mjpjay"},
            {"text": "Find MJPJAY Hospitals", "url": "/hospitals?scheme_id=mjpjay"}
        ]
        return {"text": reply_text, "chips": chips, "links": links}

    # C) AYUSHMAN VAY VANDANA (Senior Citizens 70+)
    if any(k in clean_msg for k in ["vay vandana", "senior citizen", "elderly", "old age", "70 years", "70+"]):
        reply_text = (
            "👵👴 **Ayushman Vay Vandana Scheme (Universal Senior Citizen 70+ Cover)**\n\n"
            "• **Universal Eligibility:** Every Indian citizen aged **70 years and above** is entitled to this cover — **irrespective of family income or economic class**!\n"
            "• **Coverage Amount:** Dedicated **₹5,00,000 per year** exclusively for senior citizens.\n"
            "• **Top-up Benefit:** If the senior's family is already enrolled under standard PM-JAY, the senior gets an **additional separate ₹5 Lakh top-up** reserved only for them.\n"
            "• **Single Requirement:** Just an **Aadhaar card** showing date of birth confirming age 70+.\n"
            "• **Application:** Self-register on the NHA Ayushman App or visit any empanelled hospital/CSC center."
        )
        chips = ["Documents for Vay Vandana", "Hospitals for senior citizens", "Can seniors with CGHS apply?"]
        links = [{"text": "View Vay Vandana Scheme", "url": "/schemes"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # D) RASHTRIYA AROGYA NIDHI (RAN)
    if any(k in clean_msg for k in ["ran", "rashtriya arogya nidhi", "rare disease", "super specialty", "financial assistance"]):
        reply_text = (
            "🩺 **Rashtriya Arogya Nidhi (RAN)**\n\n"
            "• **Benefit:** One-time financial assistance of up to **₹15,00,000** for poor patients living below the poverty line (BPL) who are suffering from major life-threatening disorders.\n"
            "• **Covered Institutes:** Valid at premier central government tertiary institutes like AIIMS, PGIMER, and designated state medical colleges.\n"
            "• **Special Divisions:** Includes financial grants for rare diseases and the Health Minister's Cancer Patient Fund (HMCPF).\n"
            "• **Eligibility:** Valid BPL certificate/income verification and an official treatment estimate from the treating government doctor."
        )
        chips = ["How to apply for RAN grant?", "Which diseases are covered in RAN?", "Other financial aid schemes"]
        links = [{"text": "Check RAN Details", "url": "/schemes"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # E) MATERNITY & CHILD CARE (JSSK & PMSMA)
    if any(k in clean_msg for k in ["maternity", "pregnancy", "delivery", "pregnant", "mother", "child", "jssk", "pmsma", "cesarean", "newborn"]):
        reply_text = (
            "🤰👶 **Maternity & Child Health Welfare Programmes**\n\n"
            "1. **Janani Shishu Suraksha Karyakram (JSSK):**\n"
            "   • **100% Free Deliveries:** Both normal deliveries and Caesarean sections at all public healthcare facilities.\n"
            "   • **Zero Out-of-Pocket Cost:** Free drugs, diagnostics, blood transfusion, food during hospital stay (up to 3 days for normal, 7 days for C-section), and free transport.\n"
            "   • **Sick Infants:** Free treatment, medicines, and ambulance for sick infants up to 1 year of age.\n\n"
            "2. **Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA):**\n"
            "   • Free comprehensive antenatal check-ups by specialist doctors on the **9th of every month**."
        )
        chips = ["What documents for free delivery?", "Hospitals with maternity beds", "Child immunization schemes"]
        links = [{"text": "Find Maternity Empanelled Hospitals", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 6. MEDICAL CONDITIONS & TREATMENTS
    # -------------------------------------------------------------------------
    # Dialysis & Kidney
    if any(k in clean_msg for k in ["dialysis", "kidney", "renal", "nephrology"]):
        reply_text = (
            "💊 **Kidney Care & Dialysis Coverage:**\n\n"
            "• **Free / Cashless Dialysis:** Under both **PM-JAY** and **MJPJAY**, haemodialysis is fully cashless across empanelled hospitals.\n"
            "• **Pradhan Mantri National Dialysis Programme (PMNDP):** Free dialysis services are provided to BPL beneficiaries at district government hospitals (including GMCH).\n"
            "• **Kidney Transplants:** Kidney transplantation and post-transplant immunosuppressive medications are covered under tertiary packages (up to ₹5 Lakh under MJPJAY/PM-JAY).\n\n"
            "Empanelled hospitals like **GMCH घाटी रुग्णालय** and **Dhoot Hospital** have active nephrology & dialysis units."
        )
        chips = ["Hospitals offering free dialysis", "Required documents for dialysis", "Check PM-JAY eligibility"]
        links = [{"text": "View Dialysis Empanelled Hospitals", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # Cancer & Oncology
    if any(k in clean_msg for k in ["cancer", "chemo", "chemotherapy", "radiation", "oncology", "tumor"]):
        reply_text = (
            "🎗️ **Cancer Treatment & Financial Support:**\n\n"
            "• **Comprehensive Cashless Coverage:** PM-JAY covers over 200 oncology packages including surgical removal, radiation therapy, and multiple cycles of chemotherapy.\n"
            "• **MJPJAY Maharashtra:** Covers specialized surgical oncology and medical chemotherapy at accredited hospitals.\n"
            "• **Health Minister's Cancer Patient Fund (HMCPF / RAN):** Additional financial grant of up to ₹5,00,000 for BPL cancer patients receiving care at premier institutes.\n\n"
            "All cancer patients can get their biopsy and oncology staging reports verified at the hospital's Aarogyamitra desk for fast-track cashless pre-authorization."
        )
        chips = ["Which hospitals treat cancer under PM-JAY?", "How to get chemotherapy cashless?", "RAN Cancer assistance"]
        links = [{"text": "Check Cancer Care Hospitals", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # Heart / Cardiology
    if any(k in clean_msg for k in ["heart", "cardio", "bypass", "angioplasty", "stent", "cardiac"]):
        reply_text = (
            "❤️ **Heart Care & Surgery Coverage:**\n\n"
            "• **Covered Procedures:** Coronary Artery Bypass Grafting (CABG), Coronary Angioplasty with stent placement, valve replacements, pacemaker implantation, and pediatric cardiac surgeries.\n"
            "• **Coverage Amount:** Full cashless hospitalization up to ₹5,00,000 under PM-JAY and MJPJAY.\n"
            "• **Where to go:** Empanelled cardiac centres such as GMCH and accredited private superspecialty hospitals."
        )
        chips = ["Hospitals with cardiac ICU beds", "What documents for heart surgery?", "Emergency ambulance 108"]
        links = [{"text": "Find Cardiac Hospitals & Beds", "url": "/hospitals"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # Free Medicines / Diagnostics
    if any(k in clean_msg for k in ["medicine", "medicines", "dawa", "dawai", "pharmacy", "jan aushadhi", "free test", "diagnostic"]):
        reply_text = (
            "💊 **Free & Affordable Medicines / Diagnostics:**\n\n"
            "1. **Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP):**\n"
            "   • High-quality generic medicines available at **50% to 90% cheaper** prices compared to branded medicines across 10,000+ Jan Aushadhi Kendras.\n"
            "2. **Inpatient Hospitalization Packages:**\n"
            "   • Under PM-JAY & MJPJAY, all medicines during your hospital stay and for **15 days post-discharge** are completely free and included in the cashless package.\n"
            "3. **Free Diagnostic Service Initiative:**\n"
            "   • Free basic blood tests, X-rays, and essential investigations at public District Hospitals and Primary Health Centres."
        )
        chips = ["Find nearby Jan Aushadhi Kendra", "What post-hospitalization medicines are free?", "Full scheme list"]
        links = [{"text": "Explore Healthcare Schemes", "url": "/schemes"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 7. DOCUMENTS & VERIFICATION QUESTIONS
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["document", "documents", "aadhaar", "ration card", "proof", "paperwork", "id card", "certificate"]):
        reply_text = (
            "📂 **Essential Documents for Healthcare Schemes:**\n\n"
            "To access cashless treatment or register for a government health card, prepare these core documents:\n\n"
            "1. **Identity & Age Proof:** **Aadhaar Card** (preferred) or Voter ID / Driving License.\n"
            "2. **Family & Economic Proof:** **Ration Card** (Yellow / Orange / Antyodaya AAY / Priority Household PHH) or Income Certificate.\n"
            "3. **Medical Recommendation:** Doctor's prescription, OPD slip, or hospital admission recommendation stating the required surgery/treatment.\n"
            "4. **Diagnostic Reports:** Confirmed lab reports, X-Ray, CT/MRI, or biopsy report (if claiming for specialized surgery).\n\n"
            "💡 *Tip:* Even if you do not have your physical card, the hospital Aarogyamitra can search your family status directly using your 12-digit Aadhaar number!"
        )
        chips = ["What if I don't have a Ration Card?", "How to verify documents online?", "Find hospital desk"]
        links = [{"text": "Open Document Checklist & Upload Tool", "url": "/documents"}]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 8. HOW TO APPLY / APPLICATION PROCESS
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["how to apply", "how do i apply", "apply", "process", "where to go", "registration", "kiosk", "aarogyamitra"]):
        reply_text = (
            "📝 **Step-by-Step Application & Benefit Claim Process:**\n\n"
            "**Step 1: Check Your Eligibility**\n"
            "Complete our 2-minute Scheme Finder questionnaire to view all matched welfare programmes.\n\n"
            "**Step 2: Visit an Empanelled Network Hospital**\n"
            "Walk into any government medical college or accredited private hospital.\n\n"
            "**Step 3: Meet the 'Ayushman Mitra / Aarogyamitra'**\n"
            "Locate the dedicated scheme helpdesk near the hospital registration area. Show your **Aadhaar** and **Ration card**.\n\n"
            "**Step 4: Biometric e-KYC & Cashless Approval**\n"
            "The kiosk executes biometric verification and sends an electronic pre-authorization to the scheme authority. Once approved, all surgery, bed, nursing, and medicines are 100% cashless!"
        )
        chips = ["Start Scheme Finder questionnaire", "Find closest hospital desk", "Documents checklist"]
        links = [
            {"text": "1. Start Scheme Finder", "url": "/schemes"},
            {"text": "2. Locate Empanelled Hospitals", "url": "/hospitals"}
        ]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 9. "AM I ELIGIBLE?" / CHECK ELIGIBILITY
    # -------------------------------------------------------------------------
    if any(k in clean_msg for k in ["eligible", "eligibility", "am i eligible", "can i get", "qualify", "match"]):
        if user_profile and user_profile.get("completion_pct", 0) > 30:
            needs = user_profile.get("healthcare_needs") or []
            needs_str = f" for your selected needs ({', '.join(needs[:2])})" if needs else ""
            reply_text = (
                f"✅ **Personalized Assessment for {user_name or 'You'}:**\n\n"
                f"Based on your registered profile in **{user_district}, {user_state}**{needs_str}:\n\n"
                f"• **Location Match:** You qualify for both All-India Central schemes and {user_state} state-level schemes (including **MJPJAY** and **PM-JAY**).\n"
                f"• **High-Probability Schemes:** You have preliminary matches for cashless hospitalization, free medicines, and district health programmes.\n\n"
                "To see the exact tailored scoring and why each scheme matches your criteria, view your Recommendations tab!"
            )
            links = [{"text": "View Your Matched Schemes", "url": "/recommended-schemes"}]
        else:
            reply_text = (
                "🎯 **Scheme Eligibility Overview:**\n\n"
                "Government healthcare eligibility in India is broadly based on:\n\n"
                "• **Universal Senior Citizens (70+):** Every senior citizen aged 70+ qualifies for **₹5 Lakh** under Ayushman Vay Vandana with **no income limit**.\n"
                "• **Ration Card Category:** Yellow card, Orange card, AAY, or Priority Household card holders automatically qualify for **PM-JAY** and **MJPJAY**.\n"
                "• **Mothers & Infants:** All pregnant women qualify for **100% free delivery** under JSSK.\n"
                "• **Income / BPL:** Families earning under ₹1–2.5 Lakh/year qualify for catastrophic health assistance (RAN & MJPJAY).\n\n"
                "Take our fast **Scheme Finder** to calculate your exact eligibility in under 2 minutes!"
            )
            links = [{"text": "Start 2-Minute Scheme Finder", "url": "/schemes"}]

        chips = ["Start Scheme Finder", "Check Vay Vandana for seniors", "What documents are required?"]
        return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 10. CONTEXTUAL FOLLOW-UP HANDLING
    # -------------------------------------------------------------------------
    if context.get("last_scheme"):
        scheme_key = context["last_scheme"]
        if any(k in clean_msg for k in ["cost", "how much", "amount", "limit", "money"]):
            reply_text = (
                f"Regarding **{scheme_key.upper()}**:\n\n"
                "The annual cashless financial coverage is up to **₹5,00,000 per family per year** (or ₹5 Lakh dedicated per senior citizen under Vay Vandana). "
                "This covers surgery fees, bed charges, ICU, diagnostic tests, and medicines."
            )
            chips = ["Which hospitals accept this?", "What documents are needed?", "How to apply?"]
            return {"text": reply_text, "chips": chips, "links": links}

    # -------------------------------------------------------------------------
    # 11. GENERAL KNOWLEDGE BASE SEARCH FALLBACK
    # -------------------------------------------------------------------------
    # Try searching the database for schemes matching any query words
    all_schemes = get_all_schemes(active_only=True)
    matched_schemes = []
    tokens = [t for t in clean_msg.split() if len(t) > 3]

    for s in all_schemes:
        searchable = _normalize(f"{s.get('name', '')} {s.get('description', '')} {s.get('category', '')} {s.get('who_benefits', '')} {s.get('benefits_text', '')}")
        score = sum(1 for tok in tokens if tok in searchable)
        if score > 0:
            matched_schemes.append((score, s))

    matched_schemes.sort(key=lambda x: x[0], reverse=True)

    if matched_schemes:
        top_scheme = matched_schemes[0][1]
        reply_text = (
            f"I found information related to your question under **{top_scheme['name']}**:\n\n"
            f"• **Category:** {top_scheme.get('category', 'General Healthcare')}\n"
            f"• **Overview:** {top_scheme.get('description', '')[:220]}...\n"
            f"• **Benefits:** {top_scheme.get('benefits_text', 'Cashless government healthcare support.')}\n"
            f"• **Who Benefits:** {top_scheme.get('who_benefits', 'Eligible Indian families.')}\n\n"
            "Would you like to know the required documents, empanelled hospitals, or how to apply?"
        )
        chips = [
            f"Documents for {top_scheme.get('short_tag', 'this scheme')}",
            "Find nearest empanelled hospital",
            "Take Scheme Finder assessment"
        ]
        links = [
            {"text": f"View {top_scheme.get('short_tag', 'Scheme')} Details", "url": f"/documents?scheme_id={top_scheme['id']}"},
            {"text": "Explore All Schemes", "url": "/schemes"}
        ]
        return {"text": reply_text, "chips": chips, "links": links}

    # Default friendly conversational guidance
    reply_text = (
        "Thank you for reaching out! I understand you are inquiring about government healthcare support.\n\n"
        "To give you the most accurate answer, could you tell me:\n"
        "1. **Which state/district** you are located in?\n"
        "2. **What treatment or medical condition** (e.g., surgery, dialysis, cancer, maternity, generic medicine) you need help with?\n"
        "3. Or whether you would like to find **empanelled hospitals with live bed availability**?\n\n"
        "You can also click any of the quick topics below to get started immediately."
    )
    chips = [
        "Which schemes am I eligible for?",
        "Hospitals with ICU bed availability",
        "How do I get an Ayushman card?",
        "Emergency ambulance helplines (108)"
    ]
    links = [
        {"text": "Launch 2-Min Scheme Finder", "url": "/schemes"},
        {"text": "Check Hospitals & Beds", "url": "/hospitals"}
    ]
    return {"text": reply_text, "chips": chips, "links": links}
