# importing required libraries
import requests, json, random, re, logging
import requests.exceptions
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    filename="scraping_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


proxy_list = [
    "https://35.183.5.23:11",
    "https://184.73.68.87:11",
    "https://3.255.250.250:11",
    "https://15.236.203.245:3128",
    "https://3.212.148.199:3128",
]

# List of user agents (for rotation)
agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.71",
]


# Add retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Invalid file/key names have these in them
INVALID_CHARS = r'[<>.:"/\\|?*\x00-\x1F\s]'

old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.extra_info = "{}"  # Default empty JSON string
    return record


logging.setLogRecordFactory(record_factory)


def has_complete_data(device):
    """Check if a device already has complete specification data"""
    return (
        "brief_specs" in device
        and "spec_detailed" in device
        and device["brief_specs"]
        and device["spec_detailed"]
    )


def get_progress_info(data):
    """Get the current progress information from the data"""
    try:
        for brand_idx, brand in enumerate(data["brands"]):
            for device_idx, device in enumerate(brand["devices"]):
                if not has_complete_data(device):
                    return brand_idx, device_idx
        return (
            len(data["brands"]) - 1,
            len(data["brands"][-1]["devices"]) - 1,
        )  # All complete
    except Exception as e:
        logging.error(f"Failed to get progress info: {str(e)}")
        return 0, 0


def save_progress(data, brand_idx, device_idx, error=None):
    """Save current progress and optionally log error"""
    try:
        # Save current state
        progress_info = {
            "last_brand_idx": brand_idx,
            "last_device_idx": device_idx,
            "timestamp": datetime.now().isoformat(),
        }

        # Save progress to a separate file
        writeJSON("scraping_progress", progress_info)

        if error:
            # Log error with progress information
            error_info = {
                "brand_idx": brand_idx,
                "device_idx": device_idx,
                "brand_name": data["brands"][brand_idx]["brand_name"],
                "device_name": data["brands"][brand_idx]["devices"][device_idx][
                    "device_name"
                ],
                "error": str(error),
            }
            logging.error(
                "Scraping failed", extra={"extra_info": json.dumps(error_info)}
            )

        # Save partial data
        writeJSON("partial_progress", data)

    except Exception as e:
        logging.error(f"Failed to save progress: {str(e)}")


def get_session():
    """Create a configured session with retry logic"""
    session = requests.Session()
    # session.verify = "C:/Users/sanch/anaconda3/envs/deviceSystem/Library/ssl"
    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    # session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def safe_request(url, session=None):
    """Handle requests with retries and random headers"""
    headers = {"User-Agent": random.choice(agents)}
    # proxy = FreeProxy().get()
    # proxies = {
    #     "https": proxy,
    # }
    try:
        if session:
            # session.proxies.update(proxies)
            response = session.get(url, headers=headers, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {url}: {str(e)}")
        raise


def loadJSON(file_name: str, mode: str = "r") -> dict:
    """Reads a JSON file"""
    data = {}
    try:
        with open(file_name, mode) as jsonFile:
            data = json.load(jsonFile)
        return data
    except Exception as e:
        logging.error(f"Failed to open file {file_name}: {str(e)}")
        raise


def writeJSON(filename, data, mode="w"):
    """Writes to a JSON file"""
    try:
        with open(f"{filename}.json", mode) as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logging.error(f"Failed to write to {filename}.json: {str(e)}")
        raise


def getBrandLinks():
    """Get links to brand pages"""
    brands = {"brands": []}
    try:
        response = safe_request("https://www.devicespecifications.com/en")
        soup = BeautifulSoup(response.text, "html.parser")
        brand_container = soup.find(class_="brand-listing-container-frontpage")

        if not brand_container:
            logging.error(f"Brand container not found on page")
            raise ValueError("Brand container not found on page")

        brand_tags = brand_container.find_all("a", href=True)
        brands["brands"] = [
            {"brand_name": tag.contents[0].strip(), "url": tag.get("href")}
            for tag in brand_tags
        ]

        writeJSON("brands", brands)
        return brands

    except Exception as e:
        logging.error(f"Failed to get brand links: {str(e)}")
        raise


def getPhoneLinks(brand_name: str, brand_link: str, session=None) -> list:
    """Get links to phone pages from brand page"""
    try:
        response = safe_request(brand_link, session)
        soup = BeautifulSoup(response.text, "html.parser")
        phone_containers = soup.find_all(class_="model-listing-container-80")

        phones = []
        for container in phone_containers:
            for phone in container.find_all("div"):
                if phone.h3 and phone.h3.a:
                    name = phone.h3.text.strip()
                    phones.append({"device_name": name, "url": phone.h3.a.get("href")})
        return phones

    except Exception as e:
        logging.error(f"Failed to get phone links for {brand_name}: {str(e)}")
        return {}  # Return empty dict instead of failing completely


def getBriefSpecs(soup):
    """Get brief/short specs for device"""
    brief_specs_container = soup.find(id="model-brief-specifications")
    brief_specs = {
        b_tag.text.strip(): b_tag.next_sibling.strip(": ").strip()
        for b_tag in brief_specs_container.find_all("b")
        if b_tag.next_sibling
    }
    return brief_specs


def parse_device_specs(soup):
    """Parse device specifications"""

    # Precompile regex to separate numbers and units
    result = []
    value_pattern = re.compile(r"([\d.]+)\s*(.*)")
    try:
        # Use CSS selectors for clarity and performance
        for section in soup.select("header.section-header"):
            # Extract category and description using select_one and get_text
            category_tag = section.select_one("h2.header")
            category_desc_tag = section.select_one("h3.subheader")
            category = (
                category_tag.get_text(strip=True)
                if category_tag
                else "Unknown Category"
            )
            category_desc = (
                category_desc_tag.get_text(strip=True)
                if category_desc_tag
                else "No Description"
            )

            # Get the associated table; skip if not found
            table = section.find_next_sibling("table", class_="model-information-table")
            if not table:
                continue

            sub_categories = []
            for row in table.find_all("tr"):
                tds = row.find_all("td")
                if len(tds) != 2:
                    continue

                # Extract sub-category text (direct child text only) and description
                sub_cat_text = tds[0].find(text=True, recursive=False)
                sub_category = (
                    sub_cat_text.strip() if sub_cat_text else "Unknown Sub-Category"
                )
                sub_category_desc_tag = tds[0].find("p")
                sub_category_desc = (
                    sub_category_desc_tag.get_text(strip=True)
                    if sub_category_desc_tag
                    else ""
                )

                values = []
                for content in tds[1].contents:
                    # Skip <br> tags (or any tag with name 'br')
                    if hasattr(content, "name") and content.name == "br":
                        continue

                    if isinstance(content, str):
                        text = content.strip()
                        # Split by any newlines and clean up each part
                        parts = [s.strip() for s in text.split("\n") if s.strip()]
                        for part in parts:
                            match = value_pattern.match(part)
                            if match:
                                num, unit = match.groups()
                                values.append(
                                    {
                                        "value": num,
                                        "unit": unit.strip("()") if unit else None,
                                    }
                                )
                            else:
                                values.append({"value": part, "unit": None})

                sub_categories.append(
                    {
                        "sub_category": sub_category,
                        "sub_category_desc": sub_category_desc,
                        "values": values,
                    }
                )

            result.append(
                {
                    "category": category,
                    "category_desc": category_desc,
                    "sub_categories": sub_categories,
                }
            )

        return result

    except Exception as e:
        logging.error(f"Failed to parse specs: {str(e)}")
        return []


def getPhoneSpecs(phone_link, session=None):
    """Get specs from phone page"""
    try:
        response = safe_request(phone_link, session)
        soup = BeautifulSoup(response.text, "lxml")

        return {
            "brief_specs": getBriefSpecs(soup),
            "spec_detailed": parse_device_specs(soup),
        }

    except Exception as e:
        logging.error(f"Failed to get specs for {phone_link}: {str(e)}")
        raise  # Propagate error to caller


def getCurrentBrandAndDevice(data, brand, device):
    brandIdx = 0
    deviceIdx = 0
    for brand_content in data:
        if brand_content["brand_name"] == brand:
            for device_content in brand_content["devices"]:
                if device_content == device:
                    break
                deviceIdx += 1
            break
        brandIdx += 1
    return (brandIdx, deviceIdx)


def processFaultyBrandAndDevice(brand, device):
    data = loadJSON("modified_data.json")
    brands_count = len(data["brands"])
    session = get_session()
    (brandIdx, deviceIdx) = getCurrentBrandAndDevice(data["brands"], brand, device)
    brand_content = data["brands"][brandIdx]
    device_content = brand_content["devices"][deviceIdx]
    try:
        print(
            f"Processing brand {brandIdx+1}/{brands_count}: {brand_content['brand_name']}"
        )
        print(f"  Device {deviceIdx+1}: {device_content['device_name']}")
        specs = getPhoneSpecs(device_content["link"], session)
        device_content.update(specs)
        sleep(random.uniform(0.5, 1.5))
    except Exception as e:
        # Log detailed error information
        error_info = {
            "brand": brand["brand_name"],
            "device": device["device_name"],
            "url": device["link"],
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
        logging.error(json.dumps(error_info))

    # Save current state before exiting
    writeJSON(
        f"partial_progress_{brand_content['brand_name']}{device_content['device_name']}",
        brand_content,
    )
    return  # Exit completely on first error


def writeData():
    """Write all data to a JSON file: brand, model, model brief specs, model specs"""
    data = loadJSON("modified_data.json")
    session = get_session()  # Use session for connection pooling
    brands_count = len(data["brands"])

    try:
        for brand_idx, brand in enumerate(data["brands"]):
            print(
                f"Processing brand {brand_idx+1}/{brands_count}: {brand['brand_name']}"
            )

            for device_idx, device in enumerate(brand["devices"]):
                print(f"  Device {device_idx+1}: {device['device_name']}")

                try:
                    specs = getPhoneSpecs(device["link"], session)
                    device.update(specs)
                    # Add small delay to be polite to the server
                    sleep(random.uniform(0.5, 1.5))

                except Exception as e:
                    # Log detailed error information
                    error_info = {
                        "brand": brand["brand_name"],
                        "device": device["device_name"],
                        "url": device["link"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    logging.error(json.dumps(error_info))

                    # Save current state before exiting
                    writeJSON("partial_progress", data)
                    print("Scraping aborted due to error. Partial progress saved.")
                    return  # Exit completely on first error

            # Save progress after each brand
            writeJSON(f"progress_after_{brand_idx}", data)

    except KeyboardInterrupt:
        writeJSON("partial_progress", data)
        print("Process interrupted by user. Partial progress saved.")
        raise

    # Final save
    writeJSON("final_data", data)


def scrape_data(data, start_brand_idx=None, start_device_idx=None, overwrite=False):
    """
    Scrape device data with support for starting from specific indexes

    Args:
        data: The data structure containing brands and devices
        start_brand_idx: Optional starting brand index
        start_device_idx: Optional starting device index within the brand
        overwrite: Whether to overwrite existing device data
    """
    session = get_session()
    brands_count = len(data["brands"])

    # If no starting points provided, try to load from progress file
    if start_brand_idx is None or start_device_idx is None:
        try:
            progress = loadJSON("scraping_progress.json")
            start_brand_idx = progress.get("last_brand_idx", 0)
            start_device_idx = progress.get("last_device_idx", 0)
        except:
            start_brand_idx = start_brand_idx or 0
            start_device_idx = start_device_idx or 0

    try:
        for brand_idx, brand in enumerate(
            data["brands"][start_brand_idx:], start_brand_idx
        ):
            print(
                f"Processing brand {brand_idx+1}/{brands_count}: {brand['brand_name']}"
            )

            # Determine starting device index for this brand
            current_device_idx = start_device_idx if brand_idx == start_brand_idx else 0

            for device_idx, device in enumerate(
                brand["devices"][current_device_idx:], current_device_idx
            ):
                print(f"  Device {device_idx+1}: {device['device_name']}")

                # Skip if device has data and we're not overwriting
                if not overwrite and has_complete_data(device):
                    print(f"  Skipping {device['device_name']} - data already exists")
                    continue

                try:
                    specs = getPhoneSpecs(device["link"], session)
                    device.update(specs)
                    sleep(random.uniform(0.5, 1.5))
                    save_progress(data, brand_idx, device_idx)

                except Exception as e:
                    save_progress(data, brand_idx, device_idx, error=e)
                    print(
                        f"Error processing device. Progress saved. Use indexes {brand_idx}, {device_idx} to resume."
                    )
                    return False

            # Save progress after each brand
            save_progress(data, brand_idx, len(brand["devices"]) - 1)

    except KeyboardInterrupt:
        current_brand_idx = brand_idx if "brand_idx" in locals() else start_brand_idx
        current_device_idx = (
            device_idx if "device_idx" in locals() else start_device_idx
        )
        save_progress(data, current_brand_idx, current_device_idx)
        print("\nProcess interrupted by user. Progress saved.")
        return False

    # Final save
    writeJSON("final_data", data)
    return True


def resume_scraping(data_file="modified_data.json", overwrite=False):
    """Resume scraping from the last saved position"""
    data = loadJSON(data_file)
    try:
        progress = loadJSON("scraping_progress.json")
        brand_idx = progress["last_brand_idx"]
        device_idx = progress["last_device_idx"]
        print(f"Resuming from brand index {brand_idx}, device index {device_idx}")
        return scrape_data(data, brand_idx, device_idx, overwrite)
    except Exception as e:
        print(f"Could not load progress info: {e}")
        print("Starting from the beginning...")
        return scrape_data(data, overwrite=overwrite)


def start_scraping_from_indexes(
    brand_idx, device_idx, data_file="modified_data.json", overwrite=False
):
    """Start scraping from specific brand and device indexes"""
    data = loadJSON(data_file)
    return scrape_data(data, brand_idx, device_idx, overwrite)


# writeData()
# data = loadJSON("modified_data.json")
start_scraping_from_indexes(94, 60, overwrite=False)
# print(getCurrentBrandAndDevice(data['brands'], "Alcatel", "OneTouch Pop 2 (4.5)"))
