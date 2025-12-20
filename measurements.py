import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List

from bleak import BleakClient, BleakScanner

MI_SCALE_SERVICE_UUID = "0000181b-0000-1000-8000-00805f9b34fb"
MI_MEASUREMENT_CHARACTERISTIC_UUID = "00002a9c-0000-1000-8000-00805f9b34fb"

SCALE_MAC = "D0:3E:7D:76:AF:C6" 

def parse_and_print_data(raw_data: bytearray):
    weight = ((raw_data[12] << 8) + raw_data[11]) / 200
    impedance = (raw_data[10] << 8) + raw_data[9]

    print(f"Weight: {weight}, impedance: {impedance}")

class MiScaleDataExtractor:
    def __init__(self, address: str):
        self.address = address
        self.is_running = True

    async def _handle_measurement(self, sender: int, data: bytearray):
        """
        Callback function called when new data arrives. Calls the new parser.
        """
        parse_and_print_data(data)
        

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

async def main():
    print("--- Mi Scale Data Extractor Tool ---")
    print(f"Target Address: {'Discovered via scan' if SCALE_MAC == 'XX:XX:XX:XX:XX:XX' else SCALE_MAC}")
    print("-----------------------------------")
    
    extractor = MiScaleDataExtractor(address=SCALE_MAC)
    await extractor.run_extractor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nFATAL ERROR in main execution: {e}")