from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.integrations.flask_oauth2 import current_token
from authlib.integrations.sqla_oauth2 import create_bearer_token_validator
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from models import db, OAuth2Token, HealthData

load_dotenv()

require_oauth = ResourceProtector()

# protect resource
bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
require_oauth.register_token_validator(bearer_cls())

app = Flask(__name__)

# load default configuration
app.config.from_object('settings')

# Initialize the database
db.init_app(app)


@app.route('/health-data')
def get_health_data_list():
    try:
        with require_oauth.acquire() as token:
            user = token.user
            health_data_list = HealthData.query.with_entities(
                HealthData.id,
                HealthData.data,
                HealthData.created_at
            ).filter_by(author_id=user.id).all()
            return {
                'data': [{
                    'id': health_data.id,
                    'data': health_data.data,
                    'created_at': health_data.created_at
                } for health_data in health_data_list]
            }
    except:
        return {
            "error": "invalid_token",
            "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
        }, 401


@app.route('/workout-program', methods=['POST'])
def add_workout_program():
    try:
        with require_oauth.acquire() as token:
            user = token.user
            data = request.get_json()
            
            # Create a new health data record for the workout program
            workout_program = HealthData(
                type='workout_program',
                data=data,
                author_id=user.id
            )
            
            db.session.add(workout_program)
            db.session.commit()
            
            return {
                'id': workout_program.id,
                'data': workout_program.data,
                'created_at': workout_program.created_at
            }, 201
    except:
        return {
            "error": "invalid_token",
            "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
        }, 401


@app.route('/workout-program', methods=['GET'])
def get_workout_programs():
    try:
        with require_oauth.acquire() as token:
            user = token.user
            workout_programs = HealthData.query.with_entities(
                HealthData.id,
                HealthData.data,
                HealthData.created_at
            ).filter_by(author_id=user.id, type='workout_program').all()
            
            return {
                'data': [{
                    'id': program.id,
                    'data': program.data,
                    'created_at': program.created_at
                } for program in workout_programs]
            }
    except:
        return {
            "error": "invalid_token",
            "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
        }, 401


@app.route('/workout-program/<program_id>', methods=['PUT'])
def update_workout_program(program_id):
    try:
        with require_oauth.acquire() as token:
            user = token.user
            data = request.get_json()
            
            # Find the workout program by ID and ensure it belongs to the current user
            workout_program = HealthData.query.filter_by(
                id=program_id, 
                author_id=user.id, 
                type='workout_program'
            ).first()
            
            if not workout_program:
                return {
                    "error": "not_found",
                    "error_description": "Workout program not found or you don't have permission to modify it."
                }, 404
            
            # Update the workout program data
            workout_program.data = data
            db.session.commit()
            
            return {
                'id': workout_program.id,
                'data': workout_program.data,
                'created_at': workout_program.created_at
            }
    except:
        return {
            "error": "invalid_token",
            "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons."
        }, 401


if __name__ == '__main__':
    app.run()
