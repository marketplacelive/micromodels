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
import sqlite3

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
            elif isinstance(response, str):
                logger.info(
                f"Response Data: {response}\n")
            else:
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

def get_json_data(filename):
    try:
        with open(filename, 'r') as file:
            jsondata = json.load(file)
            return jsondata
    except Exception as e:
        raise FileNotFoundError(f"JSON file '{filename}' not found.")
    except ValueError:
        raise ValueError(f"Invalid JSON data in file '{filename}'.")


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
    json_data_string = get_json_data("prompt-config.json")
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

@app.route("/api/get-meeting-description")
@require_api_key
@log_request_response
def get_meeting_description():
    request_data = request.args
    meeting_type = request_data['meeting_type']
    json_data_string = get_json_data("prompt-config.json")
    system_prompt = json_data_string.get("SYSTEM_PROMPT", "")
    meeting_description_prompt = json_data_string.get("MEETING_DESCRIPTION_PROMPT", "")
    meeting_description_prompt = meeting_description_prompt.format(meeting_type=meeting_type)
    model_name = json_data_string.get("MEETING_DESCRIPTION_PROMPT_MODEL", "")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": meeting_description_prompt}
    ]
    result = create_chat_response(messages, model_name=model_name)
    return result

@app.route("/api/get-meeting-objectives")
@require_api_key
@log_request_response
def get_meeting_objective():
    request_data = request.args
    opportunity_id = request_data['opportunity_id']
    sales_notes = get_sales_notes(opportunity_id)
    json_data_string = get_json_data("prompt-config.json")
    system_prompt = json_data_string.get("MEETING_OBJECTIVE_SYSTEM_PROMPT", "")
    meeting_objective_prompt = json_data_string.get("MEETING_OBJECTIVE_PROMPT", "")
    meeting_objective_prompt = meeting_objective_prompt.format(sales_notes=sales_notes)
    model_name = json_data_string.get("MEETING_OBJECTIVE_PROMPT_MODEL", "")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": meeting_objective_prompt}
    ]
    result = create_chat_response(messages, model_name=model_name)
    result_string = result.get_data()
    result_json = json.loads(result_string)
    meeting_type = result_json.get("answer")
    
    meeting_objective = {"Qualification Meeting": ["Identify stakeholders","Define budget availability","Identify Timelines","Identify the why?","Identify Compwetition","Clarify procurement process","Understand current Tech stack","Identify Economic Buyer"], "Discovery Meeting": ["Identify the pain points","Validate stakeholders","Validate procurement process","Identify key must have functioanlity","Set a date for a Tech stack call","Identify Champion","Set date for demonstration meeting","Discuss NDA requirement"], "Demonstration Meeting":["Cover the Dealstream Value","Deliver tailored demonstration","Gauge audience feedback","Discuss customer use cases","Discuss Value Engineering","Offer a Value engineering session","Discuss proposal delivery"], "Tech Stack Validation Meeting":["Understand the Tech environment","Discuss integration requirements","Discuss Data Provacy requirements","Identify where main data is held","Request access to business process"], "Internal Solution Review Meeting":["Deliver Tech Stack Overview","Deliver solution Overview","Discuss all integration requirements","Discuss all Language requirements","Discuss all geographical deployment","Secure commitment from PM for support"],"General Update meeting":["Project update details","Discuss any changes to plan","Discuss outstanding actions","Discuss any RFP / RFI requirements"],"Stakeholder Meeting":["Introduce key personel","present proposal for delivery","Discuss procing if requested","Present proposal and POV","Understand the paper process"],"Implementation Meeting":["Discuss  all integration reqiorements","Discuss numbers and types of users","Offer to build a draft SOW"],"Value Engineering Meeting":["Undersdtand current outcomes being achieved","Discuss number of users","Discuss sales numbers","Discuss ramp time for sales","Discuss % of top performers","Discuss revenue from top performers","Discuss second tier performer revenues"],"Contract Meeting":["Discuss all contract details","Ascertain whos contract we are using","Identify main legal contact","Set up cadence calls with legal"],"Infosec Data Provacy Meeting":["Send DPA to client","Identify main InfoSec contact","Discuss all aspects of DP","Understand the customers DP requirements"],"MAP Meeting":["Send MAP template to client","Discuss the steps in the process","Agree that the steps are correct","Agree Timelines are correct","Gain customer commitment to modify"],"Executive Alignment Meeting":["Meet key stakeholders on customer side","Meet Key stakeholders on Vendor side","Discuss executive support where needed"]}

    if meeting_type in meeting_objective:
        objectives = meeting_objective[meeting_type]
    else:
        objectives = []
    response = {"meeting_type": meeting_type, "meeting_objectives": objectives}

    return jsonify(response)

@app.route("/action-list")
@require_api_key
@log_request_response
def get_action_list():
    try:
        conn = sqlite3.connect("action_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action.action_name, action_list.account_name, action_list.category, action_list.priority, action_list.due_before
            FROM action
            INNER JOIN action_list ON action.id = action_list.action_id
        """)
        actions = cursor.fetchall()
        json_data = [
            {"action_name": action[0], "account_name": action[1], "category": action[2], "priority": action[3], "due_before": action[4]}
            for action in actions
        ]
        return jsonify(json_data)
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: {}".format(e)}), 500
    finally:
        if conn:
            conn.close()

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

@app.route('/config')
def view_config():
    config_data = get_json_data("prompt-config.json")
    return render_template('prompt_config.html', config_data=config_data)

@app.route('/update-config', methods=['POST'])
def update_config():
    request_data = request.get_json()
    # Create the JSON file
    try:
        with open('prompt-config.json', 'w') as f:
            json.dump(request_data, f)
    except Exception as e:
        return jsonify({'status': 'error', 'error': 'Failed to create local configuration file'}), 500  

    return jsonify({'status': 'success', 'message': 'Configuration updated'})

@app.route("/api/get-config")
def get_config_data():
    try:
        with open("prompt-config.json", 'r') as file:
            jsondata = json.load(file)
            return jsondata
    except Exception as e:
        raise FileNotFoundError(f"JSON file '{filename}' not found.")
    except ValueError:
        raise ValueError(f"Invalid JSON data in file '{filename}'.")

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
