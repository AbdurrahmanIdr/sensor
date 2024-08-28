#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
import sqlite3
from datetime import datetime, timedelta

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

# Ultrasonic Sensor Pins
TRIG_PIN = 23
ECHO_PIN = 24

# DHT Sensor
dht_device = adafruit_dht.DHT22(board.D18)

# Setup GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# SQLite Database setup
DATABASE = 'sensor_data.db'

def setup_database():
    """Create a new SQLite database and table if not exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            distance REAL,
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_data(distance, temperature, humidity):
    """Insert new data into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (distance, temperature, humidity)
        VALUES (?, ?, ?)
    ''', (distance, temperature, humidity))
    conn.commit()
    conn.close()

def get_distance():
    """Get distance from the ultrasonic sensor."""
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10µs pulse
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    elapsed_time = end_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is 34300 cm/s
    return distance

def get_temperature_humidity():
    """Get temperature and humidity from the DHT sensor."""
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return temperature, humidity
    except RuntimeError as error:
        print(f"Error reading from DHT sensor: {error}")
        return None, None

def calculate_averages():
    """Calculate the average values of distance, temperature, and humidity from the last 10 minutes."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    cursor.execute('''
        SELECT AVG(distance), AVG(temperature), AVG(humidity)
        FROM sensor_data
        WHERE timestamp >= ?
    ''', (ten_minutes_ago,))
    averages = cursor.fetchone()
    conn.close()
    return averages

def send_average_data(averages):
    """Send the average data. This function can be customized for actual sending logic."""
    if averages:
        distance_avg, temperature_avg, humidity_avg = averages
        print(f"Average Distance (last 10 minutes): {distance_avg:.2f} cm")
        print(f"Average Temperature (last 10 minutes): {temperature_avg:.2f}C")
        print(f"Average Humidity (last 10 minutes): {humidity_avg:.2f}%")
    else:
        print("No data available to calculate averages.")

setup_database()  # Set up the database and table

try:
    last_average_time = time.time()
    while True:
        distance = get_distance()
        temperature, humidity = get_temperature_humidity()

        print(f"Distance: {distance:.2f} cm")
        if temperature is not None and humidity is not None:
            print(f"Temperature: {temperature:.2f}C  Humidity: {humidity:.2f}%")
            insert_data(distance, temperature, humidity)
        else:
            print("Failed to retrieve data from sensor.")
        
        current_time = time.time()
        if current_time - last_average_time >= 600:  # 600 seconds = 10 minutes
            averages = calculate_averages()
            send_average_data(averages)
            last_average_time = current_time
        
        time.sleep(60)  # Wait for 1 minute

except KeyboardInterrupt:
    print("Measurement stopped by User")

finally:
    GPIO.cleanup()
