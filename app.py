#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import adafruit_dht

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

# Ultrasonic Sensor Pins
TRIG_PIN = 23
ECHO_PIN = 24

# DHT Sensor
# Create sensor object for AM2301 (compatible with DHT22) on GPIO18 (physical pin 12)
dht_device = adafruit_dht.DHT22(board.D18)  # Ensure this matches your GPIO pin

# Setup GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)


def get_distance():
    # Send a short pulse to the trigger pin
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10µs pulse
    GPIO.output(TRIG_PIN, False)

    # Wait for the echo to be received
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    # Calculate the distance
    elapsed_time = end_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is 34300 cm/s
    return distance


def get_temperature_humidity():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return temperature, humidity
    except RuntimeError as error:
        print(f"Error reading from DHT sensor: {error}")
        return None, None

try:
    while True:
        distance = get_distance()
        temperature, humidity = get_temperature_humidity()
        
        print(f"Distance: {distance:.2f} cm")
        if temperature is not None and humidity is not None:
            print(f"Temperature: {temperature:.2f}C  Humidity: {humidity:.2f}%")
        else:
            print("Failed to retrieve data from sensor.")
        time.sleep(2)

except KeyboardInterrupt:
    print("Measurement stopped by User")

finally:
    GPIO.cleanup()
