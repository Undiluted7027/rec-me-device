"""API to work with sqlite3 database"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("phone_brands.db")
    except sqlite3.Error as e:
        print("Error while connecting to SQLite database:", e)
    return conn


@app.route(rule="/gsm_brands", methods=["GET"])
def gsm_brands():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == "GET":
        try:
            get_brands = "SELECT * FROM brands;"
            cursor.execute(get_brands)
            brands = [
                dict(id=row[0], brand=row[1], device_num=row[3])
                for row in cursor.fetchall()
            ]
            return jsonify(brands), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500


@app.route(rule="/gsm_brands/<brand_name>", methods=["GET"])
def gsm_brand(brand_name):
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == "GET":
        try:
            get_devices = f"SELECT * FROM {brand_name}_devices;"
            cursor.execute(get_devices)
            devices = [
                dict(id=row[0], brand=row[2], device_name=row[1])
                for row in cursor.fetchall()
            ]
            return jsonify(devices), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500


@app.route(rule="/gsm_brands/<brand_name>/<device_name>", methods=["GET"])
def gsm_device(brand_name, device_name):
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == "GET":
        try:
            get_device = f"SELECT * FROM {brand_name}_{device_name};"
            cursor.execute(get_device)
            device_specs_headers = [
                description[0] for description in cursor.description
            ]
            device_specs = [
                dict(zip(device_specs_headers, row)) for row in cursor.fetchall()
            ]
            return jsonify(device_specs), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)  # Running the Flask application in debug mode.
