# settings.py
BOT_NAME = "gsmarena"
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
FEED_FORMAT = "json"
FEED_URI = "output.json"

SPIDER_MODULES = ["gsmarena.spiders"]
NEWSPIDER_MODULE = "gsmarena.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "scrapingcourse_scraper (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
