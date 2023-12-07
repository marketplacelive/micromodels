from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os

load_dotenv()

def get_access_token():
# Salesforce OAuth 2.0 credentials
    client_id = os.getenv('client_id')
    username = os.getenv('username')
    password = os.getenv('password')
    grant_type = 'password'

    # Instantiate Salesforce object to get access token
    sf = Salesforce(
        username=username,
        password=password,
        security_token='',  
        client_id=client_id,
    )

    # Use the get_session method to obtain an authenticated session
    access_token = sf.session_id
    return access_token
    