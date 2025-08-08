"""
Image GPS coordinate extraction module
"""

import os
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pyproj
from datetime import datetime


def extract_images_to_json(input_folder, output_file, target_crs, include_no_gps=False, verbose=False):
    """
    Extract GPS coordinates and metadata from images and save to JSON

    Args:
        input_folder (str): Path to folder containing images
        output_file (str): Path to output JSON file
        target_crs (str): Target coordinate system (default: "EPSG:5110")
        include_no_gps (bool): Include images without GPS data
        verbose (bool): Print verbose output

    Returns:
        list: List of processed image data
    """
    def get_exif_data(img):
        exif_data = {}
        info = img._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        return exif_data

    def get_decimal_from_dms(dms, ref):
        # Support both tuple and IFD_Rational (float-like) types
        def rational_to_float(r):
            try:
                return float(r.numerator) / float(r.denominator)
            except AttributeError:
                # Already a float or int
                return float(r)

        degrees = rational_to_float(dms[0])
        minutes = rational_to_float(dms[1])
        seconds = rational_to_float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal

    processed_images = []
    image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')

    try:
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(image_extensions):
                continue
            image_path = os.path.join(input_folder, filename)
            try:
                with Image.open(image_path) as img:
                    # Get file statistics
                    file_size = os.path.getsize(image_path)
                    abs_path = os.path.abspath(image_path)
                    url_path = "file://" + abs_path.replace("\\", "/")
                    processing_date = datetime.now().isoformat()
                    
                    # Extract EXIF data
                    exif_data = get_exif_data(img)
                    
                    # Get GPS information
                    gps_info = exif_data.get("GPSInfo", {})
                    lat, lon, elevation = None, None, None
                    has_gps = False
                    
                    if gps_info:
                        gps_lat = gps_info.get("GPSLatitude")
                        gps_lat_ref = gps_info.get("GPSLatitudeRef")
                        gps_lon = gps_info.get("GPSLongitude")
                        gps_lon_ref = gps_info.get("GPSLongitudeRef")
                        gps_alt = gps_info.get("GPSAltitude")
                        
                        if gps_lat and gps_lat_ref and gps_lon and gps_lon_ref:
                            lat = get_decimal_from_dms(gps_lat, gps_lat_ref)
                            lon = get_decimal_from_dms(gps_lon, gps_lon_ref)
                            has_gps = True
                            
                            # Extract elevation if available
                            if gps_alt:
                                try:
                                    if hasattr(gps_alt, 'numerator'):
                                        elevation = float(gps_alt.numerator) / float(gps_alt.denominator)
                                    else:
                                        elevation = float(gps_alt)
                                except (AttributeError, ValueError, TypeError):
                                    elevation = None
                    
                    # Get date taken from EXIF
                    date_taken = None
                    if "DateTimeOriginal" in exif_data:
                        date_taken = exif_data["DateTimeOriginal"]
                    elif "DateTime" in exif_data:
                        date_taken = exif_data["DateTime"]
                    
                    # Initialize image data dictionary
                    img_data = {
                        "filename": filename,
                        "filepath": abs_path,
                        "image_url": url_path,
                        "filesize": file_size,
                        "processing_date": processing_date,
                        "has_gps": has_gps,
                        "date_taken": date_taken
                    }
                    
                    # Add GPS data if available
                    if has_gps:
                        img_data.update({
                            "latitude": lat,
                            "longitude": lon
                        })
                        
                        if elevation is not None:
                            img_data["elevation"] = elevation
                        
                        # Transform coordinates to target CRS
                        if target_crs:
                            x, y = convert_coordinates(lat, lon, target_crs)
                            if x is not None and y is not None:
                                img_data.update({
                                    "transformed_x": x,
                                    "transformed_y": y,
                                    "coordinate_system": target_crs
                                })
                                
                                # Add transformed_z if elevation available
                                if elevation is not None:
                                    img_data["transformed_z"] = elevation
                    
                    # Only add images with GPS data unless include_no_gps is True
                    if has_gps or include_no_gps:
                        processed_images.append(img_data)
                        if verbose:
                            if has_gps:
                                print(f"Processed {filename}: lat={lat}, lon={lon}")
                            else:
                                print(f"Processed {filename}: No GPS data")
            except (IOError, OSError) as img_err:
                if verbose:
                    print(f"Could not process {filename}: {img_err}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_images, f, indent=2, ensure_ascii=False)

        return processed_images

    except (IOError, OSError) as e:
        print(f"Error processing images: {e}")
        return None


def get_gps_coordinates(image_path):
    """
    Extract GPS coordinates from image EXIF data

    Args:
        image_path (str): Path to image file

    Returns:
        tuple: (latitude, longitude) or (None, None) if no GPS data
    """
    try:
        with Image.open(image_path) as img:
            info = img._getexif()
            if not info:
                return None, None
            
            gps_info = None
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_info = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_info[sub_decoded] = value[t]
                    break
            
            if not gps_info:
                return None, None
                
            # Helper function to convert GPS coordinates
            def get_decimal_from_dms(dms, ref):
                # Support both tuple and IFD_Rational (float-like) types
                def rational_to_float(r):
                    try:
                        return float(r.numerator) / float(r.denominator)
                    except AttributeError:
                        # Already a float or int
                        return float(r)

                degrees = rational_to_float(dms[0])
                minutes = rational_to_float(dms[1])
                seconds = rational_to_float(dms[2])
                decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
                if ref in ['S', 'W']:
                    decimal = -decimal
                return decimal
                
            gps_lat = gps_info.get("GPSLatitude")
            gps_lat_ref = gps_info.get("GPSLatitudeRef")
            gps_lon = gps_info.get("GPSLongitude")
            gps_lon_ref = gps_info.get("GPSLongitudeRef")
            
            if gps_lat and gps_lat_ref and gps_lon and gps_lon_ref:
                lat = get_decimal_from_dms(gps_lat, gps_lat_ref)
                lon = get_decimal_from_dms(gps_lon, gps_lon_ref)
                return lat, lon
                
    except Exception as e:
        print(f"Error extracting GPS from {image_path}: {e}")
        
    return None, None


def convert_coordinates(lat, lon, target_crs):
    """
    Convert GPS coordinates to target coordinate system
    """
    try:
        # Define source and target CRS
        source_crs = pyproj.CRS("EPSG:4326")  # WGS84
        target_crs_obj = pyproj.CRS(target_crs)
        
        # # Validate the target CRS
        # if not target_crs_obj.is_valid:
        #     print(f"Invalid CRS: {target_crs}")
        #     return None, None

        # Create transformer
        transformer = pyproj.Transformer.from_crs(source_crs, target_crs_obj, always_xy=True)

        # Transform coordinates
        x, y = transformer.transform(lon, lat)
        
        # Basic validation - check if coordinates are reasonable
        if abs(x) > 1e10 or abs(y) > 1e10:
            print(f"Suspicious transformation result: x={x}, y={y} for CRS {target_crs}")
            return None, None

        return x, y

    except Exception as e:
        print(f"Error converting coordinates to {target_crs}: {e}")
        return None, None
