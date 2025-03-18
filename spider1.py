import scrapy
import logging

class GsmarenaSpider(scrapy.Spider):
    name = "gsmarena"
    allowed_domains = ["gsmarena.com"]
    # Entry point for brands
    start_urls = ["https://gsmarena.com/makers.php3"]
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure a log filter to show only request logs
        class RequestLogFilter(logging.Filter):
            def filter(self, record):
                return "Scrapy" in record.name or "request" in record.getMessage().lower()
        # Attach the filter to Scrapy's logger
        for handler in logging.getLogger('scrapy').handlers:
            handler.addFilter(RequestLogFilter)

        self.base_link = "https://www.gsmarena.com/"
        self.brand_count = 0
        self.total_brands = 0
        self.device_count = {}
        self.total_devices = {}

        self.brands = {}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        # Strict check to ensure we are not parsing a mobile site
        if response.url.startswith("https://m.gsmarena.com"):
            self.logger.info(f"Skipping mobile site: {response.url}")
            return
        
        # Extract brands
        brand_links = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "st-text", " " ))]//a')
        self.total_brands = len(brand_links)
        for brand in brand_links:
            url = brand.xpath('./@href').get()
            brand_name = brand.xpath('./text()').get().strip() # Extract brand name before <br>
            total_devices_text = brand.xpath('.//span/text()').get()

            # Extract only number of devices from text like "100 devices"
            self.total_devices[url] = int(total_devices_text.split()[0]) if total_devices_text else 0

            self.brand_count += 1
            self.device_count[url] = 0 # Track devices per brand
            
            self.logger.debug(f"Scraping brand {self.brand_count}/{self.total_brands}: {brand_name}")

            self.brands[brand_name] = {
                'brand_name': brand_name,
                'device_num': self.total_devices[url],
                'devices': []
            }

            yield response.follow(url, self.parse_brand, meta={'brand_url': url, 'brand_name': brand_name})

    def parse_brand(self, response):
        brand_url = response.meta['brand_url']
        brand_name = response.meta['brand_name']
        self.brands[brand_name]['brand_link'] = response.request.meta['redirect_urls'][0] if response.request.meta.get('redirect_urls') else response.request.url
        
        # Extract phone URLs from the brand page
        phone_urls = response.xpath('//*[(@id = "review-body")]//a/@href').getall()
        self.total_devices[brand_url] = len(phone_urls) # Get total devices for brand
        for url in phone_urls:
            self.device_count[brand_url] += 1
            percent = (self.device_count[brand_url] / self.total_devices[brand_url]) * 100 if self.total_devices[brand_url] else 0
            self.logger.debug(f"Scraping Device {self.device_count[brand_url]}/{self.total_devices[brand_url]} ({percent:.2f}%) from {brand_name}")
            yield response.follow(url, self.parse_phone, meta={'brand_name': brand_name})
        
        # Handling pagination
        next_page = response.xpath('//div[@class="nav-pages"]//a[@title="Next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_brand, meta={'brand_url': brand_url, 'brand_name': brand_name})
    
    def parse_phone(self, response):
        brand_name = response.meta['brand_name']
        # Extract phone specifications
        specs = {
            'name': response.xpath('//h1[@class="specs-phone-name-title"]/text()').get(),'image': response.xpath('//div[@class="specs-photo-main"]//img/@src').get(), 
            'device_link': response.request.meta['redirect_urls'][0] if response.request.meta.get('redirect_urls') else response.request.url
        }

        spec_tables = response.xpath("//div[@id='specs-list']//table")
        # Extract specifications table (key-value pairs)
        for table in spec_tables:
            category = table.xpath('.//th/text()').get(default="").replace("\xa0", " ").strip()
            category = " ".join(category.split())
            prevKey = ""
            for spec in table.xpath('.//tr'):
                key = spec.xpath('//td[@class="ttl"]/a/text()').get(default="").replace("\xa0", " ").strip()
                key = " ".join(key.split())
                value = spec.xpath('//td[@class="nfo"]//text()').get(default="").replace("\xa0", " ").strip()
                value = " ".join(value.split())
                if value == "":
                    continue
                elif key == "" and value != "" and prevKey != "":
                    specs[prevKey] += " | " + value
                elif key and value:
                    specs[f"{category} - {key}"] = value
                    prevKey = f"{category} - {key}"
            
        self.brands[brand_name]['devices'].append(specs)
    
    def closed(self, reason):
        yield from self.save_data()
    
    def save_data(self):
        yield self.brands
                
