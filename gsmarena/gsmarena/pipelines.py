class GsmarenaPipeline:
    def process_item(self, item, spider):
        if spider.name == 'gsmarena':
            # GSM-specific processing
            return item
        return item

class DeviceSpecsPipeline:
    def process_item(self, item, spider):
        if spider.name == 'devicespecs':
            # DeviceSpecs-specific processing
            return item
