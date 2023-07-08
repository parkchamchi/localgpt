import openai

import json
import os

openai.api_key_path = "oai_key.txt"
PRESETS_JSON = "presets.json"

class CGPT:
	ROLES = ["system", "assitant", "user"]
	DEFAULT_MSGS = [
		("system", "You are a helpful assistant."),
		("assistant", "Hi! Ask me anything."),
	]

	def __init__(self, messages=None):
		self.messages = messages if messages is not None else self.DEFAULT_MSGS

		self.presets = {}
		if os.path.exists(PRESETS_JSON):
			with open(PRESETS_JSON, "rt", encoding="utf-8") as fin:
				self.presets = json.load(fin)

	def clear(self):
		self.messages = []

	def set_default(self):
		self.messages = self.DEFAULT_MSGS

	def add(self, msg):
		len_msgs = len(self.messages)
		if len_msgs == 0:
			role = "system"
		elif len_msgs % 2 == 1: #odd
			role = "assistant"
		else:
			role = "user"

		self.messages += [(role, msg)]

	def chat(self):
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=[
				{"role": role, "content": content}
				for role, content
				in self.messages
			]
		)
		assistant_msg = response["choices"][0]["message"]["content"]
		print("Got.")

		self.messages += [("assistant", assistant_msg)]

	def get_preset_names(self):
		return self.presets.keys()
	
	def apply_preset(self, preset_name):
		self.clear()
		for msg in self.presets[preset_name]:
			self.add('\n'.join(msg))