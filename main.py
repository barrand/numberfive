# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
sys.path.insert(0, 'libs')

import webapp2
import random
import sentences
import urllib2
import cgi
from bs4 import BeautifulSoup

PAGE_START_HTML = """\
<html>
  <body>
    <form action="/" method="post">
    <div><textarea name="urlToXml" rows="1" cols="60">http://mar-numberfive.appspot.com/static/nycmqEpic.xml</textarea></div>
    <div><input type="submit" value="Go"></div>
"""

PAGE_END_HTML = """\
    </form>
  </body>
</html>
"""
description_en = ""
description_br = ""

class MainHandler(webapp2.RequestHandler):
	

	def setupCommonVars(self, soup):
		self.hotelName = soup.hoteldescriptivecontent['hotelname']
		self.cityName = soup.find(contactprofiletype='Property Info').find('cityname').renderContents()
		self.roomCount = soup.find_all('guestroominfo', code='8')[0]['quantity']
		self.suiteCount = soup.find_all('guestroominfo', code='9')[0]['quantity']
		print self.suiteCount
		# self.suiteCount = soup.
		print self.cityName, self.hotelName

	def buildDescriptions(self, soup):
		self.currentLangs = ['en', 'br']
		self.allDescriptions = {}
		for lang in self.currentLangs:
			self.allDescriptions[lang] = ""
		self.setupCommonVars(soup)
		self.addCityJunk(soup)
		self.addRoomJunk(soup)
		# description = addStarJunk(description)
		# description = addHistoricJunk(description)
		# description = addGuestRoomsJunk(description)
		# description = addWifiJunk(description)
		# description = addTechnologyJunk(description)
		# description = addEventSpaceJunk(description)
		# description = addPOIJunk(description)
		# description = addTransportationJunk(description)
		# description = addFitnessJunk(description)
		# description = addPoolJunk(description)
		# description = addRestaurantJunk(description)
		# description = addClosingJunk(description)


	
	def addCityJunk(self, soup):
		for lang in self.currentLangs:
			#get a random city string by the language and replace the city name
			tmpString = random.choice(sentences.cityByLang[lang]).replace('#s', self.cityName);
			tmpString = tmpString.replace('#h', self.hotelName);
			self.allDescriptions[lang] += tmpString + " "

	def addRoomJunk(self, soup):
		for lang in self.currentLangs:
			#get a random city string by the language and replace the city name
			tmpString = random.choice(sentences.roomByLang[lang]).replace('#r', self.roomCount);
			tmpString = tmpString.replace('#s', self.suiteCount);
			self.allDescriptions[lang] += tmpString


	def get(self):
		self.response.write(PAGE_START_HTML)
		self.response.write(sentences.description_en)
		self.response.write(PAGE_END_HTML)
	def post(self):
		self.response.write(PAGE_START_HTML)
		content = urllib2.urlopen(cgi.escape(self.request.get('urlToXml'))).read()
		soup = BeautifulSoup(content)
		self.buildDescriptions(soup)
		for lang in self.currentLangs:
			self.response.write(self.allDescriptions[lang])
			self.response.write('<br><br>')
		self.response.write(PAGE_END_HTML)
		
# class Description(webapp2.RequestHandler):
# 	def post(self):
# 		content = urllib2.urlopen(cgi.escape(self.request.get('urlToXml'))).read()
# 		soup = BeautifulSoup(content)
# 		print soup.hoteldescriptivecontent['hotelname']
# 		self.response.write(soup.hoteldescriptivecontent['hotelname'])
        # self.response.write('<html><body>You wrote:<pre>')
        # self.response.write(cgi.escape(self.request.get('content')))
        # self.response.write('</pre></body></html>')




app = webapp2.WSGIApplication([
    ('/', MainHandler)
    # ('/description', Description),
], debug=True)
