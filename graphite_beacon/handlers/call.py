import datetime as dt

from twilio.rest import TwilioRestClient
from tornado import gen, concurrent
from . import AbstractHandler, TEMPLATES, LOGGER

class CallHandler(AbstractHandler):

    name = 'call'

    # Default options
    defaults = {
	'account_sid': None,
	'auth_token'  : None,
	'from_' : None,	
	'to' : None,
   }

    def init_handler(self):
        """ Check self options. """
        assert self.options.get('account_sid') and self.options.get('auth_token'), "Invalid options"
        assert self.options.get('to'), 'Recepients list is empty. Call disabled.'
        if not isinstance(self.options['to'], (list, tuple)):
            self.options['to'] = [self.options['to']]

    @gen.coroutine
    def notify(self, level, alert, value, target=None, ntype=None, rule=None, smtp=None, call=None):
        from_ = self.options['from_']
        tos = set(self.options['to'] + call)
        client = TwilioRestClient(self.options['account_sid'], self.options['auth_token'])
        for to in tos:
            call = client.calls.create(url="http://demo.twilio.com/docs/voice.xml", to=to, from_=from_ )        
