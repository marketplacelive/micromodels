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

if __name__ == "__main__":
    app.run()



