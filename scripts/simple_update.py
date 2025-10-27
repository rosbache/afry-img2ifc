import json
import pandas as pd

# Simple script to update JSON image URLs from Excel file
# Customize the file paths below as needed

# File paths
JSON_FILE = 'extracted_images4.json'
EXCEL_FILE = 'N_XXXXX_SE Hovd_Files_20250807081208.xlsx'

# Read Excel file
print("Reading Excel file...")
df = pd.read_excel(EXCEL_FILE)
print(f"Found {len(df)} rows in Excel file")

# Display column names to verify
print("Excel columns:", list(df.columns))

# Create filename to URL mapping from Excel
# Adjust column names if they're different in your Excel file
filename_to_url = {}
for _, row in df.iterrows():
    filename = row['File name']  # Adjust column name if needed
    image_url = row['ImageURL']   # Adjust column name if needed
    
    if pd.notna(filename) and pd.notna(image_url):
        filename_to_url[filename] = image_url

print(f"Created mapping for {len(filename_to_url)} files")

# Read JSON file
print("Reading JSON file...")
with open(JSON_FILE, 'r') as f:
    json_data = json.load(f)

print(f"Found {len(json_data)} records in JSON file")

# Update image URLs
updated_count = 0
for item in json_data:
    if isinstance(item, dict) and 'filename' in item:
        filename = item['filename']
        if filename in filename_to_url:
            item['image_url'] = filename_to_url[filename]
            updated_count += 1
            print(f"Updated: {filename}")

print(f"Updated {updated_count} records")

# Save updated JSON
with open(JSON_FILE, 'w') as f:
    json.dump(json_data, f, indent=2)

print("JSON file updated successfully!")
