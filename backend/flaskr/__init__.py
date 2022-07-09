import os
# import psycopg2
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
import random
from models import setup_db, Question, Category, db



QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {'origins': '*'}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow_Methods', 'GET, DELETE, POST, PATCH, PUT')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Implement pagination
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
    
        categories = Category.query.all() 
        for category in categories:
            format_categories= category.format(),
        return jsonify({'success': True,
            'plants':format_categories[start:end],
            'total_plants':len(format_categories)
            })
            
          #  'categories': categories_values()


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    def categories_values():
        categories_query = db.session.query(Category).order_by(Category.id).all()
        categories = {}
        for category in categories_query:
            categories[str(category.id)] = category.type
        return categories
        
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        page = request.args.get('page', 1, type=int)

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = QUESTIONS_PER_PAGE + start
        current_questions = db.session.query(Question).order_by(Question.id).paginate(page=page, per_page=QUESTIONS_PER_PAGE).items
        # questions_query = db.session.query(Question).order_by(Question.id).all()

        questions = []
        for question in current_questions:
            questions.append({
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'difficulty': question.difficulty,
                'category': question.category
            })
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'questions': questions[start: end],
            'success': True,
            'total_questions': len(questions),
            'categories': categories_values(),
            'currentCategory': random.choice(list(categories_values().values()))
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        questions_query = Question.query.get(id)
        try:
            questions_query.delete()
        except:
            abort(404)
        data = {
            'id': id,
            'success': True
        }
        return jsonify(data)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()
        
        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')

        if body is None:
            abort(422)

        try:
            new_question = Question(
                question=question,
                answer=answer,
                difficulty=int(difficulty),
                category=int(category)
            )
            new_question.insert()
            #question = new_question.format()
        except:
            abort(404)
        finally:
            db.session.close()
        return jsonify({
            "success": True,
            "question": question,
        }), 201
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search_term = request.get_json()['searchTerm']
        search_query = Question.query.filter(Question.question.contains(search_term)).all()

        questions = []

        if not search_query:
            questions.append({})
            abort(422)
        else:
            for question in search_query:
                questions.append({
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'difficulty': question.difficulty,
                'category': question.category
            })

        data = {
            'questions': questions,
            'total_questions': len(questions),
            'success': True,
            'current_category': random.choice(questions).get('category') if len(questions) > 0 else 'no category'
        }
        return jsonify(data)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def retrieve_by_category(id):
        question_category = Question.query.filter(Question.category == id).all()
        questions = []

        for question in question_category:
            questions.append({
                'id': question.id,
                'question': question.question,
                'answer': question.answer,
                'difficulty': question.difficulty,
                'category': question.category
            })
        if len(questions) != 0:
            data = {
                'questions': questions,
                'success': True,
                'total_questions': len(question_category),
                'current_category': random.choice(list(categories_values().values()))
            }

            return jsonify(data)
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play():
        past_questions = request.get_json()['previous_questions']
        quiz_category = request.get_json()['quiz_category']
        print(quiz_category)

        query = Question.query.all()
        current_question = []

        if past_questions is None:
            abort(422)
        else:
            for question in query:
                if len(past_questions) == 0 and int(quiz_category['id']) != question.category:
                    current_question.append(question.format())
                else:
                    for last in past_questions:
                        if last != question.id and int(quiz_category['id']) != question.category:
                            current_question.append(question.format())
        return jsonify({'question': random.choice(current_question), 'success': True})
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    return app