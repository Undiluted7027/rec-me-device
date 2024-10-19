"""Setups up required tables"""

import gsm_scraper
import sqlite3
import time


def setup():
    conn = sqlite3.connect("phone_brands.db")
    cur = conn.cursor()
    return conn, cur


# def setup_mobile_brands(table_name):
#     """Setups up the table for mobile brands"""
#     conn, cur = setup()
#     phone_brand_data = get_all_links('td')
#     table_name = "brands"
#     query = f"INSERT INTO {table_name} (id, name, link, device_num) VALUES "
#     for i in range(len(phone_brand_data)):
#         sub_query = ""
#         if i != len(phone_brand_data) - 1:
#             sub_query = f"{phone_brand_data[i]}, "
#         else:
#             sub_query = f"{phone_brand_data[i]}"
#         query += sub_query

#     cur.execute(query)
#     conn.commit()


def get_index_link(table_name, value):
    conn, cur = setup()
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    for i in range(len(rows)):
        try:
            k = rows[i].index(value)
            return rows[i][2]
        except ValueError:
            return "error"


def setup_brand_with_devices(brand_name):
    schema = {
        # "id": "INTEGER PRIMARY KEY",
        f"{brand_name}_device_name": "TEXT",
        "device_brand": "CHAR(20)",
        f"{brand_name}_device_link": "TEXT",
        # "FOREIGN KEY (device_brand)": "REFERENCES brands(name)",
    }
    k = get_index_link("brands", brand_name)
    print(k)
    brand_device_info = gsm_scraper.get_brand_device_list(k)
    insert_query = f"INSERT INTO {brand_name}_devices("
    insert_query += ", ".join([f"{key}" for key, value in schema.items()])
    insert_query += ") VALUES"
    print(insert_query)
    for id in range(len(brand_device_info)):
        if id != len(brand_device_info) - 1:
            insert_query += f"{brand_device_info[id]},"
        else:
            insert_query += f"{brand_device_info[id]}"
    conn, cur = setup()
    cur.execute(insert_query)
    conn.commit()


def get_all_brands_from_table(table_name):
    conn, cur = setup()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    return rows


def create_brand_table(brand_name):
    schema = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        f"{brand_name}_device_name": "TEXT",
        "device_brand": "CHAR(20)",
        f"{brand_name}_device_link": "TEXT",
        "FOREIGN KEY (device_brand)": "REFERENCES brands(name)",
    }
    query = f"CREATE TABLE IF NOT EXISTS {brand_name}_devices("
    query += ", ".join([f"{key} {value}" for key, value in schema.items()])
    query += ");"
    conn, cur = setup()
    cur.execute(query)
    conn.commit()


def get_kth_brand_from_table(table_name, k):
    conn, cur = setup()
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    ith_row = rows[k - 1]
    print(ith_row)
    brand_link = ith_row[2]
    return brand_link


def get_headers_all_devices():
    all_devices = get_all_brands_from_table("Acer_devices")
    brand_headers = tuple()
    for device in all_devices:
        time.sleep(0.7)
        brand_headers += gsm_scraper.get_device_headers(device[3])
    print(set(brand_headers))


# get_kth_brand_from_table("brands", 2)
# create_brand_table("Acer")
# setup_brand_with_devices("Acer")
get_headers_all_devices()
