from dotenv import load_dotenv
from flask import Flask, request, jsonify
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

def require_api_key(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_SECRET:
            return jsonify({'error': 'Invalid API Key'}), 401
        return func(*args, **kwargs)
    return decorated

def get_config_file(url):
    # Make an HTTP GET request to the URL
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON content
        return response.json()
    else:
        # Print an error message if the request was not successful
        return f"Failed to fetch data. Status code: {response.status_code}"
        
@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/prompt", methods=["POST"])
@require_api_key
def get_prompt_response():
    request_data = request.get_json()
    #print(request_data);
    messages = request_data['messages']
    if "model_name" in request_data:
        model_name = request_data["model_name"]
        if not model_name.strip():
            model_name = 'gpt-3.5-turbo-1106'
    else:
        model_name = 'gpt-3.5-turbo-1106'  

    try:
        #json_request_prompt = "Provide the response in the format of a array, but refrain from using the term json in your answer."
        #opportunity_id = "006Hs00001DHMV9IAP";
        sales_notes = get_sales_notes(request_data["opportunity_id"])
        messages[1]["content"] = messages[1]["content"].format(opportunity_notes=sales_notes)
        #print(messages);
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            max_tokens=500,
            temperature=0,
        )

        # Extract the AI response from the response object
        response = response.choices[0].message.content
        return jsonify({"answer": response})
    except Exception as e:
        print(e)
        return ""

@app.route("/api/opportunity-list", methods=["GET"])
@require_api_key
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
def get_email_message():
    request_data = request.get_json()
    #messages = request_data['messages']
   
    problem_points = ",".join(request_data['problem_points'])
    suggested_solutions = request_data['suggested_solutions']
    contact_name = request_data['contact_name']
    if "model_name" in request_data:
        model_name = request_data["model_name"]
        if not model_name.strip():
            model_name = 'gpt-3.5-turbo-1106'
    else:
        model_name = 'gpt-3.5-turbo-1106'

    try:
        sample_template = """Problem Point(s): List the specific issue(s) or challenge(s) that need to be addressed. 
   - Example: Delayed project timelines, budget overruns, lack of stakeholder engagement.
Suggested Solution(s): Provide the actionable suggestion(s) or solution(s) for the problem point(s) listed above.
   - Example: Schedule a project review meeting, re-evaluate resource allocation, enhance stakeholder communication strategy.

Below are 3 sets of sample email generated based on a set of problem points and their suggested solutions.

Sample 1:

Problem Point: Stalled Opportunity
Problem Point: No response from Stakeholders
Suggested solutions: Identify Key Stakeholders
 
Email message:
I am writing to introduce myself, My name is Bob ward and I am working with your colleague John Baker on a project that I understand that you may be involved with.

I understand that you may have a similar requirement to John in terms of your Sales Development project. John is tied up with another project right now so I thought that I would take the opportunity to reach out to you. I would be happy to take you through exactly what we are doing for John and his team on a call if possible.

If you have the time please can you provide me with a suitable date and time next week for a call to discuss?


Sample 2:

Problem Point: Stalled Opportunity.  
Problem Point: No response from Stakeholders
Problem Point: No Compelling Events
Suggested solutions: Identify Key stakeholders

Email message:

I am writing to introduce myself, My name is Bob ward and I am working with your colleague John Baker on a project that I understand that you may be involved with.

If possible and if you have the time I would appreciate the opportunity to have a call with you to cover off a number of points that are currently outstanding which would really help us

Define a clear way forward on the project. I thin Joh is quite busy on other projects right now and there fore would like to discuss the problem points in more detail with you that are driving you to assess a solution like Dealstream – mainly to understand the compelling elements that are driving this project.

Your help on this would be very much appreciated

Sample 3:
 
Problem Point: Need Price Estimates
Problem Point: Legal document conflicts
Problem Point: Timeline Mismatch
Suggested Solutions: Identify Key Stakeholders

Email message :
 
I have been working with your colleague John Brown who has asked me to put some pricing estimates together. I am happy to do so however I think that a quick call with you to define a tighter

Understanding of your requirements would help me finalise this and allow me to send out a draft proposal. In addition having spoken with your legal team it seems that there are some issues with the legal documentation that we have sent across, therefore a quick conversation with you on this may be also useful. If you could also provide me with your estimated timelines for go live for the project too as there seems to be some mixed messages from different stakeholders. Hopefully nothing that we can’t resolve on a quick call.

Please do let me know when you would be available this week.

Sample details end here.

Instructions to AI: Based on the 3 samples provided, compose a professional email tailored to the recipient addressing the problem points outlined below. Incorporate the suggested solutions in a manner that encourages collaboration and prompt action. Conclude with a polite request for a meeting within the preferred timeframe. 
Use only the below problem points and suggested solutions for crafting new email. Email message should only contain maximum of 10 sentences. Remove Subject line from the message.
Your Name : Bob Ward
Recipient's Name : {contact_name}
Problem point(s) : {problem_points}
Suggested solution(s): {suggested_solutions}
"""
        #config_file_path = "../prompt-config.json"
        #json_data_string = open(config_file_path, "r").read()
        json_data_string = get_config_file("https://storage.googleapis.com/dealstream-poc/prompt-config.json")
        #print(json_data_string["MODEL_NAME"])
        #print(json_data_string["EMAIL_MESSAGE_PROMPT"])
        # Load the JSON data
        email_message_prompt = json_data_string["EMAIL_MESSAGE_PROMPT"]
        email_message_prompt_model = json_data_string["EMAIL_MESSAGE_PROMPT_MODEL"]
        email_message_prompt = email_message_prompt.format(contact_name=contact_name, problem_points=problem_points, suggested_solutions=suggested_solutions)
                
        #messages[1]={"role":"user","content": sample_template}
        messages=[{"role": "system", "content": "You're an AI sales assistant aiding sales agents in crafting concise email templates derived from problem points and suggested solutions, all within a brief word limit."},{"role":"user","content": email_message_prompt}]
        #print(email_message_prompt_model)
        response = client.chat.completions.create(
            messages=messages,
            model=email_message_prompt_model,
            max_tokens=500,
            temperature=0,
        )

        # Extract the AI response from the response object
        response = response.choices[0].message.content
        return jsonify({"answer": response})
    except Exception as e:
        print(e)
        return ""


if __name__ == "__main__":
    app.run()



