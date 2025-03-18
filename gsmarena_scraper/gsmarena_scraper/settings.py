# Scrapy settings for gsmarena_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "gsmarena_scraper"

SPIDER_MODULES = ["gsmarena_scraper.spiders"]
NEWSPIDER_MODULE = "gsmarena_scraper.spiders"

ROBOTSTXT_OBEY = False  # Ignore robots.txt rules (ensure compliance with legal terms)

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 2 # Limit concurrent requests to avoid overloading
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Enable and configure the AutoThrottle extension for automatic request throttling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable logging
LOG_LEVEL = "INFO"

# Configure item pipelines
ITEM_PIPELINES = {
   "gsmarena_scraper.pipelines.GsmarenaScraperPipeline": 300,
}

# Set download timeout
DOWNLOAD_DELAY = 1  # Base delay
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 180

# Delay Settings
RATE_LIMIT_DELAY_RANGE = (2, 5)
RATE_LIMIT_MAX_REQUESTS = 50
RATE_LIMIT_BACKOFF_FACTOR = 2
RATE_LIMIT_MAX_DELAY = 120

# Retry/Error Settings
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 429]

# Add Downloader Middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'gsmarena_scraper.middlewares.UserAgentMiddleware': 400,
    'gsmarena_scraper.middlewares.RateLimitMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}

# Disable cookies for better performance
COOKIES_ENABLED = False

# Use a custom user agent list
USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.', 'Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3']

# Enable memory debugging
MEMDEBUG_ENABLED = True

# Enable disk cache to reduce network requests
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 24 * 60 * 60  # 24 hours
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [400, 403, 404, 429, 500, 502, 503, 504]

# Output Feed
FEEDS = {
    'gsmarena_data/brands_data.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 4,
    },
}

# Custom variables for testing
MAX_BRANDS = None
MAX_DEVICES_PER_BRAND = None