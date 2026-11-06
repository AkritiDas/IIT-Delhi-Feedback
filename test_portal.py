"""
Automated End-to-End Test Suite for IIT Delhi Virtual Labs Smart Feedback Portal.
Tests form validation, submission, anonymous mode, screenshot uploads, admin authentication,
dashboard analytics, and CSV export.
"""
import io
import json
import unittest
from app import app
from database import db_manager

class IITDFeedbackPortalTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        db_manager.init_database(seed_demo=True)

    def test_01_landing_page_renders(self):
        """Verify public landing page renders with IIT Delhi branding and hero stats."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("IIT Delhi Virtual Labs", html)
        self.assertIn("Your Experience Helps Us Improve", html)
        self.assertIn("Experiment Feedback & Quality Audit", html)
        self.assertIn("Star Rating System", html)
        self.assertIn("Attach a Screenshot", html)

    def test_02_submit_valid_identified_feedback(self):
        """Submit full non-anonymous feedback with ratings and mock screenshot."""
        payload = {
            "full_name": "Rohan Deshmukh",
            "email": "rohan.deshmukh@iitd.ac.in",
            "mobile_number": "+91 9988776655",
            "user_type": "Student",
            "subject": "Electronics & Communication",
            "experiment_name": "Op-Amp Inverting Amplifier Simulation",
            "experiment_url": "https://vlabs.iitd.ac.in/ece/op-amp",
            "device": "Laptop",
            "browser": "Chrome",
            "overall_rating": "5",
            "experiment_rating": "5",
            "navigation_rating": "4",
            "technical_rating": "5",
            "selected_issues": ["Simulation is not working"],
            "technical_details": "Output voltage clipping when gain > 100",
            "experience_description": "The virtual oscilloscope simulation is very intuitive and accurately reflects real lab results.",
            "positive_experience": "Accurate sine wave visualization.",
            "improvement_suggestions": "Add an AC frequency response sweep option.",
            "recommendation": "Yes",
            "anonymous_status": "0"
        }

        # Add a dummy test image upload
        image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        data = {
            **payload,
            "screenshots": (io.BytesIO(image_content), "test_clipping_error.png")
        }

        res = self.client.post("/api/feedback", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 201)
        res_json = json.loads(res.data)
        self.assertTrue(res_json["success"])
        self.assertTrue(res_json["reference_id"].startswith("IITD-VL-2026-"))

        # Verify record exists in DB
        record = db_manager.get_feedback_by_reference(res_json["reference_id"])
        self.assertIsNotNone(record)
        self.assertEqual(record["full_name"], "Rohan Deshmukh")
        self.assertEqual(record["overall_rating"], 5)
        self.assertEqual(record["anonymous_status"], 0)
        self.assertEqual(len(record["screenshot_paths"]), 1)

    def test_03_submit_anonymous_feedback(self):
        """Submit feedback in anonymous mode; contact info should not be saved."""
        payload = {
            "user_type": "Researcher",
            "subject": "Physics",
            "experiment_name": "Diffraction Grating Spectrometry",
            "device": "Desktop",
            "browser": "Firefox",
            "overall_rating": "4",
            "experiment_rating": "4",
            "navigation_rating": "3",
            "technical_rating": "4",
            "selected_issues": ["Website is loading slowly"],
            "experience_description": "Clean spectral lines generated, though the calibration slider needed double clicking.",
            "recommendation": "Yes",
            "anonymous_status": "1"
        }

        res = self.client.post("/api/feedback", data=payload)
        self.assertEqual(res.status_code, 201)
        res_json = json.loads(res.data)
        ref_id = res_json["reference_id"]

        record = db_manager.get_feedback_by_reference(ref_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["anonymous_status"], 1)
        self.assertIsNone(record["full_name"])
        self.assertIsNone(record["email"])

    def test_04_validation_rejections(self):
        """Ensure invalid inputs (empty description, invalid ratings, missing name) are rejected with HTTP 400."""
        # 1. Missing description
        bad_payload = {
            "full_name": "Test User",
            "email": "test@domain.com",
            "subject": "Computer Science",
            "experiment_name": "Graph Traversal",
            "overall_rating": "4",
            "experiment_rating": "4",
            "navigation_rating": "4",
            "technical_rating": "4",
            "experience_description": "Short",  # under 10 chars
            "anonymous_status": "0"
        }
        res = self.client.post("/api/feedback", data=bad_payload)
        self.assertEqual(res.status_code, 400)
        res_json = json.loads(res.data)
        self.assertFalse(res_json["success"])
        self.assertIn("at least 10 characters", res_json["message"])

        # 2. Missing rating
        bad_payload["experience_description"] = "This is a valid length description for the experiment."
        bad_payload["overall_rating"] = "0"
        res = self.client.post("/api/feedback", data=bad_payload)
        self.assertEqual(res.status_code, 400)

    def test_05_admin_portal_flow(self):
        """Verify admin login protection, dashboard metrics, inspection modal API, and CSV export."""
        # 1. Unauthenticated access to dashboard should redirect
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 302)

        # 2. Login with bad credentials should fail
        res = self.client.post("/admin/login", data={"username": "wrong", "password": "bad"})
        self.assertIn("Invalid administrator credentials", res.data.decode("utf-8"))

        # 3. Login with correct credentials
        res = self.client.post("/admin/login", data={"username": "admin", "password": "admin@iitd2026"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Quality Control & Feedback Dashboard", res.data.decode("utf-8"))

        # 4. View dashboard with active session
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Total Submissions", res.data.decode("utf-8"))

        # 5. Export CSV
        res = self.client.get("/admin/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/csv; charset=utf-8")
        csv_text = res.data.decode("utf-8")
        self.assertIn("Reference ID,Submitted At,Anonymous", csv_text)

        # 6. Admin API feedback detail
        res = self.client.get("/admin/api/feedback/1")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("reference_id", data["data"])

    def test_06_receipt_page(self):
        """Verify the public confirmation/receipt page displays correctly."""
        res = self.client.get("/feedback/IITD-VL-2026-DEMO01")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("IITD-VL-2026-DEMO01", html)
        self.assertIn("Submission Summary", html)

if __name__ == "__main__":
    unittest.main()

