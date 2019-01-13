import datetime as dt

from twilio.rest import TwilioRestClient
from tornado import gen, concurrent
from . import AbstractHandler, TEMPLATES, LOGGER

class SMSHandler(AbstractHandler):

    name = 'sms'

    # Default options
    defaults = {
    'account_sid': None,
    'auth_token'  : None,
    'sms_from' : None,    
    'to' : None,
   }

    def init_handler(self):
        """ Check self options. """
        assert self.options.get('account_sid') and self.options.get('auth_token'), "Invalid options"
        assert self.options.get('to'), 'Recepients list is empty. SMS disabled.'
        if not isinstance(self.options['to'], (list, tuple)):
            self.options['to'] = [self.options['to']]

    @gen.coroutine
    def notify(self, level, alert, value, target=None, ntype=None, rule=None):
    sms_from = self.options['sms_from']
    tos = self.options['to']

    if target.split('.')[0] == 'pgp':
            hostname = target.split('.')[2]
            ip = '.'.join(target.split('.')[3].split('-')[1:])
            item = '.'.join(target.split('.')[-2:])
            body = "%s, %s, %s, %s, %s" % (level, hostname, ip, item, value)
        #LOGGER.info('level:%s, alert:%s, value:%s, target:%s, ntype:%s, rule:%s', level, alert, value, target, ntype, rule)
    elif target.split('.')[0] == 'cloudwatch':
        region = target.split('.')[3]
        project = target.split('.')[4]
        item = target.split('.')[5]
        body = "%s, %s, %s, %s, %s" % (level, region, project, item, value)
    else:
        body = "%s" % target



    client = TwilioRestClient(self.options['account_sid'], self.options['auth_token'])

        for to in tos:
            message = client.messages.create(to=to, sms_from=sms_from, body=body)        
