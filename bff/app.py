from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from functools import wraps
import openai
import os
from run_prompt import get_all_opportunities
import secrets

load_dotenv()

openai.api_key = os.getenv("API_KEY")
#print(openai.api_key)
openai.organization = os.getenv("org_id")

API_SECRET = os.getenv('API_SECRET')
secret_key = secrets.token_urlsafe(32)

max_tokens = 500

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

CORS(app)

#print("hello1")
def require_api_key(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        #print("hello4")
        api_key = request.headers.get('X-API-Key')
        if api_key != API_SECRET:
            return jsonify({'error': 'Invalid API Key'}), 401
        return func(*args, **kwargs)
    return decorated
#print("hello2")

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/api/prompt", methods=["POST"])
@require_api_key
def get_prompt_response():
    #print("hello3")
    request_data = request.get_json()
    messages = request.json['messages']
    if "model_name" in request_data:
        model_name = request_data["model_name"]
        if not model_name.strip():
            model_name = 'ft:gpt-3.5-turbo-0613:dealstreamai::83J9KIF6'
    else:
        model_name = 'ft:gpt-3.5-turbo-0613:dealstreamai::83J9KIF6'   
    #print(messages)
    try:
        response = openai.ChatCompletion.create(
            messages=messages,
            model=model_name,
            max_tokens=500,
            temperature=0,
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})
    except Exception as e:
        print(e)
        return ""

@app.route("/api/opportunity-list", methods=["POST"])
@require_api_key
def get_query_response():
    opportunities = get_all_opportunities("dealstream")
    try:
        if opportunities:
            return opportunities
    except Exception as e:
        print(e)
        return ""
    

if __name__ == "__main__":
    app.run()



