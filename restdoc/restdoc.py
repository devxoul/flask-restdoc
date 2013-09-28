# -*- coding: utf-8 -*-

from flask import current_app
import json

_errors = None

# Based on: RFC2616 (http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)
_status_codes = {
	100: 'Continue',
	101: 'Switching Protocols',
	200: 'OK',
	201: 'Created',
	202: 'Accepted',
	203: 'Non-Authoritative Information',
	204: 'No Content',
	205: 'Reset Content',
	206: 'Partial Content',
	300: 'Multiple Choices',
	301: 'Moved Permanently',
	302: 'Found',
	303: 'See Other',
	304: 'Not Modified',
	305: 'Use Proxy',
	# 306 is not used.
	307: 'Temporary Redirect',
	400: 'Bad Parameter',
	401: 'Unauthorized',
	402: 'Payment Required',
	403: 'Forbidden',
	404: 'Not Found',
	405: 'Method Not Allowed',
	406: 'Not Acceptable',
	407: 'Proxy Authentication Required',
	408: 'Request Timeout',
	409: 'Conflict',
	401: 'Gone',
	411: 'Length Required',
	412: 'Precondition Failed',
	413: 'Request Entity Too Large',
	414: 'Request-URI Too Long',
	415: 'Unsupported Media Type',
	416: 'Requested Range Not Satisfiable',
	417: 'Expectation Failed'
}

class RestAPI():
	method = None
	rule = None
	endpoint = None
	description = None
	params = None
	status = 0
	sample_response = None
	errors = None

	def __init__(self, endpoint, **options):
		self.endpoint = endpoint
		self.description = options.get('description') or None
		self.params = options.get('params') or None
		self.status = options.get('status') or 200
		self.sample_response = options.get('sample_response') or None
		self.errors = options.get('errors') or None

	def __repr__(self):
		return '<RestAPI %s %s>' % (self.method, self.rule)

	def doc(self):
		doc = '### `%s` %s\r\n\r\n' % (self.method, self.rule)

		if self.description:
			doc += '###### Description\r\n\r\n'
			doc += '%s\r\n\r\n\r\n' % (self.description)

		if self.params and len(self.params):
			doc += '###### Requset\r\n\r\n'
			doc += '| Name | Required | Description |\r\n'
			doc += '|---|---|---|\r\n'
			for param in self.params:
				doc += '| **%s** | *%s* | %s |\r\n' % (param[0], 'Required' if param[1] else 'Optional', param[2] if len(param) > 2 else '')
			doc += '\r\n\r\n'

		if self.status:
			doc += '###### HTTP Status\r\n\r\n'
			doc += '%d\r\n\r\n\r\n' % (self.status)

		if self.sample_response:
			doc += '###### Sample JSON Response\r\n\r\n'
			doc += '```\r\n'
			doc += '%s\r\n' % json.dumps(self.sample_response, indent=4)
			doc += '```\r\n\r\n\r\n'

		if self.errors and len(self.errors):
			global _errors	
			doc += '###### Errors\r\n\r\n'
			doc += '| Status | Code | Message |\r\n'
			doc += '|---|---|---|\r\n'
			for error_code in self.errors:
				errors = filter(lambda e : e[1] == error_code, _errors)
				if not errors:
					print '[WARNING] Error code not defined : %d' % error_code
					continue
				error = errors[0]
				doc += '| %d | %d | %s |\r\n' % (error[0], error_code, error[2].replace('_', '\_'))
			doc += '\r\n\r\n'

		doc += '<br /><br />\r\n\r\n\r\n'
		return doc


class Restdoc():
	app = None
	apis = dict()
	errors = None

	def __call__(self, app):
		if app: self.init_app(app)

	def init_app(self, app):
		self.app = app

	def set_errors(self, errors):
		global _errors
		_errors = errors


	# options : description, params, status, sample_response, errors
	def api(self, blueprint, **options):
		def decorator(f):
			endpoint = '%s.%s' % (blueprint.name, f.__name__)
			api = RestAPI(endpoint, **options)
			self.apis[endpoint] = api
		return decorator

	def generate(self):
		content = '# REST API Documentation\r\n\r\n<br />\r\n\r\n'

		content += '## 1. Definitions\r\n\r\n'
		content += '###### HTTP Status\r\n\r\n'
		content += '| Code | Status |\r\n'
		content += '|---|---|\r\n'

		status_codes = []
		global _errors
		if _errors and len(_errors):
			for error in _errors:
				if not status_codes.__contains__(error[0]):
					status_codes.append(error[0])

			for status_code in status_codes:
				content += '| %d | %s |\r\n' % (status_code, _status_codes[status_code])

			content += '\r\n\r\n###### Errors\r\n\r\n'
			content += '| Status | Code | Message |\r\n'
			content += '|---|---|---|\r\n'
			for error in _errors:
				content += '| %d | %d | %s |\r\n' % (error[0], error[1], error[2].replace('_', '\_'))

		content += '\r\n\r\n<br /><br />\r\n\r\n\r\n## 2. API\r\n\r\n'

		with self.app.app_context():
			for rule in current_app.url_map.iter_rules():
				api = self.apis.get(rule.endpoint)
				if not api: continue

				api.method = list(rule.methods - set(['HEAD', 'OPTIONS']))[0]
				api.rule = rule.rule.replace('<', '{').replace('>', '}').replace('int:', '')
				content += api.doc()

		doc = open(self.app.config['RESTDOC_OUTPUT'], 'w')
		doc.write(content)
		doc.close()
