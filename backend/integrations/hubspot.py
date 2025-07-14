# hubspot.py
import json
import secrets
import asyncio
import urllib.parse  
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import requests

from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID = 'XXX'
CLIENT_SECRET = 'XXX'

REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
authorization_url = 'https://app.hubspot.com/oauth/authorize'
scope = 'oauth crm.objects.contacts.read'

async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }

    raw_state = json.dumps(state_data)
    encoded_state = urllib.parse.quote(raw_state)

    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', raw_state, expire=600)

    auth_url = (
        f'{authorization_url}?client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope={scope}&state={encoded_state}&response_type=code'
    )
    return auth_url

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))

    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')

    decoded_state = urllib.parse.unquote(encoded_state)
    state_data = json.loads(decoded_state)

    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')
    original_state = state_data.get('state')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State mismatch.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )

    credentials = response.json()
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(credentials), expire=600)

    return HTMLResponse(content="""
    <html>
        <script>
            window.close();
        </script>
    </html>
    """)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return json.loads(credentials)

def create_integration_item_metadata_object(item, item_type='Contact') -> IntegrationItem:
    return IntegrationItem(
        id=item.get('id'),
        name=item.get('properties', {}).get('firstname', 'Unknown') + ' ' + item.get('properties', {}).get('lastname', ''),
        type=item_type,
        creation_time=None,
        last_modified_time=None,
        parent_id=None,
        parent_path_or_name=None
    )

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    access_token = credentials.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    response = requests.get(url, headers=headers)

    items = []
    if response.status_code == 200:
        results = response.json().get('results', [])
        for item in results:
            items.append(create_integration_item_metadata_object(item, 'Contact'))

    print(items)
    return items
