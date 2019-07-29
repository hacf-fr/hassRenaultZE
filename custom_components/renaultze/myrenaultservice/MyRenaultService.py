"""Support for Renault ZE services."""

import aiohttp
import asyncio
import json
import base64
import time
import datetime
import urllib

class MyRenaultServiceException(Exception):
    def __init__(self, value):
        sections = value.split(".")
        self.value = sections[len(sections)-1]

    def __str__(self):
        return repr(self.value)

class MyRenaultService:
    def __init__(self, gigya_username, gigya_password):
        """Initialize the sensor."""
        self._gigya_username = gigya_username
        self._gigya_password = gigya_password
        self._gigya_root_url = None
        self._gigya_api_key = None
        self._gigya_session_details = None
        self._gigya_account_details = None
        self._gigya_jwt_details = None
        self._kamereon_root_url = None
        self._kamereon_api_key = None
        self._kamereon_person_id = None
        self._kamereon_account_id = None

    def initialise_configuration_url(self, gigya_root_url, gigya_api_key, kamereon_root_url, kamereon_api_key):
        """Initialize the sensor."""
        self._gigya_root_url = gigya_root_url
        self._gigya_api_key = gigya_api_key
        self._kamereon_root_url = kamereon_root_url
        self._kamereon_api_key = kamereon_api_key

    async def initialise_configuration(self, language):
        url = 'https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_%s.json' % language
        async with aiohttp.ClientSession(
                ) as session:
            async with session.get(url) as response:
                responsetext = await response.text()
                if responsetext == '':
                    responsetext = '{}'
                jsonresponse = json.loads(responsetext)

                self.initialise_configuration_url(
                    jsonresponse['servers']['gigyaProd']['target'],
                    jsonresponse['servers']['gigyaProd']['apikey'],
                    jsonresponse['servers']['wiredProd']['target'],
                    jsonresponse['servers']['wiredProd']['apikey']
                    )

    async def gigya_login(self, session):
        #print('gigya_login')
        payload = {'loginID': self._gigya_username, 'password': self._gigya_password, 'apiKey': self._gigya_api_key}
        url = self._gigya_root_url + '/accounts.login?' + urllib.parse.urlencode(payload)
        async with session.get(url) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            if 'message' in jsonresponse:
                self.tokenData = None
                raise MyRenaultServiceException(jsonresponse['message'])
            self._gigya_session_details = jsonresponse

    async def gigya_get_account_info(self, session, gigya_cookie_value):
        #print('gigya_get_account_info')
        payload = {'oauth_token': gigya_cookie_value}
        url = self._gigya_root_url + '/accounts.getAccountInfo?' + urllib.parse.urlencode(payload)
        async with session.get(url) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            if 'message' in jsonresponse:
                self.tokenData = None
                raise MyRenaultServiceException(jsonresponse['message'])
            self._gigya_account_details = jsonresponse
            self._kamereon_person_id = self._gigya_account_details['data']['personId']

    async def gigya_get_jwt(self, session, gigya_cookie_value):
        #print('gigya_get_jwt')
        payload = {'oauth_token': gigya_cookie_value, 'fields': 'data.personId,data.gigyaDataCenter', 'expiration': 900}
        url = self._gigya_root_url + '/accounts.getJWT?' + urllib.parse.urlencode(payload)
        async with session.get(url) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            if 'message' in jsonresponse:
                self.tokenData = None
                raise MyRenaultServiceException(jsonresponse['message'])
            jsonresponse['expiry'] = datetime.datetime.strptime(jsonresponse['time'], "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(seconds=900)
            self._gigya_jwt_details = jsonresponse

    async def kamereon_get_account_id(self, session, gigya_jwt_token):
        #print('kamereon_get_account_id')
        payload = {'country': 'FR'}
        headers = {'x-gigya-id_token': gigya_jwt_token, 'apikey': self._kamereon_api_key}
        url = self._kamereon_root_url + '/commerce/v1/persons/' + self._kamereon_person_id + '?' + urllib.parse.urlencode(payload)
        async with session.get(url, headers=headers) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            if 'message' in jsonresponse:
                self.tokenData = None
                raise MyRenaultServiceException(jsonresponse['message'])
            self._kamereon_account_id = jsonresponse['accounts'][0]['accountId']

    async def get_gigya_token(self, session):
        #print('get_gigya_token')
        if (self._gigya_jwt_details is None or (datetime.datetime.utcnow() > self._gigya_jwt_details['expiry'])):
            await self.gigya_login(session)
            gigya_cookie_value = self._gigya_session_details['sessionInfo']['cookieValue']
            if (self._kamereon_person_id is None):
                await self.gigya_get_account_info(session, gigya_cookie_value)
            await self.gigya_get_jwt(session, gigya_cookie_value)
        return self._gigya_jwt_details['id_token']

    async def get_kamereon_access_token(self, session, gigya_jwt_token):
        #print('get_kamereon_access_token')
        if (self._kamereon_person_id is None):
            await self.get_gigya_token(session)

        if (self._kamereon_account_id is None):
            await self.kamereon_get_account_id(session, gigya_jwt_token)

        payload = {'country': 'FR'}
        headers = {'x-gigya-id_token': gigya_jwt_token, 'apikey': self._kamereon_api_key}
        url = self._kamereon_root_url + '/commerce/v1/accounts/' + self._kamereon_account_id + '/kamereon/token?' + urllib.parse.urlencode(payload)
        async with session.get(url, headers=headers) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            if 'message' in jsonresponse:
                self.tokenData = None
                raise MyRenaultServiceException(jsonresponse['message'])
            return jsonresponse['accessToken']

    async def apiGetCall(self, path):
        url = self._kamereon_root_url + path
        async with aiohttp.ClientSession(
                ) as session:
            gigya_jwt_token = await self.get_gigya_token(session)
            kamereon_access_token = await self.get_kamereon_access_token(session, gigya_jwt_token)
            headers = {'x-gigya-id_token': gigya_jwt_token, 'apikey': self._kamereon_api_key, 'x-kamereon-authorization' : 'Bearer ' + kamereon_access_token}
            async with session.get(url, headers=headers) as response:
                responsetext = await response.text()
                if responsetext == '':
                    responsetext = '{}'
                jsonresponse = json.loads(responsetext)
                if 'message' in jsonresponse:
                    self.tokenData = None
                    raise MyRenaultServiceException(jsonresponse['message'])
                return jsonresponse

    async def apiGetBatteryStatus(self, vin):
        path = '/commerce/v1/accounts/kmr/remote-services/car-adapter/v1/cars/%s/battery-status' % vin
        return await self.apiGetCall(path)
