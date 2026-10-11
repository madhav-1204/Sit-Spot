import os
import unittest
import tempfile

# Use temporary database for testing
test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["SITSPOT_DB"] = test_db_path

import db
import ollama_client

class TestSitSpotCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        os.close(test_db_fd)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    def test_database_initialization_and_empty_count(self):
        count = db.get_entry_count()
        self.assertEqual(count, 0)
        self.assertIsNone(db.get_last_entry())

    def test_save_and_retrieve_entry(self):
        entry_id = db.save_entry(
            target_minutes=10,
            outside_seconds=600,
            screen_seconds=50,
            prompt="Watch one branch until the wind stops.",
            raw_notes="Wind moved maple branches. One leaf dropped.",
            tidy_entry="I watched the maple branches sway in the wind until one leaf fell.",
            follow_up="Where did the leaf land?",
            is_raw_only=0
        )
        self.assertEqual(entry_id, 1)
        self.assertEqual(db.get_entry_count(), 1)
        
        last = db.get_last_entry()
        self.assertIsNotNone(last)
        self.assertEqual(last["target_minutes"], 10)
        self.assertEqual(last["outside_seconds"], 600)
        self.assertEqual(last["screen_seconds"], 50)
        self.assertEqual(last["raw_notes"], "Wind moved maple branches. One leaf dropped.")

    def test_offline_fallback_prompt(self):
        prompt, used_ai, error = ollama_client.generate_session_prompt("morning", "October", "None")
        self.assertTrue(len(prompt) > 0)
        self.assertIsInstance(prompt, str)

    def test_offline_tidy_notes_graceful_handling(self):
        tidy, follow_up, used_ai, error = ollama_client.tidy_notes("two pigeons on roof")
        if not used_ai:
            self.assertIsNotNone(error)
            self.assertTrue("Ollama" in error or "raw notes" in error)

if __name__ == "__main__":
    unittest.main()
