# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json, logging
from pathlib import Path
from itemadapter import ItemAdapter


class GsmarenaScraperPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.brands_data = {}
        self.output_dir = Path("gsmarena_data")
        self.output_dir.mkdir(exist_ok=True)

    def process_item(self, item, spider):
        return item
    
    def close_spider(self, spider):
        self.logger.info("Pipeline closing, ensuring all data is saved")
