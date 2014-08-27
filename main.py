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

class MainHandler(webapp2.RequestHandler):
	

	def setupCommonVars(self, soup):
		self.hotelName = soup.hoteldescriptivecontent['hotelname']
		self.cityName = soup.find(contactprofiletype='Property Info').find('cityname').renderContents()
		self.roomCount = soup.find_all('guestroominfo', code='8')[0]['quantity']
		self.suiteCount = soup.find_all('guestroominfo', code='9')[0]['quantity']
		urbanTags = soup.find_all('locationcategory', code='3', existscode='1', codedetail="Location Type: City")
		if len(urbanTags) > 0:
			self.isUrban = True
		else:
			self.isUrban = False
					
		suburbanTags = soup.find_all('locationcategory', code='13', existscode='1', codedetail="Location Type: Suburban")
		if len(suburbanTags) > 0:
			self.isSuburban = True
		else:
			self.isSuburban = False
		
		freeBreakfastTag = soup.find('service', code='138', existscode='1')
		if freeBreakfastTag is not None:
			self.freeBreakfast = True
		else:
			self.freeBreakfast = False

		print "free breakfast " + str(self.freeBreakfast)

		# wifiTag = soup.find('businessservicecode', code='69', existscode='1')
		# print "wifi " + wifiTag

		meetingRoomTag = soup.find('meetingrooms')
		self.meetingRooms = meetingRoomTag['meetingroomcount']
		self.totalRoomSpace = meetingRoomTag['totalroomspace']
		self.totalRoomSpaceUnit = meetingRoomTag['unitofmeasure']
		print self.meetingRooms + self.totalRoomSpace + self.totalRoomSpaceUnit

		self.airportName = soup.find('attraction', attractioncategorycode='1')['attractionname']
		if self.airportName is not None:
			print "airpport " + str(self.airportName)

		# cityCenterTag = sout.find('attraction', attractioncategorycode='68')

		self.musicPlace = soup.find('attraction', attractioncategorycode='71')['attractionname']
		if self.musicPlace is not None:
			print "music " + str(self.musicPlace)

		self.attractions = []
		attractionTag = soup.find_all('attraction', attractioncategorycode='18')
		for t in attractionTag:
			self.attractions.append(t['attractionname'])
		print "attractions " + str(self.attractions)
# self.airportName = soup.find('attraction', attractioncategorycode='1')['attractionname']
# 		if self.airportName is not None:
# 			print "airpport " + str(self.airportName)

		# self.suiteCount = soup.

	def buildDescriptions(self, soup):
		self.currentLangs = ['en', 'br']
		self.allDescriptions = {}
		for lang in self.currentLangs:
			self.allDescriptions[lang] = ""
		self.setupCommonVars(soup)
		self.addCityJunk(soup)
		self.addUrbanJunk(soup)
		self.addRoomJunk(soup)
		self.addMeetingsJunk(soup)
		self.addAirportJunk(soup)
		self.addMusicJunk(soup)
		self.addAttractionJunk(soup)
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

	def addUrbanJunk(self, soup):
		for lang in self.currentLangs:
			tmpString = random.choice(sentences.urbanByLang[lang]).replace('#s', self.cityName);
			self.allDescriptions[lang] += tmpString

	def addRoomJunk(self, soup):
		for lang in self.currentLangs:
			#get a random city string by the language and replace the city name
			tmpString = random.choice(sentences.roomByLang[lang]).replace('#r', self.roomCount);
			tmpString = tmpString.replace('#s', self.suiteCount);
			self.allDescriptions[lang] += tmpString

	def addMeetingsJunk(self, soup):
		for lang in self.currentLangs:
			#get a random city string by the language and replace the city name
			tmpString = random.choice(sentences.meetingByLang[lang]).replace('#n', self.meetingRooms);
			tmpString = tmpString.replace('#s', self.totalRoomSpace);
			tmpString = tmpString.replace('#u', self.totalRoomSpaceUnit);
			self.allDescriptions[lang] += tmpString

	def addAirportJunk(self, soup):
		for lang in self.currentLangs:
			#get a random city string by the language and replace the city name
			tmpString = random.choice(sentences.airportByLang[lang]).replace('#a', self.airportName);
			self.allDescriptions[lang] += tmpString

	def addMusicJunk(self, soup):
		for lang in self.currentLangs:
			tmpString = random.choice(sentences.musicByLang[lang]).replace('#m', self.musicPlace);
			self.allDescriptions[lang] += tmpString

	def addAttractionJunk(self, soup):
		for lang in self.currentLangs:
			tmpString = random.choice(sentences.attractionsByLang[lang]).replace('#n', self.hotelName);
			attList = ""
			for a in self.attractions:
				attList += a + ", "
			tmpString = tmpString.replace('#a', attList)
			self.allDescriptions[lang] += tmpString



	def get(self):
		self.response.write(PAGE_START_HTML)
		self.response.write(PAGE_END_HTML)
	def post(self):
		self.response.write(PAGE_START_HTML)
		content = urllib2.urlopen(cgi.escape(self.request.get('urlToXml'))).read()
		soup = BeautifulSoup(content)
		self.buildDescriptions(soup)
		for lang in self.currentLangs:
			self.response.write('<br><b>' + lang + '</b><br>')
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
