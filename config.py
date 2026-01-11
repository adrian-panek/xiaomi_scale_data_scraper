"""Configuration constants for the Mi Scale data extractor."""

import os

MI_SCALE_SERVICE_UUID = "0000181b-0000-1000-8000-00805f9b34fb"
MI_MEASUREMENT_CHARACTERISTIC_UUID = "00002a9c-0000-1000-8000-00805f9b34fb"

# Read from environment variables with fallback to defaults
SCALE_MAC = os.getenv("SCALE_MAC", "D0:3E:7D:76:AF:C6")
AGE = int(os.getenv("AGE", "25"))
HEIGHT_CM = float(os.getenv("HEIGHT_CM", "178.0"))
GENDER = os.getenv("GENDER", "male")

STABLE_READINGS_REQUIRED = int(os.getenv("STABLE_READINGS_REQUIRED", "7"))
WEIGHT_TOLERANCE = float(os.getenv("WEIGHT_TOLERANCE", "0.1"))
MIN_STABLE_DURATION_SECONDS = float(os.getenv("MIN_STABLE_DURATION_SECONDS", "3.0"))

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "scaledb")
DB_USER = os.getenv("DB_USER", "scaleuser")
DB_PASSWORD = os.getenv("DB_PASSWORD")