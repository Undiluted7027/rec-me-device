# Enhanced settings for multi-spider project
BOT_NAME = "gsmarena"

# Spider-specific configuration
SPIDER_SETTINGS = {
    'gsmarena': {
        'USER_AGENT' : 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 1.5,
        'FEED_URI': 'gsmarena_output.json'
    },
    'deviceSpecs': {
        'USER_AGENT' : 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'DOWNLOAD_DELAY': 2.0,
        'FEED_URI': 'devicespecs_output.json'
    }
}

# For rotation:
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'gsmarena.middlewares.AdvancedAntiBotMiddleware': 543,
}

CUSTOM_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

SPIDER_MIDDLEWARES = {
    'gsmarena.middlewares.UniversalMiddleware': 500,
}

# Core settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
DOWNLOAD_MAXSIZE = 15 * 1024 * 1024  # Match Googlebot's 15MB limit
DOWNLOAD_TIMEOUT = 180
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Compliance settings
ROBOTSTXT_OBEY = True
HTTPCACHE_ENABLED = True
COOKIES_ENABLED = False

# Extension configuration
EXTENSIONS = {
    'scrapy.extensions.throttle.AutoThrottle': 500,
}

# Project structure
SPIDER_MODULES = ["gsmarena.spiders"]
NEWSPIDER_MODULE = "gsmarena.spiders"
ITEM_PIPELINES = {
    'gsmarena.pipelines.GsmarenaPipeline': 300,
    'gsmarena.pipelines.DeviceSpecsPipeline': 400,
}
