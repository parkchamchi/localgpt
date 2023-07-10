from cgpt import CGPT

import flask
from flask_wtf import CSRFProtect

import argparse

app = flask.Flask(__name__)
with open("secret_key.txt", "rt") as fin:
	secret_key = fin.read()
app.config["SECRET_KEY"] = secret_key

csrf = CSRFProtect(app)

@app.route("/", methods=["GET", "POST"])
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

	app.run(port=args.port)