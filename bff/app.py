from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify, render_template
from flask_cors import CORS, cross_origin
from functools import wraps
import openai
from openai import OpenAI
import os
from get_opportunity import get_all_opportunities
import secrets
from get_sales_notes import get_sales_notes
import json
import requests
import logging
import subprocess

load_dotenv()

API_KEY = os.getenv('API_KEY')
ORG_ID = os.getenv('org_id')
client = OpenAI(api_key=API_KEY, organization=ORG_ID)

API_SECRET = os.getenv('API_SECRET')
secret_key = secrets.token_urlsafe(32)

max_tokens = 500

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

CORS(app)

logging.basicConfig(level=logging.INFO)
# Create a logger for your module
logger = logging.getLogger(__name__)

# Create a FileHandler for INFO-level messages
info_handler = logging.FileHandler('application.log')
info_handler.setLevel(logging.INFO)
info_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_format)

# Create a FileHandler for ERROR-level messages
error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)
error_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_format)

# Add the handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)


def require_api_key(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_SECRET:
            return jsonify({'error': 'Invalid API Key'}), 401
        return func(*args, **kwargs)
    return decorated


def log_request_response(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            # Log the request details
            logger.info(f"Request: {request.method} {request.url}")
            logger.info(f"Request Data: {request.get_data().decode('utf-8')}")

            # Call the actual function
            response = func(*args, **kwargs)
            # Log the response details
            if isinstance(response, list):
                logger.info(
                f"Response Data: {response}\n")
                return response
            logger.info(
                f"Response Data: {response.response}\n")
            return response
        except Exception as e:
            # Log any exceptions that may occur
            logger.error(f"An error occurred: {str(e)}")
            raise
    return decorated


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to fetch data. Status code: {response.status_code}"


def create_chat_response(messages, model_name):
    logger.info(messages)
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            max_tokens=500,
            temperature=0,
        )
        response = response.choices[0].message.content
        return jsonify({"answer": response})
    except Exception as e:
        print(e)
        return ""


def get_email_template(request_data):
    json_data_string = fetch_data(
        "https://storage.googleapis.com/dealstream-poc/prompt-config.json")
    email_message_prompt = json_data_string.get("EMAIL_MESSAGE_PROMPT", "")
    email_message_prompt_model = json_data_string.get(
        "EMAIL_MESSAGE_PROMPT_MODEL", "")
    email_message_system_prompt = json_data_string.get("EMAIL_MESSAGE_SYSTEM_PROMPT", "")
    email_message_prompt = email_message_prompt.format(
        contact_name=request_data['contact_name'],
        problem_points=request_data['problem_points'],
        suggested_solutions=request_data['suggested_solutions']
    )
    messages = [
        {"role": "system", "content": email_message_system_prompt},
        {"role": "user", "content": email_message_prompt}
    ]
    return create_chat_response(messages, model_name=email_message_prompt_model)


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


@app.route("/api/prompt", methods=["POST"])
@require_api_key
@log_request_response
def get_prompt_response():
    request_data = request.get_json()
    messages = request_data['messages']
    sales_notes = get_sales_notes(request_data["opportunity_id"])
    messages[1]["content"] = messages[1]["content"].format(opportunity_notes=sales_notes)
    model_name = request_data.get("model_name", 'gpt-3.5-turbo-1106').strip()
    if not model_name.strip():
        model_name = 'gpt-3.5-turbo-1106'
    result = create_chat_response(messages, model_name=model_name)
    return result


@app.route("/api/opportunity-list", methods=["GET"])
@require_api_key
@log_request_response
def get_query_response():
    opportunities = get_all_opportunities()
    try:
        if opportunities:
            return opportunities
    except Exception as e:
        print(e)
        return ""


@app.route("/api/get-email-template", methods=["POST"])
@require_api_key
@log_request_response
def get_email_message():
    request_data = request.get_json()
    return get_email_template(request_data)


@app.route('/update-config-file')
def index():
    return render_template('file_upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    file.save(os.path.join(file.filename))
    return 'File uploaded successfully'

def get_last_n_entries(file_path, n):
    try:
        tail_command = ['tail', '-n', str(n), file_path]
        log_data = subprocess.check_output(tail_command, universal_newlines=True)
        return log_data

    except Exception as e:
        logger.error(f"Error fetching log: {str(e)}")
        raise

@app.route('/api/viewlog', methods=['GET'])
def view_log():
    try:
        log_data = get_last_n_entries('application.log', n=100)
        return Response(log_data, mimetype='text/plain')
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch log data'}), 500

if __name__ == "__main__":
    app.run()
