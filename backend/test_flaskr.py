import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """success - creates a new question"""
    def test_create_new_question(self):
        self.new_question = {
          'question': 'What is the capital of Nigeria?',
          'answer': 'Abuja',
          'category': 2,
          'difficulty': 2 
        }
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)

    """failure - failed to create question"""
    def test_question_not_created(self):
        response = self.client().post('/questions')
        print(response)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'bad request')
        self.assertEqual(data['success'], False)

    """success - this get paginated questions"""
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        print(response)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data))
        self.assertEqual(data['success'], True)

    """failure - get paginated questions"""
    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    """ success - find search term"""
    def test_get_question_search(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'capital'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['success'], True)

    """ failure - fails to find search-term """
    def test_question_search_without_results(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'jessie'})
        data = json.loads(response.data)
        print(data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    """ success - deletes a question"""
    def test_question_deletion(self):
        # creates a question and gets id
        del_response = self.client().delete(f'/questions/3')
        data = del_response.get_json()

        self.assertEqual(del_response.status_code, 404)
        self.assertEqual(data['id'], '3')
        self.assertEqual(data['success'], True)

    """ failure - failed to delete question"""
    def test_404_if_question_does_not_exist(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)


    """ success - post quiz """
    def test_get_quizzes(self):
        self.new_quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': '1'}
        }
        response = self.client().post('/quizzes', json=self.new_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    #""" failure - quiz not posted """
    # def test_question_search_without_results(self):
    #     def test_quiz_not_created(self):
    #     data = json.loads(response.data)
    #     response = self.client().post('/quizzes')
    #     print(response)
    
    #     data = json.loads(response.data)
    #     print(data)

    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(data['message'], 'resource not found')
    #     self.assertEqual(data['success'], False)

    """ success - get questions by category"""
    def test_get_questions_by_category(self):
        result = self.client().get('categories/1/questions')
        print(result.data)

        # checks status and questions in the object returned

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()['success'], True)
        self.assertIn("questions", result.get_json())

    """ failure - fails to get questions by category"""
    def test_get_questions_by_category_error(self):
        result = self.client().get('/categories/8100/questions')
        # checks
        # checks searching by category that doesn't exist
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.get_json()['success'], False)
        self.assertIn("message", result.get_json())
        self.assertEqual(result.get_json()['message'], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()