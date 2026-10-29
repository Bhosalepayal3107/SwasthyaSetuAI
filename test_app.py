"""
test_app.py - Comprehensive Verification and Automated Test Suite for SwasthyaSetu AI
Tests all routes, form steps, validation logic, recommendation engine,
synthetic profiles, emergency handling, and error states.
"""

import sys
import unittest
from flask import session
from app import app
from scheme_catalogue import SCHEME_CATALOGUE, recommend_schemes


class SwasthyaSetuTestSuite(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()

    # -------------------------------------------------------------------------
    # 1. Existing Core Routes Integrity Test
    # -------------------------------------------------------------------------
    def test_core_routes_preserved(self):
        """Verify all existing modules render properly with HTTP 200 and eligibility redirects to schemes."""
        routes = [
            ("/", "Overview"),
            ("/documents", "Document Centre"),
            ("/hospitals", "Hospital Finder"),
            ("/records", "Medical Records"),
            ("/assistant", "Healthcare Assistant"),
            ("/tracking", "Application Tracker"),
        ]
        for path, expected_text in routes:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, f"Route {path} failed")
            self.assertIn(expected_text.encode("utf-8"), response.data, f"Missing '{expected_text}' in {path}")

        # Verify /eligibility redirects to /schemes
        res_elig = self.client.get("/eligibility")
        self.assertEqual(res_elig.status_code, 302)
        self.assertIn("/schemes", res_elig.headers["Location"])

    # -------------------------------------------------------------------------
    # 2. Scheme Finder Stepper Navigation
    # -------------------------------------------------------------------------
    def test_schemes_get_steps(self):
        """Check that GET /schemes loads all 4 steps properly."""
        for step in [1, 2, 3, 4]:
            response = self.client.get(f"/schemes?step={step}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(f"STEP {step} OF 4".encode("utf-8"), response.data)
            self.assertIn(b"Find Healthcare Schemes for You", response.data)

    def test_schemes_step1_validation(self):
        """Test Step 1 server validation for missing name, invalid age, and valid submission."""
        # Missing full name
        res = self.client.post("/schemes/step/1", data={
            "full_name": "",
            "age": "45",
            "district": "Pune",
            "state": "Maharashtra"
        }, follow_redirects=True)
        self.assertIn(b"Please enter the full name", res.data)

        # Invalid age
        res = self.client.post("/schemes/step/1", data={
            "full_name": "Ramesh Kumar",
            "age": "999",
            "district": "Pune",
            "state": "Maharashtra"
        }, follow_redirects=True)
        self.assertIn(b"Please enter a valid age", res.data)

        # Missing district
        res = self.client.post("/schemes/step/1", data={
            "full_name": "Ramesh Kumar",
            "age": "45",
            "district": "",
            "state": "Maharashtra"
        }, follow_redirects=True)
        self.assertIn(b"Please enter the district", res.data)

        # Valid Step 1 submission
        res = self.client.post("/schemes/step/1", data={
            "full_name": "Sunita Patil",
            "beneficiary": "myself",
            "age": "72",
            "gender": "Female",
            "state": "Maharashtra",
            "district": "Chhatrapati Sambhajinagar",
            "residence_type": "Rural"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Family & Financial Information", res.data)

    def test_schemes_step2_submission(self):
        """Test Step 2 financial and ration card details submission."""
        res = self.client.post("/schemes/step/2", data={
            "income": "Below ₹1 lakh",
            "ration_card": "yes",
            "ration_card_type": "Yellow / Antyodaya Anna Yojana (AAY)",
            "ayushman_card": "no",
            "mjpjay_reg": "no",
            "other_insurance": "No insurance",
            "govt_employee": "no",
            "circumstances": ["BPL / Low-income certificate holder"]
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Medical Treatment Requirements", res.data)

    def test_schemes_step3_validation(self):
        """Test Step 3 safe fallback and valid submission."""
        # Missing treatments gracefully defaults to General hospitalization and advances to Step 4
        res = self.client.post("/schemes/step/3", data={
            "treatment_status": "Doctor has recommended hospitalization",
            "treatment_cost": "₹1 lakh–₹5 lakh",
            "hospital_type": "Government hospital"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Existing Benefits & Documents", res.data)

        # Valid Step 3 submission with multiple choices
        res = self.client.post("/schemes/step/3", data={
            "treatments": ["Surgery", "Heart disease treatment"],
            "treatment_status": "Doctor has recommended hospitalization",
            "treatment_cost": "₹1 lakh–₹5 lakh",
            "hospital_type": "Government hospital",
            "hospital_accepts_scheme": "yes",
            "doctor_recommended": "yes"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Existing Benefits & Documents", res.data)

    def test_schemes_step4_and_recommendations(self):
        """Test Step 4 document answers and transition to results."""
        with self.client as c:
            # Seed Steps 1-3 in session
            with c.session_transaction() as sess:
                sess["scheme_form"] = {
                    "full_name": "Dattatraya Shinde",
                    "beneficiary": "myself",
                    "age": 73,
                    "gender": "Male",
                    "state": "Maharashtra",
                    "district": "Pune",
                    "residence_type": "Urban",
                    "income": "Below ₹1 lakh",
                    "ration_card": "yes",
                    "ration_card_type": "Orange / Kesari / Priority Household (PHH)",
                    "ayushman_card": "no",
                    "mjpjay_reg": "no",
                    "other_insurance": "No insurance",
                    "govt_employee": "no",
                    "circumstances": ["Senior citizen living alone / Elderly household"],
                    "treatments": ["Heart disease treatment", "Surgery"],
                    "treatment_status": "Doctor has recommended hospitalization",
                    "treatment_cost": "₹1 lakh–₹5 lakh",
                    "hospital_type": "Government hospital",
                    "hospital_accepts_scheme": "yes",
                    "doctor_recommended": "yes",
                }

            # Submit Step 4
            res = c.post("/schemes/step/4", data={
                "doc_aadhaar": "available",
                "doc_ration_card": "available",
                "doc_income_cert": "available",
                "doc_prescription": "available",
                "doc_hospital_estimate": "available",
            }, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Your Healthcare Support Recommendations", res.data)
            self.assertIn(b"Vay Vandana", res.data)
            self.assertIn(b"Mahatma Jyotirao Phule Jan Arogya Yojana", res.data)
            self.assertIn(b"Official Disclaimer:", res.data)

    def test_emergency_notice_handling(self):
        """Verify that when emergency status is flagged, emergency guidance is displayed."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["scheme_form"] = {
                    "full_name": "Emergency Patient",
                    "beneficiary": "myself",
                    "age": 55,
                    "state": "Maharashtra",
                    "district": "Mumbai",
                    "residence_type": "Urban",
                    "income": "Below ₹1 lakh",
                    "ration_card": "no",
                    "treatments": ["Accident and emergency care", "Surgery"],
                    "treatment_status": "Emergency treatment required now",
                    "hospital_type": "Government hospital",
                    "documents": {}
                }
            res = c.get("/schemes/results")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"URGENT EMERGENCY NOTICE", res.data)
            self.assertIn(b"112", res.data)

    def test_save_and_continue_later(self):
        """Verify the Save Progress feature preserves responses."""
        with self.client as c:
            res = c.post("/schemes/step/1", data={
                "action": "save",
                "full_name": "Kavita Rao",
                "beneficiary": "myself",
                "age": "32",
                "state": "Karnataka",
                "district": "Bengaluru",
                "residence_type": "Urban"
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Progress safely saved", res.data)
            self.assertIn(b"Kavita Rao", res.data)

    def test_reset_route(self):
        """Verify reset clears session data."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["scheme_form"] = {"full_name": "Old Data"}
            res = c.get("/schemes/reset", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Questionnaire restarted", res.data)
            with c.session_transaction() as sess:
                self.assertNotIn("scheme_form", sess)

    # -------------------------------------------------------------------------
    # 3. Recommendation Engine Synthetic Test Profiles
    # -------------------------------------------------------------------------
    def test_recommendation_profiles(self):
        """Test rule-based matcher with diverse synthetic demographic scenarios."""
        # Scenario 1: Senior Citizen 70+ in Maharashtra (Universal Cover)
        profile_senior = {
            "full_name": "Balasaheb Patil",
            "beneficiary": "myself",
            "age": 75,
            "state": "Maharashtra",
            "income": "Above ₹10 lakh",  # High income
            "ration_card": "no",
            "treatments": ["Heart disease treatment", "Surgery"],
            "documents": {"aadhaar": "available"}
        }
        recs = recommend_schemes(profile_senior)
        rec_ids = [r["id"] for r in recs]
        self.assertIn("vay_vandana", rec_ids, "Senior 70+ must match Vay Vandana universal cover")
        top_scheme = recs[0]
        self.assertEqual(top_scheme["id"], "vay_vandana")

        # Scenario 2: Pregnant woman seeking institutional delivery & maternity benefit
        profile_maternity = {
            "full_name": "Pooja Sharma",
            "beneficiary": "myself",
            "age": 23,
            "state": "Uttar Pradesh",
            "income": "Below ₹1 lakh",
            "ration_card": "yes",
            "ration_card_type": "Priority Household (PHH)",
            "treatments": ["Pregnancy and maternity care"],
            "documents": {"aadhaar": "available"}
        }
        recs_mat = recommend_schemes(profile_maternity)
        mat_ids = [r["id"] for r in recs_mat]
        self.assertIn("jsy_jssk", mat_ids, "Should match JSY / JSSK free institutional delivery")
        self.assertIn("pmmvy", mat_ids, "Should match PMMVY cash benefit")

        # Scenario 3: Dialysis patient seeking kidney care
        profile_dialysis = {
            "full_name": "Anil Deshmukh",
            "beneficiary": "myself",
            "age": 58,
            "state": "Maharashtra",
            "income": "Below ₹1 lakh",
            "ration_card": "yes",
            "ration_card_type": "Yellow / AAY",
            "treatments": ["Kidney disease or dialysis"],
            "documents": {"aadhaar": "available", "ration_card": "available"}
        }
        recs_dial = recommend_schemes(profile_dialysis)
        dial_ids = [r["id"] for r in recs_dial]
        self.assertIn("pmndp", dial_ids, "Should match PM National Dialysis Programme")
        self.assertIn("mjpjay", dial_ids, "Should match MJPJAY for dialysis in Maharashtra")

        # Scenario 4: Central Government Employee
        profile_cghs = {
            "full_name": "R. K. Verma",
            "beneficiary": "myself",
            "age": 62,
            "state": "Delhi",
            "income": "₹5 lakh–₹10 lakh",
            "govt_employee": "yes",
            "treatments": ["General hospitalization", "Surgery"],
            "documents": {"govt_health_card": "available"}
        }
        recs_cghs = recommend_schemes(profile_cghs)
        self.assertEqual(recs_cghs[0]["id"], "cghs", "Central Govt Employee must prioritize CGHS")

        # Scenario 5: Mental health distress
        profile_mental = {
            "full_name": "Student",
            "beneficiary": "myself",
            "age": 21,
            "state": "Madhya Pradesh",
            "income": "Prefer not to say",
            "treatments": ["Mental healthcare"],
            "documents": {}
        }
        recs_mental = recommend_schemes(profile_mental)
        self.assertEqual(recs_mental[0]["id"], "tele_manas", "Mental health must prioritize Tele-MANAS")

        # Scenario 6: Looking for affordable medicines only
        profile_meds = {
            "full_name": "Deepak Mehta",
            "beneficiary": "myself",
            "age": 50,
            "state": "Gujarat",
            "income": "₹2.5 lakh–₹5 lakh",
            "treatments": ["Medicines and diagnostic tests", "Diabetes and chronic diseases"],
            "documents": {"prescription": "available"}
        }
        recs_meds = recommend_schemes(profile_meds)
        med_ids = [r["id"] for r in recs_meds]
        self.assertIn("pmbjp", med_ids, "Chronic medication & pharmacy must match Janaushadhi PMBJP")

        # Scenario 7: Fallback / empty match verification
        profile_empty = {
            "full_name": "High Income Consult Only",
            "beneficiary": "myself",
            "age": 30,
            "state": "Abroad",
            "income": "Above ₹10 lakh",
            "ration_card": "no",
            "treatments": ["Routine medical consultation"],
            "documents": {}
        }
        recs_empty = recommend_schemes(profile_empty)
        # Verify recommendation handling does not crash
        self.assertIsInstance(recs_empty, list)

    # -------------------------------------------------------------------------
    # 4. Admin Panel & Dynamic Scheme CRUD Tests
    # -------------------------------------------------------------------------
    def test_admin_auth_and_access_control(self):
        """Admin panel requires authentication; redirects unauthenticated users."""
        # Unauthenticated request to /admin redirects to login
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])

        # Invalid login fails
        res_fail = self.client.post("/admin/login", data={
            "email": "admin@swasthyasetu.gov.in",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res_fail.data)

        # Valid login succeeds and shows dashboard
        res_login = self.client.post("/admin/login", data={
            "email": "admin@swasthyasetu.gov.in",
            "password": "admin@123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Admin Dashboard", res_login.data)
        self.assertIn(b"Total Schemes", res_login.data)

    def test_admin_scheme_crud_and_live_recommendation(self):
        """Admin can create a new scheme, and it immediately reflects in user recommendations."""
        with self.client as c:
            # Login as admin
            c.post("/admin/login", data={
                "email": "admin@swasthyasetu.gov.in",
                "password": "admin@123"
            })

            # Create a unique test scheme with new simplified form structure
            scheme_name = "Pradhan Mantri Special Neuro Care Yojana"
            create_res = c.post("/admin/scheme/new", data={
                "name": scheme_name,
                "short_tag": "PM-SNCY",
                "category": "Tertiary Care",
                "govt_level": "Central Government",
                "description": "Comprehensive cashless coverage for neurosurgery and brain injury.",
                "who_benefits": "All Indian citizens with neurological disorders.",
                "eligibility_rules": "Must have confirmed MRI/CT scan report\nHospital must have neurosurgery unit",
                "required_documents": [
                    "Aadhaar Card (Applicant / Patient)",
                    "Doctor's Prescription & Medical Recommendation"
                ],
                "other_required_docs": "MRI / CT Scan report",
                "official_website": "https://mohfw.gov.in/neuro",
                "application_process": "Apply at hospital neuro desk.",
                "states_applicable": "All India (Universal)",
                "income_limit": "No income limit",
                "is_active": "1"
            }, follow_redirects=True)
            self.assertEqual(create_res.status_code, 200)
            self.assertIn(b"Pradhan Mantri Special Neuro Care Yojana", create_res.data)

            # Now test as a citizen filling out the questionnaire needing brain surgery!
            from db import recommend_schemes_from_db
            neuro_patient = {
                "full_name": "Kailash Sharma",
                "beneficiary": "myself",
                "age": 42,
                "state": "Maharashtra",
                "income": "₹2.5 lakh–₹5 lakh",
                "ration_card": "no",
                "treatments": ["Neurosurgery", "Brain surgery"],
                "documents": {"aadhaar": "available"}
            }
            recs = recommend_schemes_from_db(neuro_patient)
            matched_names = [r["name"] for r in recs]
            self.assertIn(scheme_name, matched_names, "Newly created admin scheme must be dynamically recommended!")


# =============================================================================
# 3. Comprehensive Verification of 20 Testing Requirements (Section 12)
# =============================================================================

class UserAuthAndSmartProfileTestSuite(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key-auth-suite"
        self.client = app.test_client()

    # Requirement 1: A new user can register with valid information
    def test_01_user_registration_valid(self):
        import time
        email = f"anita.deshmukh_{int(time.time()*1000)}@example.com"
        res = self.client.post("/register", data={
            "name": "Anita Deshmukh",
            "email": email,
            "password": "SecurePassword123",
            "confirm_password": "SecurePassword123",
            "state": "Maharashtra",
            "district": "Pune",
            "mobile": "9876543210"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome, Anita", res.data)
        self.assertIn(b"Your profile is just getting started", res.data)

    # Requirement 2: Registration rejects invalid email addresses
    def test_02_registration_rejects_invalid_email(self):
        res = self.client.post("/register", data={
            "name": "Invalid Email User",
            "email": "not-an-email-address",
            "password": "Password123",
            "confirm_password": "Password123",
            "state": "Maharashtra",
            "district": "Pune"
        }, follow_redirects=True)
        self.assertIn(b"Please enter a valid email address", res.data)

    # Requirement 3: Registration rejects mismatched passwords
    def test_03_registration_rejects_mismatched_passwords(self):
        res = self.client.post("/register", data={
            "name": "Mismatch User",
            "email": "mismatch@example.com",
            "password": "Password123",
            "confirm_password": "DifferentPassword456",
            "state": "Maharashtra",
            "district": "Pune"
        }, follow_redirects=True)
        self.assertIn(b"Passwords do not match", res.data)

    # Requirement 4: Duplicate email registration is prevented
    def test_04_duplicate_email_registration_prevented(self):
        import time
        email = f"dup_user_{int(time.time()*1000)}@example.com"
        # First registration logs user in
        self.client.post("/register", data={
            "name": "First Instance",
            "email": email,
            "password": "Password123",
            "confirm_password": "Password123",
            "state": "Gujarat",
            "district": "Ahmedabad"
        })
        # Log out so next visitor can access registration form
        self.client.get("/logout")

        # Second registration with same email
        res2 = self.client.post("/register", data={
            "name": "Second Instance",
            "email": email,
            "password": "Password123",
            "confirm_password": "Password123",
            "state": "Gujarat",
            "district": "Surat"
        }, follow_redirects=True)
        self.assertIn(b"already registered with this email", res2.data)

    # Requirement 5: Passwords are stored as hashes (never plaintext)
    def test_05_passwords_stored_as_secure_hashes(self):
        import time
        import db
        email = f"hash_test_{int(time.time()*1000)}@example.com"
        raw_password = "MySuperSecretPlaintextPassword!"
        self.client.post("/register", data={
            "name": "Hash Check User",
            "email": email,
            "password": raw_password,
            "confirm_password": raw_password,
            "state": "Karnataka",
            "district": "Bengaluru"
        })
        user = db.get_user_by_email(email)
        self.assertIsNotNone(user)
        stored_hash = user["password_hash"]
        # Must NOT equal raw plaintext password
        self.assertNotEqual(stored_hash, raw_password)
        # Must be a werkzeug scrypt hash
        self.assertTrue(stored_hash.startswith("scrypt:"))

    # Requirement 6: A user can log in with correct credentials
    def test_06_login_with_correct_credentials(self):
        import time
        email = f"login_ok_{int(time.time()*1000)}@example.com"
        self.client.post("/register", data={
            "name": "Login Tester",
            "email": email,
            "password": "ValidPassword999",
            "confirm_password": "ValidPassword999",
            "state": "Maharashtra",
            "district": "Nashik"
        })
        # Log out first
        self.client.get("/logout")
        # Log back in
        res = self.client.post("/login", data={
            "email": email,
            "password": "ValidPassword999"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome back, Login", res.data)
        self.assertIn(b"My Healthcare Dashboard", res.data)

    # Requirement 7: Incorrect credentials are rejected
    def test_07_incorrect_credentials_rejected(self):
        res = self.client.post("/login", data={
            "email": "nonexistent_beneficiary@example.com",
            "password": "WrongPasswordXYZ"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email address or password", res.data)

    # Requirement 8: Logout ends the authenticated session
    def test_08_logout_ends_session(self):
        import time
        email = f"logout_user_{int(time.time()*1000)}@example.com"
        self.client.post("/register", data={
            "name": "Logout User",
            "email": email,
            "password": "Password123",
            "confirm_password": "Password123",
            "state": "Maharashtra",
            "district": "Nagpur"
        })
        # Confirm in dashboard
        dash_res = self.client.get("/dashboard")
        self.assertEqual(dash_res.status_code, 200)
        # Logout
        logout_res = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"safely logged out", logout_res.data)
        # Cannot access dashboard anymore
        blocked_res = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn(b"Please log in to access your personal dashboard", blocked_res.data)


    # Requirement 9: A logged-out user cannot open protected profile or dashboard pages
    def test_09_protected_routes_require_authentication(self):
        # Ensure fresh logged-out client
        with self.client as c:
            with c.session_transaction() as sess:
                sess.clear()
            for protected_url in ["/dashboard", "/profile", "/profile/edit", "/recommended-schemes"]:
                res = c.get(protected_url, follow_redirects=True)
                self.assertIn(b"Please log in", res.data, f"Route {protected_url} allowed unauthenticated access!")

    # Requirement 10: A new user can access the dashboard without completing their profile
    def test_10_new_user_can_access_dashboard_with_incomplete_profile(self):
        import time
        email = f"new_user_inc_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Pradeep Rao",
                "email": email,
                "password": "Password123",
                "confirm_password": "Password123",
                "state": "Maharashtra",
                "district": "Satara"
            })
            res = c.get("/dashboard")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Welcome, Pradeep", res.data)
            self.assertIn(b"Your profile is just getting started", res.data)
            self.assertIn(b"Complete My Profile", res.data)

    # Requirement 11: Profile completion percentage is calculated correctly
    def test_11_profile_completion_percentage_calculation(self):
        import time
        email = f"calc_pct_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Geeta Sharma",
                "email": email,
                "password": "Password123",
                "confirm_password": "Password123",
                "state": "Maharashtra",
                "district": "Pune"
            })
            # Base completion after registration should be 20%
            dash = c.get("/dashboard")
            self.assertIn(b"20% Complete", dash.data)

            # Save additional sections: Household + Occupation + Healthcare Needs
            c.post("/profile/save", data={
                "name": "Geeta Sharma",
                "state": "Maharashtra",
                "district": "Pune",
                "age": "34",
                "gender": "Female",
                "residence_type": "Urban",
                "beneficiary": "myself",
                "family_size": "4",
                "household_income": "Under ₹1 Lakh",
                "ration_card_category": "BPL / Antyodaya",
                "existing_health_coverage": "no",
                "occupation": "Homemaker",
                "worker_board": "no",
                "special_categories": "None of these",
                "healthcare_needs": ["Hospitalisation or surgery", "Medicines"],
                "healthcare_notes": "Recovering well",
                "doc_id_proof": "yes",
                "doc_address_proof": "yes",
                "doc_ration_card": "yes",
                "doc_health_card": "not_sure"
            })
            # Profile completion should now be significantly higher (>= 80%)
            dash_after = c.get("/dashboard")
            self.assertTrue(b"80% Complete" in dash_after.data or b"85% Complete" in dash_after.data or b"90% Complete" in dash_after.data or b"95% Complete" in dash_after.data or b"100% Complete" in dash_after.data)

    # Requirement 12: Users can skip optional profile fields
    def test_12_skip_optional_profile_fields(self):
        import time
        email = f"skip_opt_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Vijay Gaikwad",
                "email": email,
                "password": "Password123",
                "confirm_password": "Password123",
                "state": "Maharashtra",
                "district": "Thane"
            })
            # Save only age and healthcare need, skipping income, occupation, worker board, notes
            res = c.post("/profile/save", data={
                "name": "Vijay Gaikwad",
                "state": "Maharashtra",
                "district": "Thane",
                "age": "28",
                "healthcare_needs": ["Eye care"]
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Profile updated successfully", res.data)

    # Requirement 13: Users can save their profile and continue later
    def test_13_save_profile_and_continue_later(self):
        import time
        email = f"cont_later_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Meena Joshi",
                "email": email,
                "password": "Password123",
                "confirm_password": "Password123",
                "state": "Maharashtra",
                "district": "Kolhapur"
            })
            res = c.post("/profile/save", data={
                "name": "Meena Joshi",
                "state": "Maharashtra",
                "district": "Kolhapur",
                "action": "continue_later",
                "age": "45",
                "healthcare_needs": ["Diagnostic tests"]
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Profile saved! Your current profile is", res.data)
            self.assertIn(b"My Healthcare Dashboard", res.data)

    # Requirement 14: Saved data persists after logout and login
    def test_14_saved_data_persists_after_logout_and_login(self):
        import time
        email = f"persist_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Persistent User",
                "email": email,
                "password": "SecretPassword123",
                "confirm_password": "SecretPassword123",
                "state": "Maharashtra",
                "district": "Solapur"
            })
            c.post("/profile/save", data={
                "name": "Persistent User",
                "state": "Maharashtra",
                "district": "Solapur",
                "age": "52",
                "gender": "Male",
                "healthcare_needs": ["Kidney disease or dialysis"],
                "dialysis_prescribed": "yes"
            })
            # Logout
            c.get("/logout")
            # Log in again
            c.post("/login", data={"email": email, "password": "SecretPassword123"})
            prof_res = c.get("/profile")
            self.assertIn(b'value="52"', prof_res.data)
            self.assertIn(b'Kidney disease or dialysis', prof_res.data)

    # Requirement 15: Users cannot access another user's profile
    def test_15_user_isolation_prevent_cross_user_access(self):
        import time
        email_a = f"user_a_{int(time.time()*1000)}@example.com"
        email_b = f"user_b_{int(time.time()*1000)}@example.com"
        # User A registers and saves secret note
        with self.client as c:
            c.post("/register", data={
                "name": "User Alpha", "email": email_a, "password": "PasswordA123",
                "confirm_password": "PasswordA123", "state": "Maharashtra", "district": "Pune"
            })
            c.post("/profile/save", data={
                "name": "User Alpha", "state": "Maharashtra", "district": "Pune",
                "healthcare_notes": "AlphaSecretMedicalNote99"
            })
            c.get("/logout")

            # User B logs in
            c.post("/register", data={
                "name": "User Beta", "email": email_b, "password": "PasswordB123",
                "confirm_password": "PasswordB123", "state": "Maharashtra", "district": "Mumbai"
            })
            prof_b = c.get("/profile")
            # User B should NOT see User A's data
            self.assertNotIn(b"AlphaSecretMedicalNote99", prof_b.data)
            self.assertIn(b"User Beta", prof_b.data)

    # Requirement 16: Scheme recommendations change when relevant profile information changes
    def test_16_recommendations_change_when_profile_changes(self):
        import time
        email = f"rec_change_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Kavita Shinde", "email": email, "password": "Password123",
                "confirm_password": "Password123", "state": "Maharashtra", "district": "Amravati"
            })
            # Initially no dialysis scheme specifically targeted
            rec_initial = c.get("/recommended-schemes")
            self.assertNotIn(b"Pradhan Mantri National Dialysis Programme", rec_initial.data)

            # Update profile with Dialysis need
            c.post("/profile/save", data={
                "name": "Kavita Shinde", "state": "Maharashtra", "district": "Amravati",
                "healthcare_needs": ["Kidney disease or dialysis"]
            })
            rec_after = c.get("/recommended-schemes")
            self.assertIn(b"Pradhan Mantri National Dialysis Programme", rec_after.data)

    # Requirement 17: Missing information produces targeted follow-up questions
    def test_17_missing_info_produces_targeted_follow_up(self):
        import time
        email = f"follow_up_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Sanjay Jadhav", "email": email, "password": "Password123",
                "confirm_password": "Password123", "state": "Maharashtra", "district": "Jalgaon"
            })
            c.post("/profile/save", data={
                "name": "Sanjay Jadhav", "state": "Maharashtra", "district": "Jalgaon",
                "healthcare_needs": ["Kidney disease or dialysis"]
            })
            # Dialysis missing question should appear on dashboard
            dash = c.get("/dashboard")
            self.assertIn(b"Has dialysis been prescribed by a doctor?", dash.data)

            # Answer quick question via POST /profile/quick-answer
            ans_res = c.post("/profile/quick-answer", data={
                "question_key": "dialysis_prescribed",
                "answer_value": "yes"
            }, follow_redirects=True)
            self.assertEqual(ans_res.status_code, 200)
            self.assertIn(b"Your profile has been updated with your response", ans_res.data)

    # Requirement 18: State-specific recommendations do not appear universally
    def test_18_state_specific_recommendations(self):
        import time
        email_mh = f"mh_user_{int(time.time()*1000)}@example.com"
        email_up = f"up_user_{int(time.time()*1000)}@example.com"
        with self.client as c:
            # Maharashtra User
            c.post("/register", data={
                "name": "MH Resident", "email": email_mh, "password": "Password123",
                "confirm_password": "Password123", "state": "Maharashtra", "district": "Pune"
            })
            c.post("/profile/save", data={
                "name": "MH Resident", "state": "Maharashtra", "district": "Pune",
                "healthcare_needs": ["Hospitalisation or surgery"]
            })
            mh_recs = c.get("/recommended-schemes")
            self.assertIn(b"Mahatma Jyotirao Phule Jan Arogya Yojana", mh_recs.data)
            c.get("/logout")

            # Uttar Pradesh User
            c.post("/register", data={
                "name": "UP Resident", "email": email_up, "password": "Password123",
                "confirm_password": "Password123", "state": "Uttar Pradesh", "district": "Lucknow"
            })
            c.post("/profile/save", data={
                "name": "UP Resident", "state": "Uttar Pradesh", "district": "Lucknow",
                "healthcare_needs": ["Hospitalisation or surgery"]
            })
            up_recs = c.get("/recommended-schemes")
            # MJPJAY is Maharashtra specific; UP resident should NOT get MJPJAY
            self.assertNotIn(b"Mahatma Jyotirao Phule Jan Arogya Yojana", up_recs.data)

    # Requirement 19: Emergency-related needs are handled without forcing a lengthy questionnaire
    def test_19_emergency_needs_handled_gracefully(self):
        import time
        email = f"emergency_{int(time.time()*1000)}@example.com"
        with self.client as c:
            c.post("/register", data={
                "name": "Emergency Patient", "email": email, "password": "Password123",
                "confirm_password": "Password123", "state": "Maharashtra", "district": "Pune"
            })
            # User only selects hospitalisation and financial assistance
            c.post("/profile/save", data={
                "name": "Emergency Patient", "state": "Maharashtra", "district": "Pune",
                "healthcare_needs": ["Hospitalisation or surgery", "Financial assistance for expensive treatment"]
            })
            recs = c.get("/recommended-schemes")
            self.assertEqual(recs.status_code, 200)
            # Both PM-JAY and Rashtriya Arogya Nidhi should be recommended
            self.assertIn(b"PM-JAY", recs.data)
            self.assertIn(b"Rashtriya Arogya Nidhi", recs.data)

    # Requirement 20: Existing SwasthyaSetu AI features remain functional
    def test_20_existing_features_fully_functional(self):
        # 1. Scheme Finder
        res_finder = self.client.get("/schemes")
        self.assertEqual(res_finder.status_code, 200)
        # 2. Document Centre
        res_docs = self.client.get("/documents")
        self.assertEqual(res_docs.status_code, 200)
        # 3. Hospital Finder
        res_hosp = self.client.get("/hospitals")
        self.assertEqual(res_hosp.status_code, 200)
        # 4. Medical Records
        res_rec = self.client.get("/records")
        self.assertEqual(res_rec.status_code, 200)
        # 5. AI Assistant
        res_asst = self.client.get("/assistant")
        self.assertEqual(res_asst.status_code, 200)
        # 6. Tracker
        res_track = self.client.get("/tracking")
        self.assertEqual(res_track.status_code, 200)
        # 7. Admin Login
        res_admin = self.client.get("/admin/login")
        self.assertEqual(res_admin.status_code, 200)

    # -------------------------------------------------------------------------
    # Conversational AI Assistant Tests
    # -------------------------------------------------------------------------
    def test_conversational_assistant_page(self):
        """GET /assistant loads conversational interface with chips and clear button."""
        res = self.client.get("/assistant")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SwasthyaSetu Guide", res.data)
        self.assertIn(b"chat-messages", res.data)
        self.assertIn(b"New Chat", res.data)

    def test_conversational_assistant_ajax_emergency(self):
        """Emergency message triggers instant emergency numbers and guidance."""
        res = self.client.post("/assistant",
                                json={"message": "I need urgent ambulance for chest pain"},
                                content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("108", data["text"])
        self.assertTrue(any("Hospitals" in l["text"] for l in data.get("links", [])))

    def test_conversational_assistant_ajax_dialysis(self):
        """Dialysis condition query gives free dialysis scheme details."""
        res = self.client.post("/assistant",
                                json={"message": "Is kidney dialysis covered free under government schemes?"},
                                content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue("Dialysis" in data["text"] or "PM-JAY" in data["text"])
        self.assertTrue(len(data.get("chips", [])) > 0)

    def test_conversational_assistant_ajax_documents(self):
        """Document checklist query returns required documents."""
        res = self.client.post("/assistant",
                                json={"message": "What documents do I need for Ayushman card?"},
                                content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue("Aadhaar" in data["text"] or "Ration Card" in data["text"])

    def test_conversational_assistant_ajax_hospitals(self):
        """Hospital bed search query lists real hospitals from database."""
        res = self.client.post("/assistant",
                                json={"message": "Find hospitals with ICU beds available"},
                                content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue("ICU" in data["text"] or "Hospital" in data["text"] or "beds" in data["text"])

    def test_conversational_assistant_session_and_clear(self):
        """Assistant stores chat turns in session and clear=1 resets conversation."""
        with self.client as c:
            c.post("/assistant", json={"message": "Hello"}, content_type="application/json")
            c.post("/assistant", json={"message": "Tell me about senior citizen schemes"}, content_type="application/json")
            with c.session_transaction() as sess:
                self.assertGreaterEqual(len(sess.get("chat_history", [])), 4)

            # Clear session
            res_clear = c.get("/assistant?clear=1", follow_redirects=True)
            self.assertEqual(res_clear.status_code, 200)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get("chat_history", []), [])

    def test_set_language_endpoint(self):
        """Test setting Hindi and Marathi language preferences via endpoint."""
        with self.client as c:
            # Set Hindi
            res_hi = c.post("/set-language/hi")
            self.assertEqual(res_hi.status_code, 200)
            self.assertEqual(res_hi.get_json()["lang"], "hi")
            with c.session_transaction() as sess:
                self.assertEqual(sess.get("lang"), "hi")

            # Set Marathi
            res_mr = c.post("/set-language/mr")
            self.assertEqual(res_mr.status_code, 200)
            self.assertEqual(res_mr.get_json()["lang"], "mr")
            with c.session_transaction() as sess:
                self.assertEqual(sess.get("lang"), "mr")

    def test_multilingual_assistant_responses(self):
        """Test that conversational assistant replies in Marathi and Hindi when queried in those languages."""
        # Query in Marathi
        res_mr = self.client.post("/assistant",
                                  json={"message": "नमस्कार, तातडीची आपत्कालीन मदत हवी आहे"},
                                  content_type="application/json")
        self.assertEqual(res_mr.status_code, 200)
        data_mr = res_mr.get_json()
        self.assertIn("108", data_mr["text"])
        self.assertTrue("रुग्णवाहिका" in data_mr["text"] or "आपत्कालीन" in data_mr["text"])

        # Query in Hindi
        res_hi = self.client.post("/assistant",
                                  json={"message": "नमस्ते, मुझे आपातकालीन एम्बुलेंस चाहिए"},
                                  content_type="application/json")
        self.assertEqual(res_hi.status_code, 200)
        data_hi = res_hi.get_json()
        self.assertIn("108", data_hi["text"])
        self.assertTrue("एम्बुलेंस" in data_hi["text"] or "आपातकालीन" in data_hi["text"])


if __name__ == "__main__":
    unittest.main()
