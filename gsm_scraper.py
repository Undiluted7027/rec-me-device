"""Gets data from GSMArena website"""

import requests
import re
from bs4 import BeautifulSoup

# constant variables
LINK = "https://www.gsmarena.com/"
LINK_ALL_DEVICES = LINK + "makers.php3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
    "Keep-Alive": "timeout=15, max=98",
}


def make_request(link):
    """Creates a request to reach GSMArena"""
    req = requests.get(
        link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=15, max=98",
        },
    )
    print("Status:", req.status_code)
    htmlContent = req.text
    return htmlContent


def get_all_links(tagName):
    brands_info = []
    content_of_main_page = make_request(LINK_ALL_DEVICES)
    soup = BeautifulSoup(content_of_main_page, "html.parser")
    key = 1
    # table_of_brands = soup.findAll('td')
    for tag in soup.find_all(re.compile(f"^{tagName}")):
        print(tag.name)
        a_tag = tag.find("a")
        href = a_tag.get("href")
        # Extract the brand name (text before the <br> tag)
        brand_name = a_tag.contents[0].strip()
        # Extract the number of devices (inside the <span> tag)
        devices = a_tag.find("span").text.strip()
        devices = int(devices[: devices.find(" devices")])
        brands_info.append((brand_name, href, devices))
        print(f"Brand: {brand_name}, Link: {href}, Devices: {devices}")
        key += 1
    print(len(soup.find_all(re.compile("^td"))))
    return brands_info


def get_links(brand_name, soup, tagName):
    information = []
    k = 1
    for tag in soup.find_all(re.compile(f"^{tagName}")):
        a_tag = tag.find("a")
        href = a_tag.get("href")
        device_name = a_tag.find("span").text.strip()
        information.append((device_name, brand_name, href))
        k += 1
        print(f"Brand: {brand_name}, Link: {href}, DeviceName: {device_name}")
    return information


def get_brand_device_list(brand_link):
    brand_link = LINK + brand_link
    brand_devices = []
    brand_html_content = make_request(brand_link)
    brand_all_soup = BeautifulSoup(brand_html_content, "html.parser")
    more_than_one_page = brand_all_soup.find("div", class_="nav-pages").find_all("a")
    brand_makers_div = brand_all_soup.find("div", class_="makers")
    brand_list_html = brand_makers_div.ul
    brand_device_page = get_links("Acer", brand_list_html, "li")
    brand_devices.extend(brand_device_page)
    for page in more_than_one_page:
        href = page.get("href")
        # print(href, page.has_attr("class"))
        if href != "#" and page.has_attr("class") == False:
            brand_link = LINK + href
            brand_html_content = make_request(brand_link)
            brand_all_soup = BeautifulSoup(brand_html_content, "html.parser")
            brand_makers_div = brand_all_soup.find("div", class_="makers")
            brand_list_html = brand_makers_div.ul
            brand_device_page = get_links("Acer", brand_list_html, "li")
            brand_devices.extend(brand_device_page)
    return brand_devices


# get_brand_device_list("huawei-phones-58.php")


def get_device_headers(device_link):
    device_spec_headers = tuple()
    device_link = LINK + device_link
    device_html_content = make_request(device_link)
    device_soup = BeautifulSoup(device_html_content, "html.parser")
    device_tables = device_soup.find_all("table")
    for device_spec_table in device_tables:
        # print(device_spec_table)
        device_spec_body = device_spec_table.find("td", class_="ttl")
        device_spec_headers += (device_spec_body.text.strip(),)
        # print(device_spec_body)
    # print(len(device_soup.find_all("table")))
    print(device_spec_headers)
    print(len(device_spec_headers))
    return device_spec_headers


# get_device_info("acer_chromebook_tab_10-9139.php")
