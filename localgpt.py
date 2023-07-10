from cgpt import CGPT

import flask
from flask_wtf import CSRFProtect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import argparse
import json
import hashlib
import logging

logging.basicConfig(filename="lclgpt.log", level=logging.DEBUG)

app = flask.Flask(__name__)
with open("secret_key.txt", "rt") as fin:
	secret_key = fin.read()
app.config["SECRET_KEY"] = secret_key

csrf = CSRFProtect(app)

auth = HTTPBasicAuth()
with open("auth_users.json", "rt") as fin:
	users = json.load(fin)
users = {k: generate_password_hash(v) for k, v in users.items()}

@auth.verify_password
def verify_password(username, password):
	password_hash = hashlib.sha256(password.encode()).hexdigest()
	if username in users and check_password_hash(users.get(username), password_hash):
		return username

@app.route("/", methods=["GET", "POST"])
@auth.login_required
def index():
	messages = None
	if "cgpt" in flask.session:
		messages = flask.session["messages"]
		
	cgpt = CGPT(messages)

	if flask.request.method == "POST":
		if "newinput" in flask.request.form:
			cgpt.clear()

			i = 1
			while True:
				context_name = "context" + str(i)
				if context_name not in flask.request.form:
					break

				content = flask.request.form.get(context_name)
				cgpt.add(content)
				i += 1

			cgpt.chat()
			flask.session["messages"] = cgpt.messages

		elif "clear" in flask.request.form:
			cgpt.set_default()

		elif "presets_select" in flask.request.form:
			preset_name = flask.request.form["presets_select"]
			cgpt.apply_preset(preset_name)

	return flask.render_template("index.html", messages=cgpt.messages, role_choices=cgpt.ROLES, preset_names=cgpt.get_preset_names())
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	default_port = 8456
	parser.add_argument("-p", "--port",
		help=f"port number. defaults to {default_port}.",
		default=default_port
	)
	args = parser.parse_args()

	app.run(host="0.0.0.0", port=args.port)