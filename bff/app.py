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
    messages = request.json['messages']
    if "model_name" in request_data:
        model_name = request_data["model_name"]
        if not model_name.strip():
            model_name = 'gpt-3.5-turbo-1106'
    else:
        model_name = 'gpt-3.5-turbo-1106'

    try:
        sample_template = """1. Problem Point: Stalled Opportunity\nProblem Point: No response from Stakeholders\nSuggested solutions: Identify Key Stakeholders\n\nDear xxx\n\nI am writing to introduce myself, My name is Bob ward and I am working with your colleague John Baker on a project that I understand that you may be involved with.\n\nI understand that you may have a similar requirement to John in terms of your Sales Development project. John is tied up with another project right now so I thought that I would take the opportunity to reach out to you. I would be happy to take you through exactly what we are doing for John and his team on a call if possible.\n\nIf you have the time please can you provide me with a suitable date and time next week for a call to discuss?\n\nVery best regards\nBob Ward\n\n2. Problem Point: Stalled Opportunity.\nProblem Point: No response from Stakeholders\nProblem Point: No Compelling Events\nSuggested solutions: Identify Key stakeholders\n\nDear xxx\n\nI am writing to introduce myself, My name is Bob ward and I am working with your colleague John Baker on a project that I understand that you may be involved with.\n\nIf possible and if you have the time I would appreciate the opportunity to have a call with you to cover off a number of points that are currently outstanding which would really help us\n\nDefine a clear way forward on the project. I thin Joh is quite busy on other projects right now and there fore would like to discuss the problem points in more detail with you that are driving you to assess a solution like Dealstream – mainly to understand the compelling elements that are driving this project.\n\nYour help on this would be very much appreciated\n\nVery best regards\nBob Ward\n\n3. Problem Point: Need Price Estimates\nProblem Point: Legal document conflicts\nProblem Point: Timeline Mismatch\nSuggested Solutions: Identify Key Stakeholders\n\nDear xxx\n\nI have been working with your colleague John Brown who has asked me to put some pricing estimates together. I am happy to do so however I think that a quick call with you to define a tighter\n\nUnderstanding of your requirements would help me finalise this and allow me to send out a draft proposal. In addition having spoken with your legal team it seems that there are some issues with the legal documentation that we have sent across, therefore a quick conversation with you on this may be also useful. If you could also provide me with your estimated timelines for go live for the project too as there seems to be some mixed messages from different stakeholders. Hopefully nothing that we can’t resolve on a quick call.\n\nPlease do let me know when you would be available this week.\n\nVery best regards\nBob Ward\nThe information given consists of email samples addressing specific problem points and providing suggested solutions. Whenever you are presented a new problem point along with its suggested solution, generate email templates in similar format.\n"""
        messages[1]["content"] = sample_template + messages[1]["content"]
        response = client.chat.completions.create(
            messages=messages,
            model='gpt-3.5-turbo-1106',
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



