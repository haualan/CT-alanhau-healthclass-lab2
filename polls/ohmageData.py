# -*- coding: utf-8 -*-
import os
import sys
import requests, json, base64, pickle, time
from requests_oauthlib import OAuth2, OAuth1
from requests_oauthlib import OAuth2Session, OAuth1Session
from splinter import Browser
from pprint import pprint
import numpy as np

BASE_DIR = os.path.dirname(__file__)
base_url = 'https://ohmage-omh.smalldata.io/dsu'
client_id = '5555-2015-alan'
client_secret = 'Rtg43jkLD7z76c'
redirect_uri = 'http://localhost:7777/callback'
# redirect_uri = 'http://www.google.com'
# token = 'y4auuD'

b64Val = 'Basic ' + base64.b64encode('{}:{}'.format(client_id, client_secret))
auth_headers = {'Authorization': b64Val}

class ohmageDataClass:
  """docstring for ohm"""
  def __init__(self):
    self.arg = 'arg'
    self.tokens = pickle.load( open( BASE_DIR +'/user_tokens.p', "rb" ) )
    # self.renewIfNecessary()


  def login(self, open_browser = False):
    # request_token_url = 'https://ohmage-omh.smalldata.io/dsu/oauth/authorize?client_id={}&response_type=code'.format(client_key)
    
    # client_id = '48636836762-mulldgpmet2r4s3f16s931ea9crcc64m.apps.googleusercontent.com'
    # base_url = 'https://lifestreams.smalldata.io/dsu'

    request_token_url = base_url +'/oauth/authorize?client_id={}&response_type=code'.format(client_id)
    print request_token_url

    oauth = OAuth2Session(client_id)
    authorization_url, state = oauth.authorization_url(request_token_url)
    print authorization_url, state

    if open_browser:
      browser = Browser()
      browser.visit(authorization_url)
      token = raw_input('enter code from google sign in:')
      return token
    else:
      return authorization_url

    

    # oauth = OAuth2Session(client_id, scope = scope, redirect_uri = redirect_uri)
    # authorization_url, state = oauth.authorization_url(request_token_url,
    # # offline for refresh token
    # # force to always make user click authorize
    # access_type="offline", approval_prompt="force")
    # print 'Please go here and authorize,', authorization_url
  def getAccessToken(self, code):
    request_token_url = base_url + '/oauth/token'

    payload = {'code': code, 'grant_type': 'authorization_code'}
    r = requests.post(url=request_token_url, params = payload, headers = auth_headers)
    r = json.loads(r.text.encode('ascii', 'ignore'))

    pickle.dump( r, open( BASE_DIR + '/user_tokens.p', "wb" ) )

    return r

  def checkToken(self):
    checkToken_url = base_url + '/oauth/check_token?token={}'.format(self.tokens['access_token'])
    r = requests.get(url= checkToken_url)
    r = json.loads(r.text.encode('ascii', 'ignore'))
    # print r
    return r

  def renewToken(self):
    renewToken_url = base_url + '/oauth/token'
    payload = {'refresh_token': self.tokens['refresh_token'], 'grant_type': 'refresh_token'}
    r = requests.post(url=renewToken_url, params = payload, headers = auth_headers)
    r = json.loads(r.text.encode('ascii', 'ignore'))

    pickle.dump( r, open( BASE_DIR + '/user_tokens.p', "wb" ) )

    self.tokens = r

    # print r

  def renewIfNecessary(self):
    # Checks if token is expired and renews user tokens if so.
    r = self.checkToken()
    # epoch_time = int(time.time())
    if 'error' in r:
      print 'token expired... renewing'
      self.renewToken()

  def getDataPoints(self, schema_namespace, schema_name,fromDate = None , toDate = None, schema_version = '1.0' ):
    self.renewIfNecessary()
    url = base_url + '/dataPoints'
    payload = {
      'schema_namespace':schema_namespace,
      'schema_name':schema_name,
      'schema_version':schema_version,
      }

    if not(fromDate is None):
      payload['created_on_or_after'] = fromDate

    if not(toDate is None):
      payload['created_before'] = toDate


    # print payload

    
    headers = {'Authorization': 'Bearer {}'.format(self.tokens['access_token'])}
    # print headers
    r = requests.get(url = url, headers = headers, params = payload)
    # print r
    try:
      r = json.loads(r.text.encode('ascii', 'ignore'))
      # print r
    except:
      print 'some error has occured'
      # print r

    return r

  def parse_pam(self, iData):
    """
    takes pam data input from omh and parses them to data for plot generation

    """


    # print len(iData)
    negative_affect = []
    positive_affect = []
    pam_datetimes = []

    for i in iData:
      negative_affect.append(int(i['body']['negative_affect']['value']))
      positive_affect.append(int(i['body']['positive_affect']['value']))
      pam_datetimes.append(np.datetime64(i['body']['effective_time_frame']['date_time']))

    # print pam_datetimes
    return np.array(negative_affect), np.array(positive_affect), np.array(pam_datetimes)

  def parse_mobility_daily_summary(self, iData):
    mobilty_dates = []
    mobilty_walking_distance_in_km = []

    # pprint(iData)


    for i in iData:
      # print i['body']['date']
      mobilty_dates.append(np.datetime64(i['body']['date']))
      mobilty_walking_distance_in_km.append(float(i['body']['walking_distance_in_km']))

    
    return np.array(mobilty_walking_distance_in_km), np.array(mobilty_dates)






if __name__ == "__main__":
  a = ohmageDataClass()

  # token = a.login()

  # a.getAccessToken(token)
  # print a.checkToken()
  # print a.tokens

  # a.renewToken()
  # print a.getDataPoints(fromDate = '2012-09-18T14:01:54.9571247Z')

  # pprint(a.getDataPoints(schema_namespace = 'cornell', schema_name = 'mobility-daily-segments'))
  pprint (a.parse_mobility_daily_summary(a.getDataPoints(schema_namespace = 'cornell', schema_name = 'mobility-daily-summary')))

  pprint(a.parse_pam(a.getDataPoints(schema_namespace = 'omh', schema_name = 'pam')))

  




