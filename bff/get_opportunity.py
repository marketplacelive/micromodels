from flask import session
from get_access_token import get_access_token
import requests

def get_all_opportunities():
    """Get sales notes from Dealstream API in a given location"""
    api_endpoint = "https://dealstream-dev-ed.develop.my.salesforce.com/services/data/v56.0/query/?q=SELECT Id, Name, Account.Name, StageName, Probability, CreatedDate, Engagementscore__c, LastAction__c, Contact__c, LastActivityDate FROM  Opportunity"
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
    if response.status_code == 200:
        keys_mapping = {
            'opportunity': 'Name',
            'account_name':'Name',
            'deal_stage': 'StageName',
            'conversion_probability': 'Probability',
            'enagagement_score': 'Engagementscore__c',
            'last_active': 'LastActivityDate',
            'last_action': 'LastAction__c',
            'contact': 'Contact__c',
            'created_date': 'CreatedDate',
            'id': 'Id',
        }
        response_list = [{new_key: record.get(old_key) if new_key != 'account_name' else record.get('Account',{}).get(old_key) for new_key, old_key in keys_mapping.items()} for record in response_data['records']] 
        return response_list
    return []
