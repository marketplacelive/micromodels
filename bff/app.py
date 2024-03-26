from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify, render_template, copy_current_request_context
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
import re
from flask_swagger_ui import get_swaggerui_blueprint
import yaml
import time
import itertools
from flask import session
import threading

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

db_name = "action_data_test.db"

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

SWAGGER_URL = '/swagger'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Dealstream"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
            elif isinstance(response, tuple):
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

def remove_surrounding_quotes(s):
    # Check if the string starts with \" and ends with \", then remove them
    if s.startswith("\"") or s.endswith("\""):
        return s[1:-1].replace('\\"', '"')
    return s

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
        response = remove_surrounding_quotes(response)
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

def connect_db():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

def get_suggested_solution(request_data):
    problem_points = request_data.get("problem_points")
    suggestion_consolidate_response = ""
    sales_notes = get_sales_notes(request_data["opportunity_id"])
    account_name = request_data["account_name"]
    json_data_string = get_json_data("prompt-config.json")
    system_prompt = json_data_string.get("SYSTEM_PROMPT", "")
    for problem_point in problem_points:
        print(problem_point)
        if session.get(problem_point) is None:
            print ("call chat")
            suggested_solution_prompt = json_data_string.get("LIST_SUGGESTED_SOLUTION_PROMPT", "").format(opportunity_notes=sales_notes, account_name=account_name,problem_point_checkList=problem_point)
            model_name = request_data.get("model_name", 'gpt-3.5-turbo-1106').strip()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": suggested_solution_prompt}
            ]
            result = create_chat_response(messages, model_name=model_name)
            response_json = result.get_json()
            response_text = response_json['answer']
            suggestion_prompt = json_data_string.get("FUTURE_TENSE_PROMPT", "").format(sentences=response_text)
            suggestion_response = create_chat_response(messages=[{"role": "user", "content": suggestion_prompt}], model_name='gpt-3.5-turbo-1106')
            
            result_string = suggestion_response.get_data()
            result_json = json.loads(result_string)
            result_value = result_json.get("answer")

            suggestion_consolidate_response =  suggestion_consolidate_response + result_value

        else:
            suggestion_consolidate_response = suggestion_consolidate_response + "." +  session.get(problem_point)  
    
    return jsonify({"answer":suggestion_consolidate_response})

@app.route("/api/prompt", methods=["POST"])
@require_api_key
@log_request_response
def get_prompt_response():
    api_start_time = time.time()
    request_data = request.get_json()
    messages = request_data['messages']
    prompt_type = request_data.get("type","")
    if(prompt_type=="suggested_solution"):
        suggestion_solution = get_suggested_solution(request_data)
        return suggestion_solution
    else:    
        sales_notes = get_sales_notes(request_data["opportunity_id"])
        messages[1]["content"] = messages[1]["content"].format(opportunity_notes=sales_notes)
        model_name = request_data.get("model_name", 'gpt-3.5-turbo-1106').strip()
        if not model_name.strip():
            model_name = 'gpt-3.5-turbo-1106'
        openai_start_time = time.time()
        result = create_chat_response(messages, model_name=model_name)
        openai_endtime = time.time()
        FUTURE_TENSE_PROMPT_ENABLE = 1
        if (prompt_type=="suggested_solution" or prompt_type=="suggested_action") and FUTURE_TENSE_PROMPT_ENABLE:
            response_json = result.get_json() 
            response_text = response_json['answer'] 
            json_data_string = get_json_data("prompt-config.json")
            suggestion_prompt = json_data_string.get("FUTURE_TENSE_PROMPT", "").format(sentences=response_text)
            suggestion_response = create_chat_response(messages=[{"role": "user", "content": suggestion_prompt}], model_name='gpt-3.5-turbo-1106')
            end_time = time.time()  
            first_openai_time = openai_endtime - openai_start_time
            total_openai_time = end_time - openai_start_time
            total_time = end_time - api_start_time
            print(f"first openai call time: {first_openai_time} seconds")
            print(f"total openai time: {total_openai_time} seconds")
            print(f"Total API time: {total_time} seconds")
            return suggestion_response
        else:
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

@app.route("/api/get-action-list-email-message", methods=["GET"])
@require_api_key
@log_request_response
def get_action_list_email_message():
    request_data = request.args 
    #email_sales_note=request_data['email_sales_note']
    email_sales_note_id=request_data['id']
    json_data_string = get_json_data("prompt-config.json")
    if email_sales_note_id == "1":
        email_sales_note = "Received and email from Colin Gow regarding ball park pricing that needs to be responded to"
    elif email_sales_note_id == "2":
        email_sales_note = "Received an email from Steph Cole concering API integrations which needs to be responded to"
    else:
        email_sales_note = "Received an email from John Baker today cooncerning Data Privacy that I need to respond to"
              
    action_list_email_message_system_prompt= json_data_string.get("ACTION_LIST_EMAIL_MESSAGE_SYSTEM_PROMPT", "")
    action_list_email_message_prompt = json_data_string.get("ACTION_LIST_EMAIL_MESSAGE_PROMPT", "")
    action_list_email_message_prompt = action_list_email_message_prompt.format(email_sales_note=email_sales_note)
    model_name = json_data_string.get("ACTION_LIST_EMAIL_MESSAGE_PROMPT_MODEL", "")
    messages = [
        {"role": "system", "content": action_list_email_message_system_prompt},
        {"role": "user", "content": action_list_email_message_prompt}
    ]
    result = create_chat_response(messages, model_name=model_name)
    result_string = result.get_data()
    result_json = json.loads(result_string)
    result_value = result_json.get("answer")
    pattern = r"Subject: (.*?)\n"
    match = re.search(pattern, str(result_value), re.DOTALL)
    subject = match.group(1)
    email_text = re.sub(pattern, '', str(result_value))
    return jsonify({"subject":subject, "message":email_text}) 

@app.route("/api/get-stakeholder-email-message", methods=["GET"])
@require_api_key
@log_request_response
def get_stakeholder_email_message():
    request_data = request.args 
    #email_sales_note=request_data['email_sales_note']
    sales_notes = get_sales_notes(request_data["opportunity_id"])
    contact_name = request_data["contact_name"]
    json_data_string = get_json_data("prompt-config.json")
    stakeholder_email_message_system_prompt= json_data_string.get("STAKEHOLDER_EMAIL_MESSAGE_SYSTEM_PROMPT", "")
    stakeholder_email_message_prompt = json_data_string.get("STAKEHOLDER_EMAIL_MESSAGE_PROMPT", "")
    stakeholder_email_message_prompt = stakeholder_email_message_prompt.format(sales_notes=sales_notes, contact_name=contact_name)
    model_name = json_data_string.get("STAKEHOLDER_EMAIL_MESSAGE_PROMPT_MODEL", "")
    messages = [
        {"role": "system", "content": stakeholder_email_message_system_prompt},
        {"role": "user", "content": stakeholder_email_message_prompt}
    ]
    result = create_chat_response(messages, model_name=model_name)
    result_string = result.get_data()
    result_json = json.loads(result_string)
    result_value = result_json.get("answer")
    pattern = r"Subject: (.*?)\n"
    match = re.search(pattern, str(result_value), re.DOTALL)
    subject = match.group(1)
    email_text = re.sub(pattern, '', str(result_value))
    return jsonify({"subject":subject, "message":email_text}) 

    
@app.route("/api/get-meeting-objectives")
@require_api_key
@log_request_response
def get_meeting_objective():
    request_data = request.args
    opportunity_id = request_data['opportunity_id']
    meeting_type = request_data.get("meeting_type","")
    problem_points = request_data.get('problem_points', "")
    sales_notes = get_sales_notes(opportunity_id)
    json_data_string = get_json_data("prompt-config.json")
    system_prompt = json_data_string.get("MEETING_OBJECTIVE_SYSTEM_PROMPT", "")
    model_name = json_data_string.get("MEETING_OBJECTIVE_PROMPT_MODEL", "")
    meeting_objective = {"Qualification Meeting": ["Identify stakeholders","Define budget availability","Identify Timelines","Identify the why?","Identify Compwetition","Clarify procurement process","Understand current Tech stack","Identify Economic Buyer"], "Discovery Meeting": ["Identify the pain points","Validate stakeholders","Validate procurement process","Identify key must have functioanlity","Set a date for a Tech stack call","Identify Champion","Set date for demonstration meeting","Discuss NDA requirement"], "Demonstration Meeting":["Cover the Dealstream Value","Deliver tailored demonstration","Gauge audience feedback","Discuss customer use cases","Discuss Value Engineering","Offer a Value engineering session","Discuss proposal delivery"], "Tech Stack Validation Meeting":["Understand the Tech environment","Discuss integration requirements","Discuss Data Provacy requirements","Identify where main data is held","Request access to business process"], "Tech Stack meeting":["Understand the Tech environment","Discuss integration requirements","Discuss Data Provacy requirements","Identify where main data is held","Request access to business process"], "Internal Solution Review Meeting":["Deliver Tech Stack Overview","Deliver solution Overview","Discuss all integration requirements","Discuss all Language requirements","Discuss all geographical deployment","Secure commitment from PM for support"],"General Update meeting":["Project update details","Discuss any changes to plan","Discuss outstanding actions","Discuss any RFP / RFI requirements"],"Stakeholder Meeting":["Introduce key personel","present proposal for delivery","Discuss procing if requested","Present proposal and POV","Understand the paper process"],"Implementation Meeting":["Discuss  all integration reqiorements","Discuss numbers and types of users","Offer to build a draft SOW"],"Value Engineering Meeting":["Undersdtand current outcomes being achieved","Discuss number of users","Discuss sales numbers","Discuss ramp time for sales","Discuss % of top performers","Discuss revenue from top performers","Discuss second tier performer revenues"],"Contract Meeting":["Discuss all contract details","Ascertain whos contract we are using","Identify main legal contact","Set up cadence calls with legal"],"Infosec Data Provacy Meeting":["Send DPA to client","Identify main InfoSec contact","Discuss all aspects of DP","Understand the customers DP requirements"],"MAP Meeting":["Send MAP template to client","Discuss the steps in the process","Agree that the steps are correct","Agree Timelines are correct","Gain customer commitment to modify"],"Executive Alignment Meeting":["Meet key stakeholders on customer side","Meet Key stakeholders on Vendor side","Discuss executive support where needed"]}
    
    if not meeting_type:
        meeting_objective_prompt = json_data_string.get("MEETING_OBJECTIVE_PROMPT", "")
        meeting_objective_prompt = meeting_objective_prompt.format(sales_notes=sales_notes, problem_points=problem_points)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": meeting_objective_prompt}
        ]
        result = create_chat_response(messages, model_name=model_name)
        result_string = result.get_data()
        result_json = json.loads(result_string)
        meeting_type = result_json.get("answer")
 
    if meeting_type in meeting_objective:
        objectives = meeting_objective[meeting_type]
    else:
        objectives = []
        return jsonify({"meeting_type": meeting_type, "meeting_objectives": objectives})
    meeting_objective_prompt = json_data_string.get("ACTION_LIST_MEETING_OBJECTIVE_PROMPT", "")
    meeting_objective_prompt = meeting_objective_prompt.format(sales_notes=sales_notes, meeting_objectives=objectives, meeting_type=meeting_type)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": meeting_objective_prompt}
    ]
    result = create_chat_response(messages, model_name=model_name)
    objectives = result.get_data()
    objectives = json.loads(objectives)['answer']
    response = {"meeting_type": meeting_type, "meeting_objectives": eval(objectives)}
    return jsonify(response)

@app.route("/action-list")
@require_api_key
@log_request_response
def get_action_list():
    try:
        request_data = request.args 
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 0)
        limit = int (limit)
        offset = int (offset)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action_list.action_list_id, action_list.action_id, action_list.action_name, action_list.priority, action_list.category, action_list.category_id,
                    action_list.account_name, action_list.opportunity_id, action_list.due_before FROM action_list LIMIT ? OFFSET ?""", (limit, offset))
        actions = cursor.fetchall()
        json_data = [
            {
                "action_list_id": action[0],
                "action_id": action[1],
                "action_name": action[2], 
                "priority": action[3],  
                "category": action[4],
                "category_id": action[5],
                "account_name": action[6],
                "opportunity_id": action[7],
                "due_before":action[8]
            }
            for action in actions
        ]
        return jsonify(json_data)
    except sqlite3.Error as e:
        return jsonify({"error": "Database error: {}".format(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/action-list", methods=["DELETE"])
@require_api_key
@log_request_response
def delete_action():
    action_list_id = request.args.get("action_list_id")
    if not action_list_id:
        return jsonify({'error': 'action_list_id is required'}), 400
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM action_list WHERE action_list_id = ?", (action_list_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Action list item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 200
        
@app.route('/api/suggested-action-add-to-action-list', methods=['POST'])
@require_api_key
@log_request_response
def save_actions():
    try:
        data = request.get_json()
        action_name = data.get('action_name')
        account_name = data.get('opportunity_name')
        opportunity_id = data.get('opportunity_id')
        category = data.get('category', "Suggested action")
        category_id = data.get('category_id', 12)
    except (KeyError, TypeError) as e:
        return jsonify({"error": "Missing required fields in JSON body"}), 400
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM action WHERE action_name = ?",
                    (action_name,))
        existing_action = cur.fetchone()

        if existing_action:
            action_id = existing_action[0]
            cur.execute(
                "SELECT * FROM action_list WHERE action_id = ? AND account_name = ?", (action_id, account_name))
            existing_entry = cur.fetchone()
            if existing_entry:
                print(
                    f"Action '{action_name}' already exists for account '{account_name}'")
                conn.close()
                return jsonify({'message': 'Action already exists for this account'}), 200

        else:
            try:
                cur.execute(
                    "SELECT thread_id FROM thread WHERE opportunity_id = 'global';")
                thread_id = cur.fetchone()
                if not thread_id:
                    return "None"
                thread_id = thread_id[0]
                action = {}
                action['action'] = action_name
                action['account'] = account_name
                action['priority'] = "Low"
                action['due_before'] = "Not Specified"
                json_data_string = get_json_data("prompt-config.json")
                action_list_add_new_across_opportunity_prompt = json_data_string.get(
                    'ACTION_LIST_ADD_NEW_ACROSS_OPPORTUNITY_PROMPT')
                cur.execute("DELETE FROM action;")
                conn.commit()
                cur.execute("DELETE FROM action_list;")
                conn.commit()
                message = client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=action_list_add_new_across_opportunity_prompt.format(
                        action=str(action))
                )
                run = client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id="asst_7KKat0PEcHBgvQkwWauq2PQx"
                )
                while True:
                    time.sleep(2)
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    if run_status.status == 'completed':
                        messages = client.beta.threads.messages.list(
                            thread_id=thread_id
                        )
                        for msg in messages.data:
                            role = msg.role
                            response = msg.content[0].text.value
                            if role.lower() == "assistant":
                                response = eval(response)
                                break
                        break
                if not response:
                    return jsonify({'message': "None"})
                elif isinstance(response[0], str):
                    if response[0] == "None":
                        return jsonify({'message': "None"})
                    else:
                        print("Yes i was here")
                        response = eval(response[0])
                elif isinstance(response[0], list):
                    if len(response) > 1:
                        response = list(itertools.chain.from_iterable(response))
                    else:
                        response = response[0]
                for action in response:
                    cur.execute("""INSERT INTO action (action_name, priority) VALUES (?, ?)""",
                                   (action['action'], action['priority']))
                    conn.commit()
                    action_id = cur.lastrowid
                    cur.execute("""INSERT INTO action_list (action_id, account_name, due_before, order_across_opportunity) VALUES (?, ?, ?, ?)""",
                                   (action_id, action['account'], action['due_before'], action['order_across_opportunity']))
                    conn.commit()
                return jsonify({'message': response})

            except sqlite3.Error as e:
                conn.rollback()
                return jsonify({'Error inserting action': e}), 200
    except Exception as e:
        return jsonify({'error': e})
    finally:
        conn.close()
    return jsonify({'message': 'Something went wrong! May be account name incorrect'}), 201

#Chat assistant for action list
@app.route('/api/assistant', methods=['POST'])
@require_api_key
def assistant(): 
    try:
        data = request.get_json()
        user_prompt = data.get('question')
        page_name = data.get('page_name',"")
        opportunity_id = data.get('opportunity_id',"")
        user_thread_id = data.get('thread_id', "")
        #thread_id="thread_AKocGCwNa3MqYeh5oGyTccPo"
        global_action_list_assistant = "asst_RbZ26FH1lz0vfuI6tPPUMBvp"
        if user_thread_id == '':
            if page_name == "action_list" or page_name == "accelerate":
                conn = connect_db()
                cursor = conn.cursor()
                thread_id = cursor.execute(
                "SELECT thread_id FROM thread WHERE opportunity_id = 'global'").fetchone()
                if thread_id:
                    user_thread_id = thread_id[0]
                else:
                    thread = client.beta.threads.create()
                    user_thread_id = thread.id
            elif page_name == "problem_points":
                conn = connect_db()
                cursor = conn.cursor()
                thread_id = cursor.execute(
                "SELECT thread_id FROM thread WHERE opportunity_id = "+opportunity_id).fetchone()
                if thread_id:
                    user_thread_id = thread_id[0]
                else:
                    thread = client.beta.threads.create()
                    user_thread_id = thread.id

        message = client.beta.threads.messages.create(
            thread_id=user_thread_id,
            role="user",
            content=user_prompt
        )
        
        run = client.beta.threads.runs.create(
            thread_id=user_thread_id,
            assistant_id=global_action_list_assistant
        )
        #print("thread_id"+user_thread_id)
        while True:
            time.sleep(2)
            run_status = client.beta.threads.runs.retrieve(
                thread_id=user_thread_id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=user_thread_id
                )
                for msg in messages.data:
                    role = msg.role
                    if role.lower() == 'assistant':
                        content = msg.content[0].text.value
                        break
                return jsonify({'message': content,"thread_id":user_thread_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)})


def get_action_items(opportunity_id, opportunity):
    json_data_string = get_json_data("prompt-config.json")
    # model_name = json_data_string.get(
    #     'ACTION_LIST_PROMPT_MODEL', "")
    action_list_prompt = json_data_string.get(
        'ACTION_LIST_PROMPT')
    action_list_order_inside_opportunity_prompt = json_data_string.get(
            'ACTION_LIST_ORDER_INSIDE_OPPORTUNITY_PROMPT')    
    print("opportunity_id")    
    print(opportunity_id)
    sales_notes = get_sales_notes(opportunity_id)
    print("sales_notes")
    print(sales_notes)
    opportunity_assistant = "asst_7oAfmyIa2QBBF9LYNpfsCzID"
    action_list_prompt = action_list_prompt.format(sales_notes=sales_notes, opportunity=opportunity, opportunity_id=opportunity_id)
    conn = connect_db()
    cursor = conn.cursor()
    thread_id = cursor.execute(
                "SELECT thread_id FROM thread WHERE opportunity_id = ?", (opportunity_id,)).fetchone()
    if thread_id:
        thread_id = thread_id[0]
    else:
        thread = client.beta.threads.create()
        thread_id = thread.id
        cursor.execute(
            "INSERT INTO Thread (opportunity_id, thread_id) VALUES (?, ?)", (opportunity_id, thread_id))
        conn.commit()

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=action_list_prompt
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=opportunity_assistant
    )
    content = create_assistant_response(message, run)
    
    if content.lower() == 'none':
        return 'None'

    message = client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=action_list_order_inside_opportunity_prompt
                )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=opportunity_assistant
    )
    content = create_assistant_response(message, run)
    return content

def create_assistant_response(message, run):
    while True:
        time.sleep(2)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=message.thread_id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=message.thread_id
            )
            for msg in messages.data:
                role = msg.role
                content = msg.content[0].text.value
                if role.lower() == "assistant":
                    return content
                
def get_action_list_order_across_opportunity(action_list):
    json_data_string = get_json_data("prompt-config.json")
    global_action_list_assistant = "asst_RbZ26FH1lz0vfuI6tPPUMBvp"
    conn = connect_db()
    cursor = conn.cursor()
    thread_id = cursor.execute("SELECT thread_id FROM thread WHERE opportunity_id = 'global'").fetchone()
    if thread_id:
        thread_id = thread_id[0]
    else:
        thread = client.beta.threads.create()
        thread_id = thread.id
        cursor.execute("INSERT INTO Thread (opportunity_id, thread_id) VALUES ('global', ?)", (thread_id,))
        conn.commit()
    action_list_order_across_opportunity_prompt = json_data_string.get(
            'ACTION_LIST_ORDER_ACROSS_OPPORTUNITY_PROMPT')
    # model_name = json_data_string.get('ACTION_LIST_PROMPT_MODEL', "")
    action_list_order_across_opportunity_prompt = action_list_order_across_opportunity_prompt.format(
            action_list=action_list)
    message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=action_list_order_across_opportunity_prompt
        )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=global_action_list_assistant
    )
    response = create_assistant_response(message, run)
    print(response)
    #json_index = response.find("json")
    #json_part = response[json_index + 4:-3]
    response = eval(response)
    return response
                                
@app.route('/api/create-action-list')
@require_api_key
#def start_task():
    #@copy_current_request_context    
def assistants_function_call():
    action_list_assistant = "asst_oUKA4rjY215DBM61PdcjzVS6"
    try:
        # Step 2: Create a Thread
        conn = connect_db()
        cursor = conn.cursor()
        thread = client.beta.threads.create()
        # Step 3: Add a Message to a Thread

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content='''Can you give the action items needed for Vodafone:'006Hs00001DHMVAIA5', Walmart:'006Hs00001DHMXyIAP', Siemens:'006Hs00001DHMV9IAP' opportunities? Final response
                        should be a consolidated array from all tool functions. 
                        Example: [\{\{'action':'First action to be taken', 'action_id':'12', 'priority':'Very High', 'category':'Email', 'category_id': '2', 'account': 'opportunity name 1', 'opportunity_id':'006Hs00001IUDnyIAH', 'due_before': '5 June 2023', 'order':'2', 'order_across_opportunity':'3'\}\}, 
                        \{\{'action':'second action to be taken', 'action_id':'12', 'priority':'High', 'category':'Email', 'category_id': '2', 'account': 'opportunity name 2', 'opportunity_id':'006Hs00001IUDnyIAH', 'due_before': '5 June 2023', 'order':'2', 'order_across_opportunity':'4'\}\}]
                        ONLY JSON IS ALLOWED as an answer. No explanation or other text is allowed. Avoid prefix like 'json', quotes etc.'''
            )

        # Step 4: Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=action_list_assistant,
            instructions="Please address the user as sales agent"
        )

        print(run.model_dump_json(indent=4))

        while True:
            # Wait for 5 seconds
            time.sleep(3)

            # Retrieve the run status
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(run_status.model_dump_json(indent=4))

            # If run is completed, get messages
            if run_status.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                # Loop through messages and print content based on role
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    if role.lower() == "assistant":
                        response = get_action_list_order_across_opportunity(content)
                        print(response)
                        break
                break
            

            elif run_status.status == 'requires_action':
                print("Function Calling")
                required_actions = run_status.required_action.submit_tool_outputs.model_dump()
                print(required_actions)
                tool_outputs = []
                import json
                for action in required_actions["tool_calls"]:
                    func_name = action['function']['name']
                    arguments = json.loads(action['function']['arguments'])  
                    output = eval(func_name)(opportunity_id=arguments['opportunity_id'], opportunity=arguments['opportunity'])
                    print("Fetched "+arguments['opportunity']+" action list....sleep for 5 seconds")
                    time.sleep(5)
                    tool_outputs.append({
                        "tool_call_id": action['id'],
                        "output": output
                    })      
                print("tool_outputs")    
                print(tool_outputs)
                print("Submitting outputs back to the Assistant...")
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            else:
                print("Waiting for the Assistant to process...")
                time.sleep(5)
    

        #cursor.execute("DELETE FROM action;")
        #conn.commit()
        
        if not response:
            return jsonify({'message': "None"})
        elif isinstance(response[0], str):
            if response[0] == "None":
                return jsonify({'message': "None"})
            else:
                response = eval(response[0])
        elif isinstance(response[0], list):
            if len(response) > 1:
                response = list(itertools.chain.from_iterable(response))
            else:
                response = response[0]
        actions = cursor.execute("SELECT * FROM action;").fetchall()
        existing_actions = {action[0] for action in actions}
        cursor.execute("DELETE FROM action_list;")
        conn.commit()
        for action in response:
            action_name = action['action']
            if action_name not in existing_actions:
                cursor.execute("""INSERT INTO action (action_name, priority) VALUES (?, ?)""",
                        (action['action'], action['priority']))
                conn.commit()
                action_id = cursor.lastrowid
            else:
                for item in actions:
                    if item[1] == action_name:
                        action_id = item[0]
                        break
            cursor.execute("""INSERT INTO action_list (action_id, action_name, priority, category, category_id, account_name, opportunity_id, due_before, order_inside_opportunity, order_across_opportunity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (action['action_id'], action['action'], action['priority'], action['category'], action['category_id'], action['account'], action['opportunity_id'], action['due_before'], action['order'], action['order_across_opportunity']))
        return jsonify({'message': response})
    except Exception as e:
        return jsonify({'error': str(e)})
    #thread = threading.Thread(target=assistants_function_call)
    #thread.start()
    #return 'Started creating action list in the background, please wait for few minutes!!'

        
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

@app.route('/swagger.yaml')
def swagger():
    with open('swagger.yaml', 'r') as f:
        yaml_content = yaml.safe_load(f)
        return jsonify(yaml_content)
        
if __name__ == "__main__":
    app.run()
