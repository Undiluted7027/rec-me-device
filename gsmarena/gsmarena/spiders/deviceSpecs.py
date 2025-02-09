import scrapy


class DevicespecsSpider(scrapy.Spider):
    name = "deviceSpecs"
    allowed_domains = ["www.devicespecifications.com"]
    start_urls = ["https://www.devicespecifications.com/"]

    def parse(self, response):
        pass