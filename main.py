from flask import Flask, render_template, request, jsonify, make_response

# DB imports
import psycopg2

# Required for generating secret keys
import random
import hashlib
import json
import urlparse

# for urlparse
import os

# Setup url parse to read DB login data as environment string
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

app = Flask(__name__, static_url_path = "")

# simple map to store authenticated users sessionKeys.
auth_verified_users = {}

def connect_to_db():

	print "Creating connection object."
	db_connection = psycopg2.connect(
		database=url.path[1:],
		user=url.username,
		password=url.password,
		host=url.hostname,
		port=url.port
	)

	return db_connection

@app.route("/registerDevice",methods=['GET','POST'])
def register_device():
	device_random_code = request.form['random_hash']

	response = None

	STATUS = "REGISTRATION_SUCCEEDED"
	try:
		# Creating a random number
		app_secret = hashlib.sha224(str(random.random())).hexdigest()

		# Get databsae connection
		connection = connect_to_db()

		# Create cursor
		cursor = connection.cursor()

		# Build query
		statement = """INSERT INTO api_secret_keys VALUES(\'%s\')"""%(app_secret)

		# Execute query
		cursor.execute(statement)

		# Commit query
		connection.commit()

		response = {'STATUS' : STATUS, 'API_SECRET' : app_secret}

		connection.close()
		
	except Exception as e:
		print "DB connection falied!"
		print e
		
		STATUS = "REGISTRATION_FALIED"
		response = {'STATUS' : STATUS}

	return jsonify(response)

@app.route("/get_request", methods=['POST'])
def hello_dammit():

	for req in request.form:
		print req," ",request.form[req]

	return "lol"

@app.route("/getSession", methods=['GET','POST'])
def get_session():
	
	# Get app secret from device
	app_secret = request.form['secret_key']

	print "\n"
	print app_secret
	print "\n"

	response = None

	try:
		# Get connection object
		connection = connect_to_db()

		# Ge ta cursor
		cursor = connection.cursor()

		query = """SELECT * FROM api_secret_keys WHERE secret_key = \'%s\' ;"""%(app_secret)

		print query

		cursor.execute(query)

		data = cursor.fetchall()

		print data
		
		if len(data) == 1:

			STATUS = "SESSION_SUCCESS"
			SESSION_KEY = hashlib.md5(str(random.random())).hexdigest()
			
			query = """INSERT INTO session_keys VALUES(\'%s\',\'%s\',\'%s\',\'%s\')"""%()
			response = {'STATUS' : STATUS, 'SESSION_KEY' : SESSION_KEY}

		else:
			STATUS = "SESSION_FAILED"
			response = {'STATUS' : STATUS}

	except Exception as e:

		print "DB Insert failed."
		STATUS = "FAILED_TO_AUTH"

		print e

		response = {'STATUS' : STATUS}
	return jsonify(response)

@app.route("/getAllSession", methods=['GET','POST'])
def get_keys():
	print auth_verified_users
	return jsonify(auth_verified_users)

@app.route('/', methods=['GET','POST'])
def hello():
	return "Hello!"

@app.route('/initialAssesment', methods=['POST'])
def initialAssesment():
	questions  = {
		NUMBER_OF_QUESTIONS : '2',
		QUESTIONS : {
			1 : {
				STATEMENT : "Hi!, I'm uler, without the E. Who am I named after?",
				OPTION_A : "Leonhard Euler",
				OPTION_B : "Leonardo Da Vinci",
				OPTION_C : "Galilio Galilei",
				OPTION_C : "Nicolaus Copernicus"
			}

			2 : {
				STATEMENT : "Did you see that?",
				OPTION_A : "YES!",
				OPTION_B : "NO"
			}
		}
	}

	return jsonify(questions)
	
if __name__ == "__main__":
	app.run(debug=True)
