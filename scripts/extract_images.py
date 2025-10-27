import os
import sys
from pathlib import Path
from datetime import datetime

# Adjust paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_CORE = PROJECT_ROOT / "src" / "core"
sys.path.insert(0, str(SRC_CORE))

from image_processor import extract_images_to_json  # noqa

# Configuration
INPUT_FOLDER = Path(r"C:\Users\HTO334\OneDrive - AFRY\Pictures\BOKEMO")
TARGET_CRS = "EPSG:5107"
OUTPUT_JSON = INPUT_FOLDER / f"extracted_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

INCLUDE_NO_GPS = True
VERBOSE = True

def main():
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    print(f"Reading images from: {INPUT_FOLDER}")
    print(f"Target CRS: {TARGET_CRS}")
    print(f"Writing JSON: {OUTPUT_JSON}")
    data = extract_images_to_json(
        input_folder=str(INPUT_FOLDER),
        output_file=str(OUTPUT_JSON),
        target_crs=TARGET_CRS,
        include_no_gps=INCLUDE_NO_GPS,
        verbose=VERBOSE
    )
    print(f"Processed {len(data) if data else 0} images")

if __name__ == "__main__":
    main()