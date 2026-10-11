import os
import unittest
import tempfile
import time

test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["SITSPOT_DB"] = test_db_path

import db
from app import app

class TestSitSpotRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        os.close(test_db_fd)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    def test_01_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sit Spot", response.data)
        self.assertIn(b"Go outside", response.data)
        self.assertTrue(b"0</strong> session" in response.data or b"session" in response.data)

    def test_02_start_session_renders_out_screen(self):
        response = self.client.post("/start", data={"duration": "10"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"phone away", response.data)
        self.assertIn(b"I'm back", response.data)

    def test_03_back_session_renders_notes_screen(self):
        now = time.time() - 300
        response = self.client.post("/back", data={
            "start_timestamp": str(now),
            "prompt": "Listen to the birds.",
            "target_minutes": "10",
            "prompt_screen_seconds": "5"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Rough notes", response.data)
        self.assertIn(b"Tidy notes", response.data)
        self.assertIn(b"Save raw only", response.data)

    def test_04_tidy_save_raw_only_flow(self):
        response = self.client.post("/tidy", data={
            "raw_notes": "A squirrel ran along the fence.",
            "action": "save_raw",
            "target_minutes": "5",
            "prompt": "Find motion in the yard.",
            "outside_seconds": "320",
            "prompt_screen_seconds": "10",
            "notes_start_timestamp": str(time.time() - 20)
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Past entries", response.data)
        self.assertIn(b"A squirrel ran along the fence.", response.data)

    def test_05_save_final_entry_both(self):
        response = self.client.post("/save", data={
            "target_minutes": "10",
            "outside_seconds": "610",
            "screen_seconds": "40",
            "prompt": "Count three different greens.",
            "raw_notes": "Ferns dark green, moss light green.",
            "tidy_entry": "I observed dark green ferns and light green moss on the stones.",
            "follow_up": "Did you see any new shoots?",
            "action": "save_both"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"I observed dark green ferns", response.data)
        self.assertIn(b"Did you see any new shoots?", response.data)

    def test_06_entries_page_with_entries(self):
        response = self.client.get("/entries")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"What keeps showing up", response.data)
        self.assertIn(b"A squirrel ran along the fence.", response.data)

if __name__ == "__main__":
    unittest.main()
