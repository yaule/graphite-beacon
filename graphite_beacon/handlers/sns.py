from holly.courier import SNSCourier
from tornado import gen, concurrent
from . import AbstractHandler, TEMPLATES, LOGGER

class SNSHandler(AbstractHandler):

    name = 'sns'

    # Default options
    defaults = {
	'topic': None,
	'sns_region': None,
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
   }

    def init_handler(self):
        """ Check self options. """
        assert self.options.get('topic') and self.options.get('sns_region') and self.options.get('aws_access_key_id') and self.options.get('aws_secret_access_key'), "Invalid options"

    @gen.coroutine
    def notify(self, level, alert, value, target=None, ntype=None, rule=None, smtp=None, call=None):
        topic = self.options['topic']
        sns_region = self.options['sns_region']
        aws_access_key_id = self.options['aws_access_key_id']
        aws_secret_access_key = self.options['aws_secret_access_key']
        check = alert.name
        if target.split('.')[0] == 'pgp' or target.split('.')[0] == 'pgp-game' or target.split('.')[0] == 'aliasByNode(pgp' or target.split('.')[0] == 'averageSeries(pgp' or target.split('.')[0] == 'minSeries(pgp':
            target_region = target.split('.')[1]
        elif target.split('.')[0] == 'cloudwatch' or target.split('.')[0] == 'asPercent(cloudwatch':
            target_region = target.split('.')[3]
        else:
            target_region = 'us-west-1'
        courier = SNSCourier(topic=topic, region=sns_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key) 
        courier.send(app='beacon',region=target_region,check=check,level=level)
