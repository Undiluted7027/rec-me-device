import json, logging, random, re, time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import scrapy
from scrapy.http import response
from scrapy import signals
from scrapy.exceptions import CloseSpider

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespaces and replacing HTML entities"""
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

class GsmarenaSpider(scrapy.Spider):
    name = "gsmarena"
    allowed_domains = ["gsmarena.com"]
    # Entry point for brands
    start_urls = ["https://www.gsmarena.com/makers.php3"]

    # Settings that can be modified
    MAX_BRANDS = None # Limit number of brands for testing
    MAX_DEVICES_PER_BRAND = None # Limit number of devices per brand for testing
    DELAY_RANGE = (2, 5) # Random delay between requests in seconds

    # Track data across the spider
    brands_data = {}
    total_requests = 0

    def __init__(self, *args, **kwargs):
        super(GsmarenaSpider, self).__init__(*args, **kwargs)
        self.logger.info("Initializing GSMArena Spider")

        # Create output directory
        self.output_dir = Path("gsmarena_data")
        self.output_dir.mkdir(exist_ok=True)

        # Initialize counter to track requests
        self.request_count = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GsmarenaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, spider):
        """Save all brand data when spider closes"""
        self.logger.info(f"Spider closed. Total requests made: {self.total_requests}")

        # Save a summary of all brands
        brands_summary = []
        for brand_name, brand_data in self.brands_data.items():
            brands_summary.append({
                "brand_name": brand_name,
                "device_count": brand_data.get("total_devices", 0),
                "devices_scraped": len(brand_data.get("devices", [])),
                "brand_url": brand_data.get("brand_url", "")
            })
        with open(self.output_dir / "brands_summary.json", "w", encoding="utf-8") as f:
            json.dump(brands_summary, f, indent=4, ensure_ascii=False)
    
    def start_requests(self):
        """Start by scraping the brands page"""
        self.logger.info("Starting to scrape GSMArena brands")

        for url in self.start_urls:
            yield scrapy.Request(
                url= url,
                callback=self.parse_brands
            )
    
    def parse_brands(self, response):
        """Parse the brands page and extract brand info"""
        self.total_requests += 1
        self.logger.info(f"Parsing brands from {response.url}")

        # Find all brand blocks
        brand_blocks = response.css("div.st-text a")
        self.logger.info(f"Found {len(brand_blocks)} brands")

        brands_processed = 0

        for brand in brand_blocks:
            # Extract brand information
            brand_name = clean_text(brand.xpath('./text()').get())
            brand_url = brand.xpath('./@href').get()
            
            # Extract device count from the format "xx devices"
            device_count_text = brand.xpath('.//span/text()').get("0 devices")
            device_count = int(re.search(r'(\d+)', device_count_text).group(1)) if re.search(r'(\d+)', device_count_text) else 0
            
            # Store brand information
            self.brands_data[brand_name] = {
                "brand_name": brand_name,
                "brand_url": brand_url,
                "total_devices": device_count,
                "devices": []
            }

            self.logger.info(f"Brand: {brand_name}, URL: {brand_url}, Device Count: {device_count}")

            # Sleep to respect rate limits
            time.sleep(random.uniform(*self.DELAY_RANGE))
            
            # Request the brand page to get devices
            yield response.follow(
                url = brand_url,
                callback = self.parse_brand_devices,
                meta={
                    "brand_name": brand_name,
                    "page_num": 1,
                }
            )
            brands_processed += 1
            # If testing, limit the number of brands
            if self.settings.getint('MAX_BRANDS') and brands_processed >= self.settings.getint('MAX_BRANDS'):
                self.logger.info(f"Reached maximum brands limit ({self.settings.getint('MAX_BRANDS')})")
                break
    
    def parse_brand_devices(self, response):
        """Parse a brand page and extract device information"""
        self.total_requests += 1
        brand_name = response.meta.get("brand_name")
        page_num = response.meta.get("page_num", 1)

        self.logger.info(f"Parsing devices for {brand_name} - Page {page_num}")

        # Extract devices from the page
        devices = response.css("div.makers ul li")
        self.logger.info(f"Found {len(devices)} devices on page {page_num}")

        devices_processed = 0

        for device in devices:
            device_name = clean_text(device.css("strong span::text").get())
            device_url = device.css("a::attr(href)").get()
            image_url = device.css("img::attr(src)").get("")
            description = clean_text(device.css("img::attr(title)").get(""))
            device_info = {
                "name": device_name,
                "url": device_url,
                "image_url": image_url,
                "description": description,
                "specifications": {}
            }
            
            # Add device to brand data
            if brand_name in self.brands_data:
                self.brands_data[brand_name]['devices'].append(device_info)

            # Sleep to respect rate limits
            time.sleep(random.uniform(*self.DELAY_RANGE))

            # Request the device page to get specifications
            yield response.follow(
                url=device_url,
                callback=self.parse_device_specs,
                
                meta={
                    "brand_name": brand_name,
                    "device_name": device_name,
                }
            )
            devices_processed += 1

            # If testing, limit the number of devices per brand
            if self.settings.getint('MAX_DEVICES_PER_BRAND') and devices_processed >= self.settings.getint('MAX_DEVICES_PER_BRAND'):
                self.logger.info(f"Reached maximum devices per brand limit ({self.settings.getint('MAX_DEVICES_PER_BRAND')})")
                break
            
            # Check for next page
            next_page = response.css('div.nav-pages a[title="Next page"]::attr(href)').get()
            if next_page and (not self.settings.getint('MAX_DEVICES_PER_BRAND') or devices_processed < self.settings.getint('MAX_DEVICES_PER_BRAND')):
                next_page_url = response.urljoin(next_page)
                self.logger.info(f"Found next page for {brand_name}: {next_page_url}")

                # Sleep to respect rate limits
                time.sleep(random.uniform(*self.DELAY_RANGE))

                yield response.follow(
                    url=next_page_url,
                    callback=self.parse_brand_devices,
                    
                    meta={
                        "brand_name": brand_name,
                        "page_num": page_num + 1
                    }
                )
            else:
                self.logger.info(f"No more pages for {brand_name}, saving data...")

                # Save brand data to a file
                self._save_brand_data(brand_name)
    

    def parse_device_specs(self, response):
        """Parse device specification page"""
        self.total_requests += 1
        brand_name = response.meta.get("brand_name")
        device_name = response.meta.get("device_name")

        self.logger.info(f"Parsing specifications for {device_name}")

        # Find the device in the brand data
        device = None
        if brand_name in self.brands_data:
            for d in self.brands_data[brand_name]["devices"]:
                if d["name"] == device_name:
                    device = d
                    break
        
        if not device:
            self.logger.warning(f"Device {device_name} not found in brand {brand_name} data")
            return
        
        # Extract popularity of device 'xx hits'
        popularity_text = clean_text(response.css('li.help-popularity span::text').get("0 hits"))
        popularity = int(re.sub(r'\D', '', popularity_text)) if popularity_text else 0

        # Extract specifications by category
        spec_tables = response.css('div#specs-list table')

        specifications = {
            "popularity": popularity
        }

        for table in spec_tables:
            category = clean_text(table.css("th *::text").get(""))

            rows = table.css("tr")
            last_key = None
            
            for row in rows:
                spec_key = clean_text(row.css('td.ttl *::text').get(""))
                spec_value = clean_text(row.css('td.nfo *::text').get(""))

                # Additional processing to handle multiple values in one cell
                if spec_key:
                    full_key = f"{category} - {spec_key}"
                    specifications[full_key] = spec_value if spec_value else "N/A"
                    last_key = full_key
                elif spec_value and last_key:
                    # Append to the last key if there's no new key but there is a value
                    specifications[last_key] = specifications.get(last_key, "") + " | " + spec_value

        # Update device specifications
        device['specifications'] = specifications

        # Check if we've collected all devices for this brand
        if brand_name in self.brands_data:
            all_specs_collected = True
            for d in self.brands_data[brand_name]["devices"]:
                if not d.get("specifications"):
                    all_specs_collected = False
                    break
            
            if all_specs_collected:
                self.logger.info(f"All specifications collected for {brand_name}, saving data...")
                self._save_brand_data(brand_name)

    def _save_brand_data(self, brand_name):
        """Save brand data to a JSON file"""
        if brand_name not in self.brands_data:
            self.logger.warning(f"No data found for brand {brand_name}")
            return
        
        brand_data = self.brands_data[brand_name]

        # Create clean filename
        filename = re.sub(r'[^\w\s-]', '', brand_name).strip().lower()
        filename = re.sub(r'[-\s]+', '-', filename)

        filepath = self.output_dir / f"{filename}.json"
        
        self.logger.info(f"Saving data for {brand_name} to {filepath}")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(brand_data, f, indent=4, ensure_ascii=False)



    