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
import json
from pprint import pprint
import cgi
from bs4 import BeautifulSoup
from random import shuffle

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


		# wifiTag = soup.find('businessservicecode', code='69', existscode='1')
		# print "wifi " + wifiTag

		meetingRoomTag = soup.find('meetingrooms')
		self.meetingRooms = meetingRoomTag['meetingroomcount']
		self.totalRoomSpace = meetingRoomTag['totalroomspace']
		self.totalRoomSpaceUnit = meetingRoomTag['unitofmeasure']
		# print self.meetingRooms + self.totalRoomSpace + self.totalRoomSpaceUnit

		# self.airportName = soup.find('attraction', attractioncategorycode='1')['attractionname']
		# if self.airportName is not None:
		# 	print "airpport " + str(self.airportName)

		# cityCenterTag = sout.find('attraction', attractioncategorycode='68')

		# self.musicPlace = soup.find('attraction', attractioncategorycode='71')['attractionname']
		# if self.musicPlace is not None:
		# 	print "music " + str(self.musicPlace)

		self.attractions = []
		attractionTag = soup.find_all('attraction', attractioncategorycode='62')
		for t in attractionTag:
			if int(t['sort']) < 6:
				self.attractions.append(t['attractionname'])
				if int(t['sort']) == 1:
					self.topPoiDist = t.find_all('refpoint')[0]['distance']
# self.airportName = soup.find('attraction', attractioncategorycode='1')['attractionname']
# 		if self.airportName is not None:
# 			print "airpport " + str(self.airportName)

		# self.suiteCount = soup.

	def buildDescriptions(self, soup):
		# self.currentLangs = ['en', 'br']
		self.currentLangs = ['en']
		self.allDescriptions = {}
		self.setupCommonVars(soup)
		json_data = open('sentencesTest.json')
		templates = json.load(json_data)
		for lang in self.currentLangs:
			#initialize the string that will hold all the descriptions
			self.allDescriptions[lang] = ""
			#randomize and loop through all the sentence templates
			randomSentences = templates['sentences']
			random.shuffle(randomSentences)
			sentencesByOrder = {}
			for t in randomSentences:
				# #fill in the holders from the banks
				tmpString = self.fillFromBanks(soup, t)

				try:
					sentencesByOrder[t['order']]
				except KeyError:
					sentencesByOrder[t['order']] = []
				
				sentencesByOrder[t['order']].append(tmpString)
				
				

			#Put in the sentences according to their order parameter
			for i in range(1, len(sentencesByOrder)+1):
				#keep the description as it was before we add the new sentence in case it will be too long.
				origDescription = self.allDescriptions[lang]

				for s in sentencesByOrder[i]:
					self.allDescriptions[lang] += s 

				#only add the sentence if we aren't over the limit
				# if len(self.allDescriptions[lang]) > 900:
				# 	self.allDescriptions[lang] = origDescription


		json_data.close()

	#function to pick a random sentence, and fill it from the banks
	def fillFromBanks(self, soup, t):
		tmpString = ""
		tmpString = self.recursiveFindPhrase(t['phrases'], tmpString)
		for b in t['banks'].keys():
			#create a list of all the options from this particular bank
			bOptions = t['banks'][b].split('/')
			if tmpString.find("{b") > -1:
				tmpString = tmpString.replace("{"+b+"}", random.choice(bOptions))
		print tmpString
		return tmpString

	def recursiveFindPhrase(self, phraseList, tmpString):
		# find a random phrase choice from the base list
		tmpPhrase = random.choice(phraseList)
		print "r tmpPhrase" + str(tmpPhrase)

		# add the part of the phrase from our random choice
		tmpString += tmpPhrase['phrase']
		print "tmpString in r " + tmpString

		# see if there are additional sub-phrases to add on the end of this string
		if tmpPhrase.get('phrases'):
			return self.recursiveFindPhrase(tmpPhrase['phrases'], tmpString)
		else:
			return tmpString


	# def addAttractionJunk(self, soup):
	# 	for lang in self.currentLangs:
	# 		# tmpString = random.choice(sentences.attractionsByLang[lang]).replace('#n', self.hotelName);
	# 		json_data = open('sentences.json')
	# 		data = json.load(json_data)
			

	# 		tmpString = random.choice(data['sentences']['pois']['phrases'])['phrase']
	# 		poiList = ""
	# 		poiCount = 0
	# 		totalPoi = len(self.attractions)
	# 		for a in self.attractions:
	# 			if poiCount < totalPoi -1:
	# 				poiList += a + ", "
	# 			else:
	# 				poiList += " and the " + a + "."
	# 			poiCount += 1
	# 		tmpString = tmpString.replace('{poiList}', poiList)
	# 		tmpString = tmpString.replace('{topPoi}', self.attractions[0])
	# 		print "dazed and confused " + self.topPoiDist
	# 		tmpString = tmpString.replace('{topPoiDist}', str(self.topPoiDist))

	# 		print "tmpString " + str(tmpString)
	# 		b1 = data['sentences']['pois']['b1'].split('/')
	# 		b2 = data['sentences']['pois']['b2'].split('/')
	# 		b3 = data['sentences']['pois']['b3'].split('/')
	# 		print "b1 " + str(b1)
	# 		tmpString = tmpString.replace('{b1}', random.choice(b1))
	# 		tmpString = tmpString.replace('{b2}', random.choice(b2))
	# 		tmpString = tmpString.replace('{b3}', random.choice(b3))
	# 		tmpString = tmpString.replace('{hotel}', self.hotelName)
	# 		# attList = ""
	# 		# for a in self.attractions:
	# 		# 	attList += a + ", "
	# 		# tmpString = tmpString.replace('#a', attList)
	# 		self.allDescriptions[lang] += tmpString

	# 		json_data.close()



	def get(self):
		self.response.write(PAGE_START_HTML)
		content = urllib2.urlopen(cgi.escape("http://mar-numberfive.appspot.com/static/nycmqEpic.xml")).read()
		soup = BeautifulSoup(content)
		self.buildDescriptions(soup)
		for lang in self.currentLangs:
			self.response.write('<br><b>' + lang + '</b><br>')
			self.response.write(self.allDescriptions[lang])
			self.response.write('<br><br>')
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
