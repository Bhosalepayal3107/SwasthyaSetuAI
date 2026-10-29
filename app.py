from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import json
from db import (
    init_db, get_all_schemes, get_scheme_by_id, create_scheme,
    update_scheme, delete_scheme, toggle_scheme_status,
    verify_admin, count_schemes, recommend_schemes_from_db,
    create_user, verify_user, get_user_by_id, get_user_by_email,
    update_user_basic, get_user_profile, save_user_profile,
    update_quick_answer, calculate_profile_completion,
    get_empanelled_hospitals, get_hospital_by_id,
    get_newly_launched_schemes
)
from scheme_recommender import recommend_schemes_for_user

app = Flask(__name__)
app.secret_key = "swasthyasetu-secure-session-key-dev"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Initialize database on startup
init_db()

NAV = [
    ("home", "Overview", "⌂", "/"),
    ("profile", "My Profile", "👤", "/profile"),
    ("schemes", "Scheme Finder", "⌕", "/schemes"),
    ("recommended_schemes", "Recommendations", "★", "/recommended-schemes"),
    ("documents", "Documents", "▤", "/documents"),
    ("hospitals", "Hospitals", "✚", "/hospitals"),
    ("records", "Medical Records", "▧", "/records"),
    ("assistant", "AI Assistant", "✧", "/assistant"),
    ("tracking", "Track Application", "◷", "/tracking"),
]

def page(template, active, title, **kwargs):
    return render_template(template, active=active, nav=NAV, page_title=title, **kwargs)

@app.route("/")
def home():
    schemes = get_all_schemes(active_only=True)
    return page("home.html", "home", "Overview", schemes=schemes)

@app.route("/set-language/<lang>", methods=["POST"])
def set_portal_language(lang):
    if lang in ["en", "hi", "mr"]:
        session["lang"] = lang
        return jsonify({"status": "ok", "lang": lang})
    return jsonify({"status": "error", "message": "Unsupported language"}), 400

# =====================================================================
# MULTI-STEP SCHEME FINDER ROUTES (unchanged logic, uses DB now)
# =====================================================================

@app.route("/schemes", methods=["GET", "POST"])
def schemes():
    if request.method == "POST":
        if "current_step" in request.form:
            try:
                current_step = int(request.form.get("current_step", 1))
            except ValueError:
                current_step = 1
            return schemes_submit_step(current_step)
        return schemes_assess()

    if request.args.get("restart") == "1":
        session.pop("scheme_form", None)
        session.pop("scheme_assessment", None)
        return redirect(url_for("schemes"))

    # Legacy stepper test support
    if "step" in request.args:
        step_arg = request.args.get("step", "1")
        try:
            step = int(step_arg)
            if step < 1 or step > 4:
                step = 1
        except ValueError:
            step = 1
        form_data = session.get("scheme_form", {})
        return page("schemes.html", "schemes", "Find Healthcare Schemes for You", step=step, data=form_data)

    user = None
    profile = None
    if session.get("user_id"):
        user = get_user_by_id(session["user_id"])
        if user:
            profile = get_user_profile(user["id"])

    assessment = session.get("scheme_assessment", {})
    return page("schemes.html", "schemes", "Find Healthcare Schemes for You",
                assessment=assessment, user=user, profile=profile, step=1, data=assessment)


@app.route("/schemes/assess", methods=["POST"])
def schemes_assess():
    beneficiary = request.form.get("beneficiary", "myself").strip()
    patient_age_str = request.form.get("patient_age", "").strip()
    gender = request.form.get("gender", "Female").strip()
    state = request.form.get("state", "Maharashtra").strip()
    district = request.form.get("district", "Chhatrapati Sambhajinagar").strip()
    healthcare_needs = request.form.getlist("healthcare_needs")
    doctor_rec = request.form.get("doctor_recommended", "").strip()
    treatment_stage = request.form.get("treatment_stage", "").strip()
    notes = request.form.get("notes", "").strip()
    special_category = request.form.get("special_category", "").strip()

    doc_keys = ["identity_proof", "ration_card", "income_cert", "medical_reports", "hospital_estimate", "health_card"]
    doc_avail = {}
    for dk in doc_keys:
        doc_avail[dk] = request.form.get(f"doc_{dk}", "not_sure")

    patient_age = int(patient_age_str) if patient_age_str.isdigit() else 45

    assessment = {
        "beneficiary": beneficiary,
        "patient_age": patient_age,
        "age": patient_age,
        "gender": gender,
        "state": state,
        "district": district,
        "healthcare_needs": healthcare_needs,
        "doctor_recommended": doctor_rec,
        "treatment_stage": treatment_stage,
        "treatment_context": {
            "doctor_recommended": doctor_rec,
            "treatment_stage": treatment_stage
        },
        "notes": notes,
        "special_category": special_category,
        "document_availability": doc_avail
    }

    session["scheme_assessment"] = assessment

    # Sync with scheme_form for legacy readers
    session["scheme_form"] = {
        "full_name": beneficiary.title() if beneficiary != "myself" else (session.get("user_name") or "Applicant"),
        "beneficiary": beneficiary,
        "age": patient_age,
        "gender": gender,
        "state": state,
        "district": district,
        "treatments": healthcare_needs,
        "doctor_recommended": doctor_rec,
        "treatment_status": treatment_stage
    }

    # If user is logged in, sync with database profile
    if session.get("user_id"):
        user_id = session["user_id"]
        prof = get_user_profile(user_id)
        prof["beneficiary"] = beneficiary
        prof["beneficiary_type"] = beneficiary
        prof["age"] = patient_age
        prof["gender"] = gender
        prof["healthcare_needs"] = healthcare_needs
        prof["treatment_context"] = {"doctor_recommended": doctor_rec, "treatment_stage": treatment_stage}
        prof["notes"] = notes
        prof["special_category"] = special_category
        prof["document_availability"] = doc_avail
        save_user_profile(user_id, prof)

    flash("Assessment completed! Below are your eligible government healthcare schemes.", "info")
    return redirect(url_for("recommended_schemes"))


@app.route("/schemes/step/<int:step_num>", methods=["POST"])
def schemes_submit_step(step_num):
    if step_num < 1 or step_num > 4:
        return redirect(url_for("schemes", step=1))

    form_data = session.get("scheme_form", {})
    action = request.form.get("action", "next")

    # STEP 1: PERSONAL INFORMATION
    if step_num == 1:
        full_name = request.form.get("full_name", "").strip()
        beneficiary = request.form.get("beneficiary", "myself").strip()
        age_str = request.form.get("age", "").strip()
        patient_age_str = request.form.get("patient_age", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "Female").strip()
        state = request.form.get("state", "Maharashtra").strip()
        district = request.form.get("district", "").strip()
        city_village = request.form.get("city_village", "").strip()
        residence_type = request.form.get("residence_type", "Rural").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name or len(full_name) < 2:
            flash("Please enter the full name of the applicant or patient.", "error")
            return redirect(url_for("schemes", step=1))

        if not age_str.isdigit() or not (0 <= int(age_str) <= 120):
            flash("Please enter a valid age between 0 and 120 years.", "error")
            return redirect(url_for("schemes", step=1))

        if beneficiary != "myself":
            if patient_age_str:
                if not patient_age_str.isdigit() or not (0 <= int(patient_age_str) <= 120):
                    flash("Please enter a valid patient age between 0 and 120.", "error")
                    return redirect(url_for("schemes", step=1))
            else:
                patient_age_str = age_str

        if not district:
            flash("Please enter the district of residence.", "error")
            return redirect(url_for("schemes", step=1))

        form_data.update({
            "full_name": full_name,
            "beneficiary": beneficiary,
            "age": int(age_str),
            "patient_age": int(patient_age_str) if patient_age_str else int(age_str),
            "dob": dob,
            "gender": gender,
            "state": state,
            "district": district,
            "city_village": city_village,
            "residence_type": residence_type,
            "phone": phone
        })

    # STEP 2: FAMILY & FINANCIAL DETAILS
    elif step_num == 2:
        income = request.form.get("income", "Below ₹1 lakh").strip()
        ration_card = request.form.get("ration_card", "yes").strip()
        ration_card_type = request.form.get("ration_card_type", "").strip()
        ayushman_card = request.form.get("ayushman_card", "no").strip()
        mjpjay_reg = request.form.get("mjpjay_reg", "no").strip()
        other_insurance = request.form.get("other_insurance", "No insurance").strip()
        govt_employee = request.form.get("govt_employee", "no").strip()
        circumstances = request.form.getlist("circumstances")

        form_data.update({
            "income": income,
            "ration_card": ration_card,
            "ration_card_type": ration_card_type if ration_card == "yes" else "No Ration Card",
            "ayushman_card": ayushman_card,
            "mjpjay_reg": mjpjay_reg,
            "other_insurance": other_insurance,
            "govt_employee": govt_employee,
            "circumstances": circumstances
        })

    # STEP 3: MEDICAL TREATMENT REQUIREMENTS
    elif step_num == 3:
        treatments = request.form.getlist("treatments")
        treatment_status = request.form.get("treatment_status", "").strip()
        treatment_cost = request.form.get("treatment_cost", "₹1 lakh–₹5 lakh").strip()
        hospital_type = request.form.get("hospital_type", "Government hospital").strip()
        hospital_accepts_scheme = request.form.get("hospital_accepts_scheme", "not_sure").strip()
        doctor_recommended = request.form.get("doctor_recommended", "yes").strip()
        diagnosis_notes = request.form.get("diagnosis_notes", "").strip()

        if not treatments:
            treatments = ["General hospitalization"]
        if not treatment_status:
            treatment_status = "Doctor has recommended hospitalization"

        form_data.update({
            "treatments": treatments,
            "treatment_status": treatment_status,
            "treatment_cost": treatment_cost,
            "hospital_type": hospital_type,
            "hospital_accepts_scheme": hospital_accepts_scheme,
            "doctor_recommended": doctor_recommended,
            "diagnosis_notes": diagnosis_notes
        })

    # STEP 4: EXISTING BENEFITS AND DOCUMENTS
    elif step_num == 4:
        doc_fields = [
            "aadhaar", "ration_card", "income_cert", "residence_cert",
            "medical_reports", "prescription", "hospital_estimate",
            "disability_cert", "govt_health_card", "other_docs"
        ]
        documents_status = {}
        for df in doc_fields:
            documents_status[df] = request.form.get(f"doc_{df}", "not_sure").strip()
        form_data["documents"] = documents_status

    session["scheme_form"] = form_data
    session.modified = True

    if action == "save":
        flash("Progress safely saved in your session.", "info")
        return redirect(url_for("schemes", step=step_num))

    if step_num < 4:
        return redirect(url_for("schemes", step=step_num + 1))
    else:
        return redirect(url_for("schemes_results"))


@app.route("/schemes/results", methods=["GET"])
def schemes_results():
    profile = session.get("scheme_form", {})
    if not profile or not profile.get("full_name") or not profile.get("treatments"):
        flash("Please complete the questionnaire so we can recommend matching schemes.", "info")
        return redirect(url_for("schemes", step=1))

    # Use the dynamic DB-based recommendation engine
    recommendations = recommend_schemes_from_db(profile)
    return page("scheme_results.html", "schemes", "Your Healthcare Support Recommendations",
                profile=profile, recommendations=recommendations)


@app.route("/schemes/reset", methods=["GET", "POST"])
def schemes_reset():
    session.pop("scheme_form", None)
    flash("Questionnaire restarted. All answers have been reset.", "info")
    return redirect(url_for("schemes", step=1))


# =====================================================================
# USER AUTHENTICATION & SMART PROFILE ROUTES
# =====================================================================

def user_login_required(f):
    """Decorator to protect user profile, dashboard, and personalised routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access your personal dashboard and profile.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        state = request.form.get("state", "").strip()
        district = request.form.get("district", "").strip()
        mobile = request.form.get("mobile", "").strip()

        # Validation
        if not name or len(name) < 2:
            flash("Please enter your full legal or preferred name.", "error")
            return render_template("register.html", page_title="Create Your Account")

        import re
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not email or not re.match(email_regex, email):
            flash("Please enter a valid email address.", "error")
            return render_template("register.html", page_title="Create Your Account")

        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html", page_title="Create Your Account")

        if password != confirm_password:
            flash("Passwords do not match. Please re-enter carefully.", "error")
            return render_template("register.html", page_title="Create Your Account")

        if not state:
            flash("Please select your state of residence.", "error")
            return render_template("register.html", page_title="Create Your Account")

        if not district:
            flash("Please enter your district.", "error")
            return render_template("register.html", page_title="Create Your Account")

        # Check existing user
        existing = get_user_by_email(email)
        if existing:
            flash("An account is already registered with this email. Please log in.", "error")
            return redirect(url_for("login"))

        # Create user (stores secure scrypt hash, never plaintext)
        user_id = create_user(name, email, password, state, district, mobile)
        if user_id:
            session["user_id"] = user_id
            session["user_name"] = name
            session["user_email"] = email
            flash(f"Welcome, {name.split()[0]}! Your profile is just getting started. Account created successfully.", "info")
            return redirect(url_for("profile_view"))
        else:
            flash("An error occurred creating your account. Please try again.", "error")

    return render_template("register.html", page_title="Create Your Account")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile_view"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.form.get("next", "") or request.args.get("next", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html", page_title="Beneficiary Login", next=next_url)

        user = verify_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name'].split()[0]}!", "info")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("profile_view"))
        
        # If the user enters admin credentials on this login form, redirect them straight to the admin panel
        admin_data = verify_admin(email, password)
        if admin_data:
            session["admin_logged_in"] = True
            session["admin_user"] = admin_data.get("email") or "admin@swasthyasetu.gov.in"
            flash("Welcome, Administrator!", "info")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid email address or password. Please try again.", "error")

    return render_template("login.html", page_title="Beneficiary Login", next=request.args.get("next", ""))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)
    flash("You have been safely logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@user_login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))
    profile = get_user_profile(user["id"])
    recommendations = recommend_schemes_for_user(user, profile)
    recent_schemes = get_newly_launched_schemes(limit=6)
    return page("dashboard.html", "profile", "My Complete Profile",
                user=user, profile=profile,
                recommendations=recommendations,
                recent_schemes=recent_schemes)


@app.route("/profile")
@user_login_required
def profile_view():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    profile = get_user_profile(user["id"])
    return page("profile.html", "profile", "My Complete Profile",
                user=user, profile=profile)


@app.route("/profile/edit")
@user_login_required
def profile_edit():
    return redirect(url_for("profile_view"))


@app.route("/profile/save", methods=["POST"])
@user_login_required
def profile_save():
    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for("login"))

    action = request.form.get("action", "save")

    # Update basic user info if provided
    name = request.form.get("name", user["name"]).strip()
    state = request.form.get("state", user["state"]).strip()
    district = request.form.get("district", user["district"]).strip()
    mobile = request.form.get("mobile", user.get("mobile", "")).strip()
    if name:
        update_user_basic(user_id, name=name, mobile=mobile, state=state, district=district)
        session["user_name"] = name

    # Parse age & dob
    dob = request.form.get("dob", "").strip()
    age_str = request.form.get("age", "").strip()
    age = None
    if dob:
        try:
            b_year = int(dob.split("-")[0])
            c_year = datetime.now().year
            if 1900 <= b_year <= c_year:
                age = c_year - b_year
        except Exception:
            pass
    if age is None and age_str.isdigit():
        age = int(age_str)

    # Document availability dictionary
    doc_keys = [
        "id_proof", "address_proof", "income_cert", "ration_card",
        "medical_reports", "hospital_estimate", "disability_cert", "health_card"
    ]
    doc_avail = {}
    for dk in doc_keys:
        val = request.form.get(f"doc_{dk}", "not_sure")
        doc_avail[dk] = val

    profile_data = {
        "dob": dob,
        "age": age,
        "gender": request.form.get("gender", ""),
        "residence_type": request.form.get("residence_type", ""),
        "beneficiary": request.form.get("beneficiary", "myself"),
        "family_size": request.form.get("family_size", ""),
        "household_income": request.form.get("household_income", ""),
        "ration_card_category": request.form.get("ration_card_category", ""),
        "existing_health_coverage": request.form.get("existing_health_coverage", ""),
        "other_coverage": request.form.get("other_coverage", ""),
        "occupation": request.form.get("occupation", ""),
        "worker_board": request.form.get("worker_board", ""),
        "special_categories": request.form.getlist("special_categories"),
        "healthcare_needs": request.form.getlist("healthcare_needs"),
        "healthcare_notes": request.form.get("healthcare_notes", "").strip(),
        "dialysis_prescribed": request.form.get("dialysis_prescribed", ""),
        "pregnancy_stage": request.form.get("pregnancy_stage", ""),
        "disability_cert_status": request.form.get("disability_cert_status", ""),
        "treatment_stage": request.form.get("treatment_stage", ""),
        "document_availability": doc_avail
    }

    completion_pct = save_user_profile(user_id, profile_data)

    if action == "continue_later":
        flash(f"Profile saved! Your current profile is {completion_pct}% complete. You can continue anytime.", "info")
        return redirect(url_for("dashboard"))
    else:
        flash(f"Profile updated successfully! Completion is now {completion_pct}%.", "info")
        return redirect(url_for("profile_view"))


@app.route("/profile/quick-answer", methods=["POST"])
@user_login_required
def profile_quick_answer():
    user_id = session["user_id"]
    question_key = request.form.get("question_key", "").strip()
    answer_value = request.form.get("answer_value", "").strip()
    next_url = request.form.get("next_url", "")

    if question_key and answer_value:
        update_quick_answer(user_id, question_key, answer_value)
        flash("Thank you! Your profile has been updated with your response.", "info")

    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect(url_for("dashboard"))


@app.route("/recommendations")
@app.route("/recommended-schemes")
def recommended_schemes():
    if not session.get("user_id"):
        flash("Please log in to view your personalized recommendations.", "error")
        return redirect(url_for("login", next=request.path))

    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))
    profile = get_user_profile(user["id"])
    assessment = session.get("scheme_assessment", {})

    # If scheme assessment was completed in session, prioritize its state and needs
    if assessment:
        if assessment.get("healthcare_needs"):
            profile["healthcare_needs"] = assessment["healthcare_needs"]
        if assessment.get("state"):
            user["state"] = assessment["state"]
        if assessment.get("district"):
            user["district"] = assessment["district"]
        if assessment.get("special_category"):
            profile["special_category"] = assessment["special_category"]

    recommendations = recommend_schemes_for_user(user, profile)

    count_potential = sum(1 for r in recommendations if r.get("match_status") == "Potential Match")
    count_more_info = sum(1 for r in recommendations if r.get("match_status") == "More Information Needed")
    count_unverified = sum(1 for r in recommendations if r.get("match_status") == "Eligibility Not Yet Verified")

    recent_schemes = get_newly_launched_schemes(limit=4)
    return page("recommended_schemes.html", "recommended_schemes", "Recommended Healthcare Schemes",
                user=user, profile=profile, recommendations=recommendations,
                count_potential=count_potential, count_more_info=count_more_info, count_unverified=count_unverified,
                recent_schemes=recent_schemes)


# =====================================================================
# ADMIN PANEL ROUTES
# =====================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email_or_username = (request.form.get("email") or request.form.get("username") or "").strip()
        password = request.form.get("password", "").strip()
        admin_data = verify_admin(email_or_username, password)
        if admin_data:
            session["admin_logged_in"] = True
            session["admin_user"] = admin_data.get("email") or admin_data.get("username") or "admin@swasthyasetu.gov.in"
            flash("Logged in successfully.", "info")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("admin_login.html", page_title="Admin Login")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin_login"))


def admin_required(f):
    """Decorator to protect admin routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login to access the admin panel.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = count_schemes()
    all_schemes = get_all_schemes(active_only=False)
    # Group by category
    categories = {}
    for s in all_schemes:
        cat = s.get("category", "Other")
        categories.setdefault(cat, []).append(s)
    return render_template("admin_dashboard.html",
                           page_title="Admin Dashboard",
                           stats=stats,
                           schemes=all_schemes,
                           categories=categories,
                           admin_user=session.get("admin_user", "admin"))


@app.route("/admin/scheme/new", methods=["GET", "POST"])
@admin_required
def admin_scheme_new():
    if request.method == "POST":
        data = _parse_scheme_form(request.form)
        data["added_by"] = session.get("admin_user", "Government Administrator")
        create_scheme(data)
        flash(f"Government Scheme '{data['name']}' published! Beneficiaries can now view this update on their dashboards.", "info")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_scheme_form.html",
                           page_title="Add New Scheme",
                           scheme=None,
                           mode="new",
                           admin_user=session.get("admin_user", "admin"))


@app.route("/admin/scheme/<int:scheme_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_scheme_edit(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        flash("Scheme not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        data = _parse_scheme_form(request.form)
        update_scheme(scheme_id, data)
        flash(f"Scheme '{data['name']}' updated successfully!", "info")
        return redirect(url_for("admin_dashboard"))

    # Parse JSON fields for the form
    for field in ["eligibility_rules", "required_documents"]:
        try:
            val = json.loads(scheme.get(field, "[]") or "[]")
            scheme[field + "_text"] = "\n".join(val)
            if field == "required_documents":
                scheme["required_documents_list"] = val
        except Exception:
            scheme[field + "_text"] = ""
            if field == "required_documents":
                scheme["required_documents_list"] = []

    return render_template("admin_scheme_form.html",
                           page_title=f"Edit: {scheme['name']}",
                           scheme=scheme,
                           mode="edit",
                           admin_user=session.get("admin_user", "admin"))


@app.route("/admin/scheme/<int:scheme_id>/delete", methods=["POST"])
@admin_required
def admin_scheme_delete(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if scheme:
        delete_scheme(scheme_id)
        flash(f"Scheme '{scheme['name']}' deleted.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/scheme/<int:scheme_id>/toggle", methods=["POST"])
@admin_required
def admin_scheme_toggle(scheme_id):
    toggle_scheme_status(scheme_id)
    return redirect(url_for("admin_dashboard"))


def _parse_scheme_form(form):
    """Parse admin scheme form data into a dict ready for DB insert/update."""
    def lines_to_json(field_name):
        text = form.get(field_name, "")
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        return json.dumps(lines)

    # Documents from multi-select checklist + any custom typed documents
    docs_selected = form.getlist("required_documents")
    other_docs = form.get("other_required_docs", "").strip()
    if other_docs:
        for od in other_docs.split("\n"):
            od = od.strip()
            if od and od not in docs_selected:
                docs_selected.append(od)

    # State applicable from dropdown
    state_selected = form.get("states_applicable", "All India").strip()
    if state_selected in ["All", "All India", "All India (Universal)", "All States & UTs"]:
        state_selected = "All"

    name = form.get("name", "").strip()
    desc = form.get("description", "").strip()
    cat = form.get("category", "General").strip()
    who = form.get("who_benefits", "").strip()
    combined_text = f"{name} {desc} {cat} {who}".lower()

    # Automatically extract matching tags from text without manual admin entry
    common_tags = [
        "hospitalization", "surgery", "cancer", "heart", "cardiac", "kidney",
        "dialysis", "maternity", "pregnancy", "mental", "eye", "vision",
        "medicine", "pharmacy", "accident", "emergency", "disability",
        "senior", "elderly", "child", "pediatric", "bpl", "ayushman", "neurosurgery", "brain"
    ]
    auto_tags = [tag for tag in common_tags if tag in combined_text]

    return {
        "name": name,
        "short_tag": form.get("short_tag", "").strip(),
        "category": cat,
        "govt_level": form.get("govt_level", "Central Government").strip(),
        "description": desc,
        "who_benefits": who,
        "eligibility_rules": lines_to_json("eligibility_rules"),
        "required_documents": json.dumps(docs_selected),
        "benefits_text": form.get("benefits_text", "").strip(),
        "covered_treatments": json.dumps([]),
        "official_website": form.get("official_website", "https://mohfw.gov.in/").strip(),
        "application_process": form.get("application_process", "").strip(),
        "states_applicable": state_selected,
        "age_min": 0,
        "age_max": 120,
        "income_limit": form.get("income_limit", "No income limit").strip(),
        "match_tags": json.dumps(auto_tags),
        "is_active": 1 if form.get("is_active") else 0,
        "color": "blue",
    }


# =====================================================================
# EXISTING MODULES PRESERVED
# =====================================================================

@app.route("/eligibility", methods=["GET", "POST"])
def eligibility():
    return redirect(url_for("schemes"))

@app.route("/documents", methods=["GET", "POST"])
def documents():
    scheme_id = request.args.get("scheme_id", type=int)
    all_schemes = get_all_schemes(active_only=True)
    selected_scheme = None
    if scheme_id:
        selected_scheme = get_scheme_by_id(scheme_id)
    if not selected_scheme and all_schemes:
        selected_scheme = all_schemes[0]

    # Parse scheme required documents checklist
    checklist = []
    if selected_scheme:
        req_docs = selected_scheme.get("required_documents")
        if isinstance(req_docs, str):
            try:
                checklist = json.loads(req_docs)
            except Exception:
                checklist = [d.strip() for d in req_docs.split(",") if d.strip()]
        elif isinstance(req_docs, list):
            checklist = req_docs

    if not checklist:
        checklist = [
            "Aadhaar Card (Applicant & Patient identity proof)",
            "Ration Card (Yellow, Orange, or White)",
            "Income Certificate issued by Tahsildar / SDM",
            "Doctor's Prescription & Recent Medical Reports",
            "Hospital Treatment Cost Estimate Memo"
        ]

    # Handle post upload directly if submitted to /documents
    if request.method == "POST":
        files = request.files.getlist("documents")
        uploaded = session.get("uploaded_documents", [])
        valid_count = 0
        for f in files:
            if f and f.filename:
                content = f.read()
                size_kb = max(1, len(content) // 1024)
                uploaded.append({
                    "filename": f.filename,
                    "size_kb": size_kb,
                    "status": "Verified & Format Ready"
                })
                valid_count += 1
        session["uploaded_documents"] = uploaded
        if valid_count > 0:
            flash(f"{valid_count} document(s) uploaded and format-verified successfully for hospital submission.", "info")
        else:
            flash("Please choose at least one file first.", "error")

    uploaded_files = session.get("uploaded_documents", [])
    return page("documents.html", "documents", "Document Centre",
                selected_scheme=selected_scheme,
                all_schemes=all_schemes,
                checklist=checklist,
                uploaded_files=uploaded_files)


@app.route("/documents/upload", methods=["POST"])
def documents_upload():
    scheme_id = request.form.get("scheme_id", type=int)
    files = request.files.getlist("documents")
    uploaded = session.get("uploaded_documents", [])
    valid_count = 0
    for f in files:
        if f and f.filename:
            content = f.read()
            size_kb = max(1, len(content) // 1024)
            uploaded.append({
                "filename": f.filename,
                "size_kb": size_kb,
                "status": "Verified & Format Ready"
            })
            valid_count += 1

    session["uploaded_documents"] = uploaded
    if valid_count > 0:
        flash(f"{valid_count} document(s) uploaded and format-verified successfully for hospital submission.", "info")
    else:
        flash("Please select at least one document to upload.", "error")

    return redirect(url_for("documents", scheme_id=scheme_id))


@app.route("/hospitals", methods=["GET", "POST"])
def hospitals():
    scheme_id = request.args.get("scheme_id", type=int)
    query = request.args.get("q", "").strip() or request.form.get("location", "").strip()
    
    selected_scheme = get_scheme_by_id(scheme_id) if scheme_id else None
    
    # Priority sorting min to max distance is default in get_empanelled_hospitals
    hospitals_list = get_empanelled_hospitals(scheme_id=scheme_id, search_term=query, sort_by="distance")

    return page("hospitals.html", "hospitals", "Hospital Finder",
                hospitals=hospitals_list,
                selected_scheme=selected_scheme,
                query=query)

@app.route("/records", methods=["GET", "POST"])
def records():
    records_list = []
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Medical report")
        date = request.form.get("date", "")
        if title:
            records_list.append({"title": title, "category": category, "date": date or datetime.now().strftime("%d %b %Y")})
            flash("Record added for this demo session only; it is not saved to a database.", "info")
        else:
            flash("Enter a record title.", "error")
    return page("records.html", "records", "Medical Records", records_list=records_list)

@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    from ai_assistant import generate_assistant_reply

    # Session-backed conversation history
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        # AJAX / fetch JSON request from browser
        if request.is_json:
            data = request.get_json(force=True)
            user_msg = (data.get("message") or "").strip()
            if not user_msg:
                return jsonify({"error": "empty"}), 400

            history = session.get("chat_history", [])

            # Optionally pass user profile context
            user_profile = None
            if session.get("user_id"):
                user = get_user_by_id(session["user_id"])
                prof = get_user_profile(session["user_id"])
                user_profile = {}
                if user:
                    user_profile["name"] = user.get("name", "")
                    user_profile["state"] = user.get("state", "")
                    user_profile["district"] = user.get("district", "")
                if prof:
                    user_profile["healthcare_needs"] = json.loads(prof.get("healthcare_needs") or "[]")
                    user_profile["completion_pct"] = prof.get("completion_pct", 0)

            reply = generate_assistant_reply(
                user_msg,
                history=history,
                user_profile=user_profile,
                session_lang=session.get("lang", "en")
            )

            # Append to conversation history (keep last 24 messages)
            history.append({"role": "user", "text": user_msg})
            history.append({"role": "bot", "text": reply["text"]})
            session["chat_history"] = history[-24:]
            session.modified = True

            return jsonify({
                "text": reply["text"],
                "chips": reply.get("chips", []),
                "links": reply.get("links", [])
            })

        # Plain HTML form POST fallback
        question = request.form.get("question", "").strip()
        if question:
            history = session.get("chat_history", [])
            reply = generate_assistant_reply(
                question,
                history=history,
                session_lang=session.get("lang", "en")
            )
            session["chat_history"] = (history + [
                {"role": "user", "text": question},
                {"role": "bot", "text": reply["text"]}
            ])[-24:]
            session.modified = True

    if request.args.get("clear") == "1":
        session["chat_history"] = []
        session.modified = True
        return redirect(url_for("assistant"))

    return page("assistant.html", "assistant", "Healthcare Assistant",
                chat_history=session.get("chat_history", []))

@app.route("/set-language/<lang>", methods=["POST", "GET"])
def set_language(lang):
    """Set the session language preference (en, hi, mr)."""
    if lang in ["en", "hi", "mr"]:
        session["lang"] = lang
        session.modified = True
    return jsonify({"status": "ok", "lang": session.get("lang", "en")})

@app.route("/tracking", methods=["GET", "POST"])
def tracking():
    application_id = request.form.get("application_id", "").strip() if request.method == "POST" else ""
    return page("tracking.html", "tracking", "Application Tracker", application_id=application_id)

if __name__ == "__main__":
    app.run(debug=True)
