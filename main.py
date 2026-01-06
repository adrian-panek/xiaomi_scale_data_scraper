"""Main entry point for the Mi Scale data extractor."""

import asyncio
from config import SCALE_MAC, DB_PATH, AGE, HEIGHT_CM, GENDER
from database import init_database
from extractor import MiScaleDataExtractor


async def main():
    print("--- Mi Scale Data Extractor Tool ---")
    print(f"Target Address: {'Discovered via scan' if SCALE_MAC == 'XX:XX:XX:XX:XX:XX' else SCALE_MAC}")
    print(f"Database: {DB_PATH}")
    print(f"Configuration: Age={AGE}, Height={HEIGHT_CM}cm, Gender={GENDER}")
    print("-----------------------------------")
    
    init_database()
    
    extractor = MiScaleDataExtractor(address=SCALE_MAC, age=AGE, height_cm=HEIGHT_CM, gender=GENDER)
    await extractor.run_extractor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nFATAL ERROR in main execution: {e}")

