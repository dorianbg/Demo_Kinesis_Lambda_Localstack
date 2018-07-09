# Flask imports
from flask_api import FlaskAPI
from flask import request
import math

# Init FlaskAPI app
app = FlaskAPI(__name__)

# Set response to json only (globally)
app.config['DEFAULT_RENDERERS'] = [
    'flask_api.renderers.JSONRenderer'
]


# Handle 404 errors (Not found)
@app.errorhandler(404)
def not_found(error):
    return {'error': 'endpoint is not found'}, 404


@app.route('/messages/', methods=['POST'])
def get_data():
    post_data = request.data
    print('Received: ', post_data['data'], ' root is ', int(math.sqrt(int(post_data['data']))))


@app.route('/messages/<string:name>/', methods=['GET'])
def get_message(name):
    print(name)


# Run App
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
