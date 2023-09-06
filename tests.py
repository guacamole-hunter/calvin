
import unittest
from models import ManualModel
from controllers import ManualController

class TestManualAssistant(unittest.TestCase):
    def setUp(self):
        self.model = ManualModel()
        self.controller = ManualController(self.model)

    def test_search_manual(self):
        response, key = self.controller.handle_query("calibration")
        self.assertIsNotNone(response)
        self.assertIsNotNone(key)

    def test_chat_history(self):
        self.controller.handle_query("calibration")
        self.controller.handle_query("repair")
        context = self.model.get_chat_context()
        self.assertEqual(len(context), 2)

    def test_vectorization(self):
        # Testing if the content is being vectorized properly
        content = "This is a test content for vectorization."
        vector = self.model.vectorizer.transform([content])
        self.assertIsNotNone(vector)

    def test_redis_connection(self):
        # Testing if the Redis connection is established properly
        self.assertIsNotNone(self.model.redis_db)

if __name__ == '__main__':
    unittest.main()

