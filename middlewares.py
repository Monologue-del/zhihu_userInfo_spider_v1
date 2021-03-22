# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
import random

class ProxyMiddleware(object):
    def __init__(self, ip):
        self.ip = ip

    @classmethod
    def from_crawler(cls, crawler):
        return cls(ip=crawler.settings.get('PROXIES'))

    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://222.132.197.172:4578'
        # ip = random.choice(self.ip)
        # request.meta['proxy'] = ip

    def process_exception(self, request, exception, spider):
        print('ip过期')
        # ip = random.choice(self.ip)
        # request.meta['proxy'] = ip

        return request
