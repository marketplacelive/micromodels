from flask import session
from get_access_token import get_access_token
import requests
import re

def get_sales_notes(opportunity_id):
    """Get sales notes from Dealstream Salesforce API """
    api_endpoint = "https://dealstream-dev-ed.develop.my.salesforce.com/services/data/v56.0/query/?q=SELECT Date__c, Note__c  FROM Notes__c WHERE Opportunity__c='" + opportunity_id + "' ORDER BY Date__c ASC LIMIT 50"
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
        access_token = get_access_token()
        session["access_token"] = access_token
        headers["Authorization"] = "Bearer " + access_token
        response = requests.get(api_endpoint, headers=headers)
        response_data = response.json()

    # Check the response status code
    result = None
    if response.status_code == 200:
        result = response_data
    
    if result:
        sales_notes = ""
        for note in result["records"]:
            if note['Date__c']:
                sales_notes += note["Date__c"] + " - " + note["Note__c"] + " "
            else: 
                sales_notes += note["Note__c"] + " "
        result = re.sub(r'\s+', ' ', sales_notes)
    return result
