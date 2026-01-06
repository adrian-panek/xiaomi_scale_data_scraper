"""Mi Scale BLE data extractor class."""

import asyncio
from datetime import datetime
from typing import Optional

from bleak import BleakClient, BleakScanner

from config import (
    MI_SCALE_SERVICE_UUID,
    MI_MEASUREMENT_CHARACTERISTIC_UUID,
    SCALE_MAC,
    STABLE_READINGS_REQUIRED,
    WEIGHT_TOLERANCE,
    MIN_STABLE_DURATION_SECONDS,
    AGE,
    HEIGHT_CM,
    GENDER
)
from parser import parse_measurement_data
from database import store_measurement


class MiScaleDataExtractor:
    def __init__(self, address: str, age: int = AGE, height_cm: float = HEIGHT_CM, gender: str = GENDER):
        self.address = address
        self.is_running = True
        self.age = age
        self.height_cm = height_cm
        self.gender = gender
        self.recent_readings = []
        self.reading_timestamps = []
        self.stable_start_time = None 
        self.measurement_stored = False 

    def _is_measurement_stable(self, weight: float) -> bool:
        """Check if the measurement is stable based on recent readings and duration."""
        current_time = datetime.now()
        self.recent_readings.append(weight)
        self.reading_timestamps.append(current_time)
        
        if len(self.recent_readings) > STABLE_READINGS_REQUIRED:
            self.recent_readings.pop(0)
            self.reading_timestamps.pop(0)
        
        if len(self.recent_readings) < STABLE_READINGS_REQUIRED:
            return False
        
        min_weight = min(self.recent_readings)
        max_weight = max(self.recent_readings)
        is_weight_stable = (max_weight - min_weight) <= WEIGHT_TOLERANCE
        
        if not is_weight_stable:
            self.stable_start_time = None
            return False
        
        if self.stable_start_time is None:
            self.stable_start_time = current_time
            return False
        
        stable_duration = (current_time - self.stable_start_time).total_seconds()
        
        return stable_duration >= MIN_STABLE_DURATION_SECONDS

    async def _handle_measurement(self, sender: int, data: bytearray):
        """
        Callback function called when new data arrives.
        Detects stable measurements and stores only one per session.
        """
        if self.measurement_stored:
            return
        
        try:
            measurement = parse_measurement_data(data, self.age, self.height_cm, self.gender)
            weight = measurement['weight']
            
            if self._is_measurement_stable(weight):
                success = store_measurement(
                    weight=measurement['weight'],
                    impedance=measurement['impedance'],
                    bmi=measurement['bmi'],
                    bmr=measurement['bmr'],
                    body_fat=measurement['body_fat']
                )
                
                if success:
                    self.measurement_stored = True
                    print("\n" + "="*50)
                    print("✅ MEASUREMENT STORED SUCCESSFULLY")
                    print("="*50)
                    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Weight: {measurement['weight']:.2f} kg")
                    print(f"Impedance: {measurement['impedance']}")
                    print(f"BMI: {measurement['bmi']:.2f}")
                    print(f"BMR: {measurement['bmr']:.2f} kcal/day")
                    print(f"Body Fat %: {measurement['body_fat']:.2f}%")
                    print("="*50)
                    print("\n✅ Measurement saved to database. You can step off the scale.")
                    print("   Press Ctrl+C to exit.\n")
                    
                    self.is_running = False
            else:
                readings_count = len(self.recent_readings)
                weight_stable = len(self.recent_readings) >= STABLE_READINGS_REQUIRED and \
                               (max(self.recent_readings) - min(self.recent_readings)) <= WEIGHT_TOLERANCE
                
                if weight_stable and self.stable_start_time:
                    stable_duration = (datetime.now() - self.stable_start_time).total_seconds()
                    progress_msg = f"⏳ Stabilizing measurement... ({readings_count}/{STABLE_READINGS_REQUIRED} readings, stable for {stable_duration:.1f}/{MIN_STABLE_DURATION_SECONDS}s, weight: {weight:.2f} kg)"
                else:
                    progress_msg = f"⏳ Stabilizing measurement... ({readings_count}/{STABLE_READINGS_REQUIRED} readings, weight: {weight:.2f} kg)"
                
                print(progress_msg, end='\r')
                
        except Exception as e:
            print(f"\n❌ Error processing measurement: {e}")
        

    async def discover_scale(self) -> Optional[str]:
        print(f"🔍 Starting BLE scan for Mi Scale (Service UUID: {MI_SCALE_SERVICE_UUID})...")
        devices = await BleakScanner.discover(
            service_uuids=[MI_SCALE_SERVICE_UUID],
            timeout=10.0
        )

        if devices:
            device = devices[0]
            self.address = device.address
            print(f"✅ Found Mi Scale: **{device.address}** ({device.name})")
            return device.address
        else:
            print("❌ No Mi Scale devices found after scanning for 10 seconds.")
            return None

    async def run_extractor(self):
        if self.address == SCALE_MAC:
            discovered_address = await self.discover_scale()
            if not discovered_address:
                return
            self.address = discovered_address
            
        try:
            async with BleakClient(self.address) as client:
                if not client.is_connected:
                    print("❌ Failed to connect to the Mi Scale.")
                    return

                print(f"✅ Successfully connected to Mi Scale at {self.address}.")
                print(f"⏳ Subscribing to measurement characteristic...")
                await client.start_notify(
                    MI_MEASUREMENT_CHARACTERISTIC_UUID,
                    self._handle_measurement
                )
                print("\n   *** DATA EXTRACTOR IS RUNNING. PLEASE STEP ON THE SCALE NOW. ***")
                print("   (Press Ctrl+C to stop listening at any time)")
                
                while self.is_running:
                    await asyncio.sleep(1) 

        except Exception as e:
            print(f"❌ An error occurred during BLE operation: {e}")
            
        finally:
            print("\nData extraction process finished.")

