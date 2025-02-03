import scrapy


class BrandItem(scrapy.Item):
    name = scrapy.Field()
    device_count = scrapy.Field()
    url = scrapy.Field()


class DeviceItem(scrapy.Item):
    brand = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    specifications = scrapy.Field()
