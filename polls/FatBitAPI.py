# -*- coding: utf-8 -*-
import os
import sys
import requests, json
from requests_oauthlib import OAuth1
# import time 
from pprint import pprint
import urllib

# constants, configure to match your environment
HOST = 'https://api.fitbit.com'


# belongs to alan hau user permanently after initial login
user_access_token = '15cc6ca3c96263654162c0c253289a32'
user_access_token_secret = 'a8dbe3a07feee5dc68c4d3ff74c5613b'

# belongs to software on server
client_Consumer_Key = '8c0ce206dc9446468b2e34474a357f4f'
client_Consumer_Secret = '2052f53de91b488d81d303cb7f0db291'


def getCalories(istr):
  # accesses API to get food calorie information, if no info, return 0
  istr = urllib.urlencode({
    "query" : istr
    })

  api_url = '/1/foods/search.json?{}'.format(istr)
  r = reqAPI(api_url)

  try:
    return r['foods'][0]['calories']
  except:
    return 0

def getFloorsTimeSeries():
  api_url = '/1/user/-/activities/floors/date/today/1m.json'
  r = reqAPI(api_url)
  try:
    result = []
    for i in r['activities-floors']:
      result.append((i['dateTime'], int(i['value'])))
    return result

  except:
    return []
  

def reqAPI(reqResourceURL):
  # signature = 'OAuth oauth_nonce="abc", oauth_timestamp="123", oauth_version="1.0", oauth_signature_method="HMAC-SHA1", oauth_consumer_key="foo", oauth_signature="h2sRqLArjhlc5p3FTkuNogVHlKE%3D"'
  auth = OAuth1(
    client_key=client_Consumer_Key, 
    client_secret=client_Consumer_Secret,
    resource_owner_key=user_access_token, 
    resource_owner_secret=user_access_token_secret,
    signature_method='HMAC-SHA1')

  url = '{}{}'.format(HOST,reqResourceURL)
  r = requests.get(url, auth=auth)

  return json.loads(r.text.encode('ascii', 'ignore')  )



# res = json.loads(searchServer("healthcare"))


# print res
# print res['hits']['hits'][0]['fields']['file'][0]


if __name__ == "__main__":
  # print getNonce(), int(time.time())
  # r = reqAPI('/1/foods/search.json?query=chicken%20parmesan')
  # pprint(r)

  # print getCalories('chicken parmesan fish toad')

  pprint (getFloorsTimeSeries())
  



