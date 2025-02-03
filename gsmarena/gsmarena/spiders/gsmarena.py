import scrapy


class GSMArenaSpider(scrapy.Spider):
    name = "gsmarena"
    start_urls = ["https://www.gsmarena.com/"]

    def parse(self, response):
        # Extract all brand links
        brands = response.css("div.brandmenu-v2 li a::attr(href)").getall()
        for brand in brands:
            yield response.follow(brand, callback=self.parse_brand_page)

    def parse_brand_page(self, response):
        # Extract brand name from URL
        brand = response.url.split("/")[-1].split("-")[0].replace("_", " ")

        # Extract device links
        devices = response.css("div.makers li a")
        for device in devices:
            yield response.follow(
                device, callback=self.parse_device_page, meta={"brand": brand}
            )

        # Handle pagination
        next_page = response.css("a.pages-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_brand_page)

    def parse_device_page(self, response):
        # Extract device name
        device = response.css("h1.specs-phone-name-title::text").get().strip()

        # Extract specifications
        specs = {}
        for table in response.css("#specs-list table"):
            category = table.xpath(".//tr[1]/th//text()").get().strip()
            specs[category] = []

            for row in table.css("tr"):
                name = "".join(row.css(".ttl *::text").getall()).strip()
                value = "".join(row.css(".nfo *::text").getall()).strip()

                if name and value:
                    specs[category].append({"name": name, "value": value})

        yield {
            "brand": response.meta["brand"],
            "device": device,
            "specifications": specs,
        }
