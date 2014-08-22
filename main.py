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
		print self.cityName, self.hotelName

	def buildDescription(self, soup):
		self.setupCommonVars(soup)
		toReturn = ""
		toReturn = self.addCityJunk(soup, toReturn)
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
		return toReturn


	
	def addCityJunk(self, soup, toReturn):
		city1 = "When visiting #s, there is no better place to stay than #h."
		city2 = "Come see why the #h is the treasure of #s."
		city3 = "Celebrate #s with a stay in #h."
		city4 = "Without a doubt #h has the best that #s has to offer."
		city5 = "Enjoy the sights and sounds of #s while visiting #h."
	
		tmpString = city1.replace('#s', self.cityName);
		tmpString = tmpString.replace('#h', self.hotelName);
		return toReturn + " goo "+ tmpString

	def get(self):
		self.response.write(PAGE_START_HTML)
		self.response.write(PAGE_END_HTML)
	def post(self):
		self.response.write(PAGE_START_HTML)
		content = urllib2.urlopen(cgi.escape(self.request.get('urlToXml'))).read()
		soup = BeautifulSoup(content)
		output = self.buildDescription(soup)
		self.response.write(output)
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
