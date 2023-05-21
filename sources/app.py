from flask import Flask, render_template
import configparser
import redis
import pymysql
import random
from waitress import serve

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

redis_host = config.get("redis", "host")
redis_port = config.get("redis", "port")
redis_password = config.get("redis", "password")

mysql_host = config.get("mysql", "host")
mysql_port = config.getint("mysql", "port")
mysql_user = config.get("mysql", "user")
mysql_password = config.get("mysql", "password")
mysql_database = config.get("mysql", "database")

app_port = config.get("listening", "port")

redis_connection = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
mysql_connection = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password, database=mysql_database)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/explore")
def explore():
    planet_name = redis_connection.get("planet_name")
    planet_type = redis_connection.get("planet_type")
    planet_average_temperature = redis_connection.get("planet_average_temperature")
    planet_orbital_velocity = redis_connection.get("planet_orbital_velocity")
    random_id = random.randint(1, 8)
    cursor = mysql_connection.cursor()

    if planet_name is None:
        cursor.execute("SELECT name FROM planets WHERE id=%s", (random_id))
        for row1 in cursor.fetchone():
            planet_name = row1[0:]
        redis_connection.setex("planet_name", 10, planet_name)

    if planet_type is None:
        cursor.execute("SELECT type FROM planets WHERE id=%s", (random_id))
        for row2 in cursor.fetchone():
            planet_type = row2[0:]
        redis_connection.setex("planet_type", 10, planet_type)

    if planet_average_temperature is None:
        cursor.execute("SELECT average_temperature FROM planets WHERE id=%s", (random_id))
        planet_average_temperature = cursor.fetchone()[0]
        redis_connection.setex("planet_average_temperature", 10, planet_average_temperature)

    if planet_orbital_velocity is None:
        cursor.execute("SELECT orbital_velocity FROM planets WHERE id=%s", (random_id))
        planet_orbital_velocity = cursor.fetchone()[0]
        redis_connection.setex("planet_orbital_velocity", 10, planet_orbital_velocity)

    return render_template("planet.html", planet_name=planet_name, planet_type=planet_type, planet_average_temperature=planet_average_temperature, planet_orbital_velocity=planet_orbital_velocity)

if __name__ == "__main__":
    print("The app is running on port " + app_port + "!")
    print("Press Ctrl+C to exit.")
    serve(app, host='0.0.0.0', port=app_port)
