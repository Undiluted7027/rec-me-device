# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import request, response
from scrapy.exceptions import NotConfigured

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from typing import List, Optional
from urllib.parse import urlparse
from collections import defaultdict
import random, logging, random, time

class RateLimitMiddleware:
    """Middleware to implement adaptice rate limiting based on domain response"""

    def __init__(self, delay_range=(2, 5), max_requests_per_domain=50, backoff_factor=2, max_delay=120):
        self.delay_range = delay_range
        self.max_requests_per_domain = max_requests_per_domain
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)

        # Track requests per domain
        self.domain_requests = defaultdict(int)
        # Track 429 or other responses per domain
        self.domain_errors = defaultdict(int)
        # Track current delay per domain
        self.domain_delays = defaultdict(lambda: delay_range[0])
        # Last request timestamp per domain
        self.last_request_time = defaultdict(float)

    @classmethod
    def from_crawler(cls, crawler):
        # Get settings from crawler
        delay_range = crawler.settings.getlist('RATE_LIMIT_DELAY_RANGE', (2, 5))
        max_requests = crawler.settings.getint('RATE_LIMIT_MAX_REQUESTS', 50)
        backoff_factor = crawler.settings.getfloat('RATE_LIMIT_BACKOFF_FACTOR', 2.0)
        max_delay = crawler.settings.getint('RATE_LIMIT_MAX_DELAY', 120)
        
        # Create middleware instance
        middleware = cls(delay_range, max_requests, backoff_factor, max_delay)
        
        # Connect signals
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        
        return middleware
    
    def spider_opened(self, spider):
        self.logger.info("Rate limit middleware enabled")
    
    def process_request(self, request, spider):
        """Process each request and delay if needed"""
        domain = self._get_domain(request.url)
        current_time = time.time()

        # Increment request counter for this domain
        self.domain_requests[domain] += 1

        # Calculate delay needed
        current_delay = self.domain_delays[domain]
        time_since_last_request = current_time - self.last_request_time[domain]

        # If we need to delay more
        if time_since_last_request < current_delay:
            delay_needed = current_delay - time_since_last_request
            self.logger.debug(f"Delaying request to {domain} by {delay_needed:.2f}s")
            time.sleep(delay_needed)
        
        # Update last request time
        self.last_request_time[domain] = time.time()

        # If we've made many requests to this domain, add a small random delay
        if self.domain_requests[domain] > self.max_requests_per_domain:
            random_delay = random.uniform(*self.delay_range)
            self.logger.debug(f"Adding random delay of {random_delay:.2f}s for {domain}")
            time.sleep(random_delay)

    def process_response(self, request, response, spider):
        """Process response and adjust delays if needed"""
        domain = self._get_domain(request.url)

        # Check for 429 (Too Many Requests) or other 4xx/5xx errors
        if response.status in [429] or (response.status >= 400 and response.status < 600):
            self.domain_errors[domain] += 1

            # Increase delay for this domain
            current_delay = self.domain_delays[domain]
            new_delay = min(current_delay * self.backoff_factor, self.max_delay)
            self.domain_delays[domain] = new_delay

            self.logger.warning(
                 f"Received status {response.status} from {domain}. "
                f"Increasing delay to {new_delay:.2f}s. "
                f"Error count: {self.domain_errors[domain]}"
            )

            # If we get too many errors, we might want to pause for a while
            if self.domain_errors[domain] > 5:
                self.logger.warning(f"Too many errors from {domain}, pausing for 60s")
                time.sleep(60)
                self.domain_errors[domain] = 0  # Reset error count
        
        return response
    
    def _get_domain(self, url):
        """Extract domain from URL"""
        return urlparse(url).netloc
    

class UserAgentMiddleware:
    """Middleware to rotate user agents"""
    def __init__(self, user_agents):
        self.user_agents = user_agents
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.getlist('USER_AGENTS', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
        ])

        if not user_agents:
            raise NotConfigured("USER_AGENTS setting is empty or not set")
        
        return cls(user_agents)
    
    def process_request(self, request, spider):
        """Set random user agent for each request"""
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        self.logger.debug(f"Using User-Agent: {user_agent}")


class GsmarenaScraperSpiderMiddleware:
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


class GsmarenaScraperDownloaderMiddleware:
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


class RotateUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        # Randomly select a User-Agent from the list
        user_agent = random.choice(self.user_agents)
        if user_agent:
            request.headers['User-Agent'] = user_agent    