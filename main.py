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
from operator import attrgetter, itemgetter

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
		self.poiList = ""
		self.topPoi = self.attractions[0]
		poiCount = 0
		totalPoi = len(self.attractions)
		for a in self.attractions:
			if poiCount < len(self.attractions)-1:
				self.poiList += a + ", "
			else:
				self.poiList += " and the " + a
			poiCount += 1
		
		poiCount = 0
		self.restPoiList = ""
		self.attractions.pop(0)
		for a in self.attractions:
			if poiCount < len(self.attractions)-1:
				self.restPoiList += a + ", "
			else:
				self.restPoiList += " and the " + a
			poiCount += 1
		print "rest of poi list " + self.restPoiList
# self.airportName = soup.find('attraction', attractioncategorycode='1')['attractionname']
# 		if self.airportName is not None:
# 			print "airpport " + str(self.airportName)

		# self.suiteCount = soup.
	def replaceVars(self, str):
		str = str.replace('{hotelName}', self.hotelName)
		str = str.replace('{cityName}', self.cityName)
		str = str.replace('{poiList}', self.poiList)
		str = str.replace('{topPoiDist}', self.topPoiDist)
		str = str.replace('{topPoi}', self.topPoi)
		str = str.replace('{restPoiList}', self.restPoiList)
		return str

	def buildDescriptions(self, soup):
		# self.currentLangs = ['en', 'br']
		self.currentLangs = ['en']
		self.allDescriptions = {}
		self.setupCommonVars(soup)
		uniqueOrderKeys = []
		json_data = open('sentencesTest.json')
		templates = json.load(json_data)
		for lang in self.currentLangs:
			#initialize the string that will hold all the descriptions
			self.allDescriptions[lang] = ""
			#randomize and loop through all the sentence templates
			allSentences = templates['sentences']
			# a = sorted(allSentences, key=self.sortkeypicker(['order', 'priority']))
			allSentences = sorted(allSentences, key=self.sortkeypicker(['priority', 'order']))
			sentencesByOrder = {}
			currentLength = 0
			#loop through all the sentences and fill in the blanks to see how long they will be
			for t in allSentences:
				#create the sentence with all the var filled in
				tmpString = self.fillFromBanks(soup, t)
				#make sure we aren't over the limit, if we are over the limit, remove the sentence
				if currentLength + len(tmpString) > templates['maxLimit']:
					a.remove(t)
				else:
					currentLength += len(tmpString)
					t['output'] = tmpString
					uniqueOrderKeys.append(t['order'])
					try:
						sentencesByOrder[t['order']]
					except KeyError:
						sentencesByOrder[t['order']] = []
					sentencesByOrder[t['order']].append(t)

			#make it a uniqe list
			uniqueOrderKeys = sorted(list(set(uniqueOrderKeys)))
			
			print "uniq order keys " + str(sentencesByOrder)
			#for every unique order entry
			for k in uniqueOrderKeys:
				print "k " + str(k)
				print "sentencesByOrder[k] " + str(sentencesByOrder[k])
				# 	#grab all the sentences with that order parameter
				shuffle(sentencesByOrder[k])
				# #loop through those sentences and add the output
				for t in sentencesByOrder[k]:
					try:
						self.allDescriptions[lang] += t['output']
					except KeyError:
						print "\tCOULDN'T ADD " + str(t)

			self.allDescriptions[lang] = self.replaceVars(self.allDescriptions[lang])

		json_data.close()

	def sortkeypicker(self, keynames):
	    negate = set()
	    for i, k in enumerate(keynames):
	        if k[:1] == '-':
	            keynames[i] = k[1:]
	            negate.add(k[1:])
	    def getit(adict):
	       composite = [adict[k] for k in keynames]
	       for i, (k, v) in enumerate(zip(keynames, composite)):
	           if k in negate:
	               composite[i] = -v
	       return composite
	    return getit

	#function to pick a random sentence, and fill it from the banks
	def fillFromBanks(self, soup, t):
		tmpString = ""
		tmpString = self.recursiveFindPhrase(t['phrases'], tmpString)
		print "ready to fill from banks " + tmpString
		for b in t['banks'].keys():
			print "b " + b
			#create a list of all the options from this particular bank
			bOptions = t['banks'][b].split('/')
			if tmpString.find("{b") > -1:
				tmpString = tmpString.replace("{"+b+"}", random.choice(bOptions))
		return tmpString

	def recursiveFindPhrase(self, phraseList, tmpString):
		# find a random phrase choice from the base list
		tmpPhrase = random.choice(phraseList)

		# add the part of the phrase from our random choice
		tmpString += tmpPhrase['phrase']

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
