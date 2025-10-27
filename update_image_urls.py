import json
import pandas as pd
import os
import sys

def update_json_with_excel_urls(json_file_path, excel_file_path, output_json_path=None):
    """
    Update image URLs in JSON file based on matching filenames from Excel file.
    
    Args:
        json_file_path (str): Path to the JSON file containing image data
        excel_file_path (str): Path to the Excel file with filename and ImageURL columns
        output_json_path (str, optional): Path for the updated JSON file. If None, overwrites original.
    
    Returns:
        dict: Summary of the update operation
    """
    
    # Read the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"Loaded JSON file with {len(json_data)} records")
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
    
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file_path)
        print(f"Loaded Excel file with {len(df)} rows")
        
        # Check if required columns exist
        if 'File name' not in df.columns:
            # Try alternative column names
            filename_col = None
            for col in df.columns:
                if 'file' in col.lower() and 'name' in col.lower():
                    filename_col = col
                    break
            if filename_col is None:
                print("Available columns:", list(df.columns))
                raise ValueError("Could not find 'File name' column in Excel file")
        else:
            filename_col = 'File name'
            
        if 'ImageURL' not in df.columns:
            # Try alternative column names
            url_col = None
            for col in df.columns:
                if 'url' in col.lower() or ('image' in col.lower() and 'url' in col.lower()):
                    url_col = col
                    break
            if url_col is None:
                print("Available columns:", list(df.columns))
                raise ValueError("Could not find 'ImageURL' column in Excel file")
        else:
            url_col = 'ImageURL'
            
        print(f"Using columns: '{filename_col}' and '{url_col}'")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    
    # Create a mapping dictionary from Excel data
    excel_mapping = {}
    for _, row in df.iterrows():
        filename = row[filename_col]
        image_url = row[url_col]
        
        # Skip rows with missing data
        if pd.isna(filename) or pd.isna(image_url):
            continue
            
        # Extract just the filename if it's a full path
        if isinstance(filename, str):
            filename = os.path.basename(filename)
        
        excel_mapping[filename] = image_url
    
    print(f"Created mapping for {len(excel_mapping)} files from Excel")
    
    # Update JSON data
    updated_count = 0
    not_found_count = 0
    not_found_files = []
    
    for item in json_data:
        # Skip items that don't have required fields
        if not isinstance(item, dict) or 'filename' not in item:
            continue
            
        filename = item['filename']
        
        if filename in excel_mapping:
            old_url = item.get('image_url', 'N/A')
            new_url = excel_mapping[filename]
            item['image_url'] = new_url
            updated_count += 1
            print(f"Updated {filename}: {old_url} -> {new_url}")
        else:
            not_found_count += 1
            not_found_files.append(filename)
    
    # Save updated JSON
    output_path = output_json_path or json_file_path
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"Updated JSON saved to: {output_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return None
    
    # Summary
    summary = {
        'total_json_records': len(json_data),
        'total_excel_mappings': len(excel_mapping),
        'updated_count': updated_count,
        'not_found_count': not_found_count,
        'not_found_files': not_found_files[:10]  # Show first 10 not found files
    }
    
    print("\n" + "="*50)
    print("UPDATE SUMMARY")
    print("="*50)
    print(f"Total JSON records: {summary['total_json_records']}")
    print(f"Total Excel mappings: {summary['total_excel_mappings']}")
    print(f"Successfully updated: {summary['updated_count']}")
    print(f"Files not found in Excel: {summary['not_found_count']}")
    
    if not_found_files:
        print(f"\nFirst few files not found in Excel:")
        for filename in summary['not_found_files']:
            print(f"  - {filename}")
        if not_found_count > 10:
            print(f"  ... and {not_found_count - 10} more")
    
    return summary

def main():
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'extracted_images.json')
    excel_file = os.path.join(script_dir, 'N_XXXXX_SE Hovd_Files_20250807081208.xlsx')
    
    # Check if files exist
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        print("Available Excel files in directory:")
        for file in os.listdir(script_dir):
            if file.endswith('.xlsx'):
                print(f"  - {file}")
        return
    
    # Create backup of original JSON file
    backup_file = json_file.replace('.json', '_backup.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as src, open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f"Created backup: {backup_file}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Run the update
    result = update_json_with_excel_urls(json_file, excel_file)
    
    if result:
        print(f"\nUpdate completed successfully!")
        print(f"Backup saved as: {backup_file}")
    else:
        print("Update failed!")

if __name__ == "__main__":
    main()
