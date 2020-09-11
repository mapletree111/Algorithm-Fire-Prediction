from google.appengine.ext import ndb

import webapp2
import json
import random

class predictCalls(ndb.Model):
	id=ndb.StringProperty()
	cause=ndb.StringProperty()
	year=ndb.IntegerProperty(required=True)
	location=ndb.IntegerProperty(required=True)
	callcount=ndb.IntegerProperty(required=True)

class predictionHandler(webapp2.RequestHandler):
	def post(self):
		post_data = json.loads(self.request.body)
		input_year = False
		input_location = False
		input_callcount = False
		input_cause = False
		for category in post_data:
			if category == "year":
				input_year = True
			elif category == "location":
				input_location = True
			elif category == "callcount":
				input_callcount = True
			elif category == "cause":
				input_cause = True
		if input_year and input_location and input_callcount:
			post_prediction = predictCalls(year=post_data['year'],
										 location=post_data['location'],
										 callcount=post_data['callcount'])
			post_prediction.put()
			if input_cause:
				post_prediction.cause=post_data['cause'] 
			post_prediction.id=str(post_prediction.key.urlsafe())
			post_prediction.put()
			post_prediction_dict = post_prediction.to_dict()
			post_prediction_dict['self'] = '/calls/' + post_prediction.key.urlsafe()
			self.response.write(json.dumps(post_prediction_dict))
		else:
			self.response.status = 400
			self.response.write("ERROR: expected format => {\"year\": \"int\", \"location\": \"int\", \"callcount\": \"int\"}")

	def get(self, id=None):
		if id:
			call_exists = False
			for call in predictCalls.query():
				if call.id == id:
					call_exists = True
			if call_exists:
				get_call = ndb.Key(urlsafe=id).get()
				get_call_dict = get_call.to_dict()
				get_call_dict['self'] = "/calls/" + id
				self.response.write(json.dumps(get_call_dict))
				
			else:
				self.response.status=400
				self.response.write("Error: Cannot find call data / call data does not exist")
		else:
			get_call_query_results = [get_call_query.to_dict()
									  for get_call_query in predictCalls.query()]
			for call in get_call_query_results:
				call['self'] = "/calls/" + str(call['id'])
			self.response.write(json.dumps(get_call_query_results))

	def delete(self, id=None):
		if id:
			b = ndb.Key(urlsafe=id).get()
			b_cause = b.cause
			b_year = b.year
			b_location = b.location
			b_callcount = b.callcount
			b.key.delete()
			self.response.write("Successful DELETED " + str(b_cause)+" "+str(b_year)+" "+str(b_location)+" "+str(b_callcount))
		else:
			self.response.status = 400
			self.response.write("Error, entry not found")

class queryHandler(webapp2.RequestHandler):
	#Expected URL to follow format: /calls/?year=2016&location=214&cause=321
	def get(self, url):
		year = int(self.request.get("year"))
		location = int(self.request.get("location"))
		cause = self.request.get("cause")
		input_year = False
		input_location = False
		input_cause = False
		
		if year:
			input_year = True
		if location:
			input_location = True
		if cause:
			input_cause = True

		if input_year and input_location and input_cause:
			for call in predictCalls.query():
				if call.year == year and call.location == location and call.cause == cause:
					self.response.write(call.callcount)
		else:
			self.response.status=400
			self.response.write("Error: Cannot find data")
		

# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
       self.response.write("The Visionary's Call Predictor")

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/calls', predictionHandler),
	('/calls/query/(.*)', queryHandler),
    ('/calls/(.*)', predictionHandler)
], debug=True)
# [END app]