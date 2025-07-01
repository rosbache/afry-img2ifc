"""
Image processor for extracting GPS metadata and transforming coordinates
"""

import os
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread
import pyproj
from typing import Dict, Optional, Tuple, List
import config


class ImageProcessor:
    """Handles image metadata extraction and coordinate transformation"""
    
    def __init__(self):
        """Initialize the image processor with coordinate transformation"""
        # Set up coordinate transformation from WGS84 to EPSG:5110
        self.transformer = pyproj.Transformer.from_crs(
            config.SOURCE_CRS, 
            config.TARGET_CRS, 
            always_xy=True
        )
    
    def extract_gps_data(self, image_path: str) -> Optional[Dict]:
        """
        Extract GPS coordinates, elevation, and date from image EXIF data
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with GPS data or None if not found
        """
        try:
            # Try using Pillow first for basic EXIF data
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                
                if exif_data is None:
                    print(f"No EXIF data found in {image_path}")
                    return None
                
                # Extract GPS info
                gps_info = {}
                date_taken = None
                
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    if tag == "GPSInfo":
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_info[gps_tag] = gps_value
                    elif tag == "DateTime":
                        date_taken = str(value)
                
                # Extract latitude and longitude
                lat = self._get_decimal_from_dms(
                    gps_info.get('GPSLatitude'), 
                    gps_info.get('GPSLatitudeRef')
                )
                lon = self._get_decimal_from_dms(
                    gps_info.get('GPSLongitude'), 
                    gps_info.get('GPSLongitudeRef')
                )
                
                if lat is None or lon is None:
                    print(f"No valid GPS coordinates found in {image_path}")
                    return None
                
                # Extract elevation
                elevation = self._get_elevation(gps_info)
                
                return {
                    'filename': os.path.basename(image_path),
                    'filepath': image_path,
                    'latitude': lat,
                    'longitude': lon,
                    'elevation': elevation,
                    'date_taken': date_taken
                }
                
        except Exception as e:
            print(f"Error extracting GPS data from {image_path}: {str(e)}")
            return None
    
    def _get_decimal_from_dms(self, dms, ref) -> Optional[float]:
        """Convert GPS DMS (Degrees, Minutes, Seconds) to decimal degrees"""
        if not dms or not ref:
            return None
        
        try:
            degrees = float(dms[0])
            minutes = float(dms[1])
            seconds = float(dms[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Adjust for hemisphere
            if ref in ['S', 'W']:
                decimal = -decimal
                
            return decimal
        except (IndexError, ValueError, TypeError):
            return None
    
    def _get_elevation(self, gps_info: Dict) -> float:
        """Extract elevation from GPS info, default to 0 if not found"""
        try:
            altitude = gps_info.get('GPSAltitude')
            altitude_ref = gps_info.get('GPSAltitudeRef', 0)
            
            if altitude is not None:
                elevation = float(altitude)
                # GPSAltitudeRef: 0 = above sea level, 1 = below sea level
                if altitude_ref == 1:
                    elevation = -elevation
                return elevation
        except (ValueError, TypeError):
            pass
        
        return 0.0  # Default elevation
    
    def transform_coordinates(self, lat: float, lon: float, elevation: float = 0.0) -> Tuple[float, float, float]:
        """
        Transform coordinates from WGS84 to EPSG:5110 (in meters)
        
        Args:
            lat: Latitude in WGS84
            lon: Longitude in WGS84
            elevation: Elevation in meters
            
        Returns:
            Tuple of (x, y, z) coordinates in EPSG:5110 in meters
        """
        try:
            # Transform horizontal coordinates
            x, y = self.transformer.transform(lon, lat)
            # Keep coordinates in meters for IFC2x3 with meter units
            return x, y, elevation
        except Exception as e:
            print(f"Error transforming coordinates ({lat}, {lon}): {str(e)}")
            return None
    
    def process_images_folder(self, folder_path: str) -> List[Dict]:
        """
        Process all images in a folder and extract GPS data
        
        Args:
            folder_path: Path to the folder containing images
            
        Returns:
            List of dictionaries with image data and transformed coordinates
        """
        processed_images = []
        
        if not os.path.exists(folder_path):
            print(f"Images folder not found: {folder_path}")
            return processed_images
        
        # Get all image files
        image_files = []
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in config.SUPPORTED_FORMATS):
                image_files.append(os.path.join(folder_path, file))
        
        print(f"Found {len(image_files)} image files to process")
        
        for image_path in image_files:
            filename = os.path.basename(image_path)
            print(f"Processing: {filename}")
            
            # Extract GPS data
            gps_data = self.extract_gps_data(image_path)
            
            if gps_data is None:
                if config.REQUIRE_GPS_DATA:
                    print(f"  Skipping {filename} - No GPS data found")
                    continue
                else:
                    print(f"  Warning: No GPS data found for {filename}")
                    continue
            
            # Create image URL
            image_url = config.BASE_IMAGE_URL + filename
            
            # Transform coordinates
            transformed_coords = self.transform_coordinates(
                gps_data['latitude'], 
                gps_data['longitude'], 
                gps_data['elevation']
            )
            
            if transformed_coords is None:
                print(f"  Skipping {filename} - Coordinate transformation failed")
                continue
            
            image_data = {
                'filename': filename,
                'filepath': image_path,
                'latitude': gps_data['latitude'],
                'longitude': gps_data['longitude'],
                'elevation': gps_data['elevation'],
                'date_taken': gps_data['date_taken'],
                'image_url': image_url,
                'transformed_x': transformed_coords[0],
                'transformed_y': transformed_coords[1],
                'transformed_z': transformed_coords[2]
            }
            
            processed_images.append(image_data)
            
            print(f"  GPS: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f}")
            print(f"  Transformed: {transformed_coords[0]:.2f}, {transformed_coords[1]:.2f}, {transformed_coords[2]:.2f}")
        
        print(f"Successfully processed {len(processed_images)} images")
        return processed_images
    
    def save_processed_data(self, processed_images: List[Dict], output_path: str):
        """Save processed image data to JSON file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(processed_images, f, indent=2)
            print(f"Saved processed data to {output_path}")
        except Exception as e:
            print(f"Error saving processed data: {str(e)}")
