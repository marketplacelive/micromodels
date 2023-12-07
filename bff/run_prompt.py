from openai import OpenAI
import json
import requests
from get_access_token import get_access_token
from flask import session
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
organization = os.getenv("org_id")

client = OpenAI(api_key=api_key, organization=organization)

# Function get sales notes between Dealstream and its opportunity
def get_all_opportunities(company):
    """Get sales notes from Dealstream API in a given location"""
    api_endpoint = "https://dealstream-dev-ed.develop.my.salesforce.com/services/data/v56.0/query/?q=SELECT Id, Name  FROM Opportunity"
    # Replace with your OAuth2.0 access token
    access_token = session.get('access_token')
    headers = {
        "Authorization": "Bearer " + str(access_token)
        }

    if access_token is None:
        access_token =  get_access_token()
        session["access_token"] = access_token

    headers["Authorization"] = "Bearer " + access_token
    response = requests.get(api_endpoint, headers=headers)
    response_data = response.json()
    
    if 'errorCode' in response_data:
        access_token =  get_access_token()
        session["access_token"] = access_token
        headers["Authorization"] = "Bearer " + access_token
        response = requests.get(api_endpoint, headers=headers)
        response_data = response.json()
    
    # Check the response status code
    result = None

    if response.status_code == 200:
        result = response_data
    
    if result:
        opportunity_list = []
        for record in result["records"]:
            opportunity_list.append(record["Name"])

        return opportunity_list
    return result

def run_prompt(message):
    # Step 1: send the conversation and available functions to the model
    model = "gpt-3.5-turbo-0613"
    json_format_prompt = "Please provide the answers in JSON format."
    messages = [{"role": "user", "content": message+json_format_prompt}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_all_opportunities",
                "description": "Get the list of all opportunities of dealstream",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company": {
                            "type": "string",
                            "description": "Dealstream.",
                        },
                    },
                    "required": ["company"],
                },
            },
        },
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        messages.append(response_message) 
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = eval(function_name)
            function_args = eval(tool_call.function.arguments)
            function_response = function_to_call(list(function_args.items())[0][1])
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response)
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content