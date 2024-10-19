import gsm_scraper, sql_init
from bs4 import BeautifulSoup
import requests, time

# constant variables
LINK = "https://www.gsmarena.com/"
LINK_ALL_DEVICES = LINK + "makers.php3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
    "Keep-Alive": "timeout=15, max=98",
}


def get_all_device_headers_session(device_link):
    device_spec_headers = tuple()
    all_devices = sql_init.get_all_brands_from_table("Acer_devices")
    brand_headers = tuple()
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for device in all_devices:
            response = session.get(LINK + device[3])
            if response.status_code == 200:
                device_html_content = response.text
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
            time.sleep(5)
    return device_spec_headers
