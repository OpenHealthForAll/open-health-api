from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.integrations.flask_oauth2 import current_token
from authlib.integrations.sqla_oauth2 import create_bearer_token_validator
from dotenv import load_dotenv
from flask import Flask

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
@require_oauth()
def get_health_data_list():
    user = current_token.user
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


if __name__ == '__main__':
    app.run()
