# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GsmarenaScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BrandItem(scrapy.Item):
    brand_name = scrapy.Field()
    brand_url = scrapy.Field()
    total_devices = scrapy.Field()

class DeviceItem(scrapy.Item):
    brand_name = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    description = scrapy.Field()
    specifications = scrapy.Field()
