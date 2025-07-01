"""
Utility functions for the image GPS to IFC marker exporter
"""

import os
import json
from typing import Dict, List, Any


def validate_image_data(image_data: Dict) -> bool:
    """
    Validate that image data contains required fields
    
    Args:
        image_data: Dictionary with image metadata
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['filename', 'latitude', 'longitude', 'transformed_x', 'transformed_y', 'transformed_z']
    
    for field in required_fields:
        if field not in image_data:
            return False
        if image_data[field] is None:
            return False
    
    return True


def load_processed_images(file_path: str) -> List[Dict]:
    """
    Load processed image data from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of image data dictionaries
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading processed images: {str(e)}")
        return []


def get_supported_image_files(folder_path: str, extensions: List[str]) -> List[str]:
    """
    Get list of supported image files in a folder
    
    Args:
        folder_path: Path to folder
        extensions: List of supported extensions
        
    Returns:
        List of image file paths
    """
    image_files = []
    
    if not os.path.exists(folder_path):
        return image_files
    
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in extensions):
            image_files.append(os.path.join(folder_path, file))
    
    return image_files


def create_image_url(filename: str, base_url: str) -> str:
    """
    Create full URL for an image file
    
    Args:
        filename: Image filename
        base_url: Base URL for hosting
        
    Returns:
        Full image URL
    """
    return f"{base_url.rstrip('/')}/{filename}"


def format_coordinates(x: float, y: float, z: float, precision: int = 2) -> str:
    """
    Format coordinates for display
    
    Args:
        x, y, z: Coordinate values
        precision: Decimal precision
        
    Returns:
        Formatted coordinate string
    """
    return f"({x:.{precision}f}, {y:.{precision}f}, {z:.{precision}f})"


def print_processing_summary(processed_images: List[Dict]):
    """
    Print a summary of processed images
    
    Args:
        processed_images: List of processed image data
    """
    print(f"\n=== Processing Summary ===")
    print(f"Total images processed: {len(processed_images)}")
    
    if processed_images:
        # Calculate bounds
        x_coords = [img['transformed_x'] for img in processed_images]
        y_coords = [img['transformed_y'] for img in processed_images]
        z_coords = [img['transformed_z'] for img in processed_images]
        
        print(f"Coordinate bounds (EPSG:5110):")
        print(f"  X: {min(x_coords):.2f} to {max(x_coords):.2f}")
        print(f"  Y: {min(y_coords):.2f} to {max(y_coords):.2f}")
        print(f"  Z: {min(z_coords):.2f} to {max(z_coords):.2f}")
        
        # Count images with dates
        with_dates = sum(1 for img in processed_images if img.get('date_taken'))
        print(f"Images with date information: {with_dates}/{len(processed_images)}")
        
        # Count images with elevation
        with_elevation = sum(1 for img in processed_images if img.get('elevation', 0) != 0)
        print(f"Images with elevation data: {with_elevation}/{len(processed_images)}")
    
    print(f"========================\n")
