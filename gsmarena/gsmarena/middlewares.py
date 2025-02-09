# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from urllib.parse import urlparse
import random
import logging

# Custom User Agents for device specifications site
DEVICESPECS_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36"
]

class GsmarenaSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class GsmarenaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DeviceSpecsMiddleware:
    """Core middleware for DeviceSpecs spider functionality"""
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_request(self, request, spider):
        """Handle DeviceSpecs-specific request modifications"""
        if spider.name == 'devicespecs':
            # Rotate user agents for each request
            request.headers['User-Agent'] = random.choice(DEVICESPECS_USER_AGENTS)
            
            # Set referer header for better request acceptance
            if 'referer' not in request.meta:
                request.headers['Referer'] = 'https://www.devicespecifications.com/'
            
            # Add cache-busting parameter
            parsed = urlparse(request.url)
            if not parsed.query:
                request = request.replace(url=request.url + '?cachebust=' + str(random.randint(1000,9999)))
            
            spider.logger.debug(f"Processed request for {request.url}")
        
        return None

    def process_response(self, request, response, spider):
        """Handle DeviceSpecs-specific response validation"""
        if spider.name == 'devicespecs':
            if response.status == 403:
                spider.logger.warning(f"Forbidden response from {response.url}")
                return request.replace(dont_filter=True)
            
            if "bot-detected" in response.text.lower():
                spider.logger.error("Bot detection triggered")
                return request.replace(dont_filter=True)
            
            # Check HTML structure validity
            if not response.css('div.specs-category'):
                spider.logger.warning("Missing specifications container in response")
                return request.replace(dont_filter=True)
        
        return response
    
    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class CustomRetryMiddleware:
    """Enhanced retry logic for both spiders"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.max_retry = crawler.settings.getint('RETRY_TIMES', 3)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if spider.name == 'devicespecs':
            retries = request.meta.get('retry_times', 0) + 1
            if response.status in [429, 503]:
                spider.logger.info(f"Retrying {request.url} (attempt {retries}/{self.max_retry})")
                return self._retry(request, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if spider.name in ['gsmarena', 'devicespecs']:
            return self._retry(request, spider)

    def _retry(self, request, spider):
        retries = request.meta.get('retry_times', 0)
        if retries < self.max_retry:
            return request.copy(meta={
                **request.meta,
                'retry_times': retries + 1,
                'dont_obey_robotstxt': True
            })

class UniversalMiddleware:
    """Shared middleware for both spiders"""
    
    def process_spider_input(self, response, spider):
        # Common validation for all spiders
        if response.status != 200:
            spider.logger.error(f"Non-200 response: {response.status}")
        return None

    def process_spider_output(self, response, result, spider):
        # Add timestamp to all yielded items
        for item in result:
            if is_item(item):
                adapter = ItemAdapter(item)
                adapter['crawl_timestamp'] = self.crawler.stats.get_value('start_time')
            yield item


class AdvancedAntiBotMiddleware:
    def process_request(self, request, spider):
        request.headers.update({
            'Sec-CH-UA': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-CH-UA-Platform-Version': '"15.0.0"',
            'Sec-CH-UA-Full-Version-List': '"Chromium";v="122.0.6261.95", "Not(A:Brand";v="24.0.0.0", "Microsoft Edge";v="122.0.2365.92"'
        })