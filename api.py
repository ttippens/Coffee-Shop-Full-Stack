import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
COMPLETE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('drinks', methods=['GET'])
def drinks():

    all_drinks = Drink.query.all()
    try:
        if all_drinks is not None:
            drinks = [drink.short() for drink in all_drinks]
            return jsonify({
                'success': True,
                'drinks': drinks
            })
    except Exception:
        abort(404)


'''
COMPLETE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail():

    all_drinks = Drink.query.all()
    try:
        if all_drinks is not None:
            drinks = [drink.long() for drink in all_drinks]
            return jsonify({
                'success': True,
                'drinks': drinks
            })
    except Exception:
        abort(404)


'''
COMPLETE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():

    form = request.get_json()

    new_title = form.get('title')
    new_recipe = form.get('recipe')

    if new_title is None or new_recipe is None:
        abort(422)

    try:
        drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        ).insert()

        drink = Drink.query.filter_by(title=new_title, recipe=new_recipe).one_or_none()
        drink.long()

        return jsonify({
            'success': True,
            'drinks': drink
        })
    except Exception:
        abort(422)

'''
COMPLETE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):

    form = request.get_json()

    updated_title = form.get('title')
    updated_recipe = form.get('recipe')

    if updated_title is None or updated_recipe is None:
        abort(422)

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(422)
    
    try:
        drink.title = updated_title
        drink.recipe = json.dumps(updated_recipe)
        drink.update()

        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        drink.long()

        return jsonify({
            'success': True,
            'dirnks': drink
        })
    except Exception:
        abort(422)

    
'''
COMPLETE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception:
        abort(422)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
COMPLETE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

'''
COMPLETE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"                
                    }), 404

'''
COMPLETE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authorization_error(error):
    return jsonify({
                    "success": False,
                    "error": AuthError,
                    "message": "Error with authorization."
                    }), AuthError

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Unauthorized."
                    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad request."
                    }), 400