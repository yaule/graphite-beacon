# -*- coding: utf-8 -*-
from . import AbstractHandler, TEMPLATES, LOGGER
from tornado import gen, concurrent
import requests
import time
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')


class WechatHandler(AbstractHandler):

    ACCESS_TOKEN_GROUP = (None, time.time())

    name = 'wechat'

    # Default options
    defaults = {
        'qy_corpid': None,
        'qy_secret': None,
        'to_user': None,
        'to_party': None
    }

    def init_handler(self):
        """ Check self options. """
        assert self.options.get('qy_corpid') and self.options.get(
            'qy_secret'), "Invalid options"

    def get_access_token(self):
        # self.ACCESS_TOKEN_GROUP
        ts = time.time()
        if self.ACCESS_TOKEN_GROUP[1] < ts:
            url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secrect}'
            url = url.format(
                corpid=self.options['qy_corpid'], secrect=self.options['qy_secret'])
            result = requests.get(url).json()
            self.ACCESS_TOKEN_GROUP = (
                result["access_token"], ts + result["expires_in"])
        return self.ACCESS_TOKEN_GROUP[0]

    @gen.coroutine
    def notify(self, level, alert, value, target=None, ntype=None, rule=None, smtp=None, call=None):
        # def notify(self, text, appid=4, touser=None, toparty=None):
        txt_tmpl = TEMPLATES[ntype]['text']
        ctx = dict(
            reactor=self.reactor, alert=alert, value=value, level=level, target=target, 
            rule=rule, **self.options)
        text = txt_tmpl.generate(**ctx)
        if type(text) is unicode:
            text = text.encode('utf8')
        if not touser:
            touser = []
        if not toparty:
            toparty = ['2']
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        url = url.format(access_token=self.get_access_token())
        data = {"touser": "|".join(touser),
                "toparty": "|".join(toparty),
                "msgtype": "text",
                "agentid": str(appid),
                "text": {"content": text},
                "safe": "0",
                }
        result = requests.post(url, data=json.dumps(data, ensure_ascii=False))
        return result
