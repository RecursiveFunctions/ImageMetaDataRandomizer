#!/usr/bin/env python3
"""
Test script for GPS data randomization in Image Metadata Randomizer.

This script:
1. Creates a test image with known GPS data
2. Processes it with image_metadata_randomizer.py
3. Verifies that the GPS data was replaced with randomized values
"""

import os
import sys
import tempfile
from PIL import Image
import piexif
from image_metadata_randomizer import randomize_metadata, display_metadata

def create_test_image_with_gps():
    """Create a test image with known GPS data."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    test_image_path = os.path.join(temp_dir, "test_gps_image.jpg")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Create EXIF data with GPS information
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    # Add some basic EXIF data
    exif_dict['0th'][piexif.ImageIFD.Make] = "TestCamera".encode('ascii')
    exif_dict['0th'][piexif.ImageIFD.Model] = "TestModel".encode('ascii')
    
    # Add GPS data - this is the Eiffel Tower location (48.8584° N, 2.2945° E)
    # Convert decimal coordinates to DMS format
    lat = 48.8584
    lon = 2.2945
    
    # Convert to DMS format
    def decimal_to_dms(coord):
        degrees = int(coord)
        minutes_float = (coord - degrees) * 60
        minutes = int(minutes_float)
        seconds = int((minutes_float - minutes) * 60 * 100)  # multiply by 100 for precision
        return (degrees, 1), (minutes, 1), (seconds, 100)
    
    lat_dms = decimal_to_dms(lat)
    lon_dms = decimal_to_dms(lon)
    
    # Set GPS tags
    exif_dict['GPS'][piexif.GPSIFD.GPSVersionID] = (2, 2, 0, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = "N"
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = lat_dms
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = "E"  
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = lon_dms
    exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (330, 1)  # 330 meters
    exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef] = 0  # Above sea level
    
    # Save image with EXIF data
    exif_bytes = piexif.dump(exif_dict)
    img.save(test_image_path, "jpeg", exif=exif_bytes, quality=95)
    
    print(f"Created test image with GPS data at: {test_image_path}")
    return test_image_path

def extract_gps_data(image_path):
    """Extract GPS data from an image and return as a dictionary."""
    try:
        img = Image.open(image_path)
        if 'exif' not in img.info:
            return None
            
        exif_dict = piexif.load(img.info.get('exif', b''))
        if 'GPS' not in exif_dict or not exif_dict['GPS']:
            return None
            
        gps_data = {}
        
        # Extract latitude
        if piexif.GPSIFD.GPSLatitude in exif_dict['GPS'] and piexif.GPSIFD.GPSLatitudeRef in exif_dict['GPS']:
            lat_dms = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
            lat_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef]
            if isinstance(lat_ref, bytes):
                lat_ref = lat_ref.decode('ascii', errors='replace')
                
            try:
                lat_degrees = lat_dms[0][0] / lat_dms[0][1]
                lat_minutes = lat_dms[1][0] / lat_dms[1][1]
                lat_seconds = lat_dms[2][0] / lat_dms[2][1]
                latitude = lat_degrees + lat_minutes/60 + lat_seconds/3600
                if lat_ref == 'S':
                    latitude = -latitude
                gps_data['latitude'] = latitude
                gps_data['latitude_ref'] = lat_ref
            except (IndexError, ZeroDivisionError, TypeError):
                pass
        
        # Extract longitude
        if piexif.GPSIFD.GPSLongitude in exif_dict['GPS'] and piexif.GPSIFD.GPSLongitudeRef in exif_dict['GPS']:
            lon_dms = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
            lon_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef]
            if isinstance(lon_ref, bytes):
                lon_ref = lon_ref.decode('ascii', errors='replace')
                
            try:
                lon_degrees = lon_dms[0][0] / lon_dms[0][1]
                lon_minutes = lon_dms[1][0] / lon_dms[1][1]
                lon_seconds = lon_dms[2][0] / lon_dms[2][1]
                longitude = lon_degrees + lon_minutes/60 + lon_seconds/3600
                if lon_ref == 'W':
                    longitude = -longitude
                gps_data['longitude'] = longitude
                gps_data['longitude_ref'] = lon_ref
            except (IndexError, ZeroDivisionError, TypeError):
                pass
        
        # Extract altitude
        if piexif.GPSIFD.GPSAltitude in exif_dict['GPS']:
            try:
                alt = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
                altitude = alt[0] / alt[1]
                alt_ref = exif_dict['GPS'].get(piexif.GPSIFD.GPSAltitudeRef, 0)
                gps_data['altitude'] = altitude
                gps_data['altitude_ref'] = alt_ref
            except (IndexError, ZeroDivisionError, TypeError):
                pass
        
        return gps_data
    except Exception as e:
        print(f"Error extracting GPS data: {e}")
        return None

def test_gps_randomization():
    """Test that GPS data is properly randomized."""
    # Create a test image with GPS data
    original_image = create_test_image_with_gps()
    
    # Extract original GPS data
    original_gps = extract_gps_data(original_image)
    if not original_gps:
        print("ERROR: Failed to create test image with GPS data")
        return False
    
    print("\n=== Original GPS Data ===")
    if 'latitude' in original_gps and 'longitude' in original_gps:
        print(f"Latitude: {original_gps['latitude']:.6f}° {original_gps['latitude_ref']}")
        print(f"Longitude: {original_gps['longitude']:.6f}° {original_gps['longitude_ref']}")
    
    if 'altitude' in original_gps:
        print(f"Altitude: {original_gps['altitude']:.2f}m")
    
    # Process the image with randomize_metadata
    print("\n=== Processing Image ===")
    processed_image = randomize_metadata(original_image)
    
    # Extract GPS data from processed image
    processed_gps = extract_gps_data(processed_image)
    if not processed_gps:
        print("ERROR: Processed image does not contain GPS data")
        return False
    
    print("\n=== Randomized GPS Data ===")
    if 'latitude' in processed_gps and 'longitude' in processed_gps:
        print(f"Latitude: {processed_gps['latitude']:.6f}° {processed_gps['latitude_ref']}")
        print(f"Longitude: {processed_gps['longitude']:.6f}° {processed_gps['longitude_ref']}")
    
    if 'altitude' in processed_gps:
        print(f"Altitude: {processed_gps['altitude']:.2f}m")
    
    # Verify that GPS data has been changed
    gps_changed = True
    reasons = []
    
    if 'latitude' in original_gps and 'latitude' in processed_gps:
        if abs(original_gps['latitude'] - processed_gps['latitude']) < 0.0001:
            gps_changed = False
            reasons.append("Latitude was not changed significantly")
    
    if 'longitude' in original_gps and 'longitude' in processed_gps:
        if abs(original_gps['longitude'] - processed_gps['longitude']) < 0.0001:
            gps_changed = False
            reasons.append("Longitude was not changed significantly")
    
    if 'altitude' in original_gps and 'altitude' in processed_gps:
        if abs(original_gps['altitude'] - processed_gps['altitude']) < 0.1:
            gps_changed = False
            reasons.append("Altitude was not changed significantly")
    
    # Print test results
    print("\n=== Test Results ===")
    if gps_changed:
        print("✅ PASS: GPS data was successfully randomized")
        for field in ['latitude', 'longitude', 'altitude']:
            if field in original_gps and field in processed_gps:
                print(f"  - {field.capitalize()}: {original_gps[field]:.6f} → {processed_gps[field]:.6f}")
    else:
        print("❌ FAIL: GPS data was not properly randomized")
        for reason in reasons:
            print(f"  - {reason}")
    
    # Clean up
    try:
        os.remove(original_image)
        os.remove(processed_image)
        os.rmdir(os.path.dirname(original_image))
        print("\nTest files cleaned up")
    except Exception as e:
        print(f"\nWarning: Could not clean up test files: {e}")
    
    return gps_changed

if __name__ == "__main__":
    print("=== GPS Randomization Test ===")
    print("Testing if GPS data is properly randomized...")
    
    success = test_gps_randomization()
    
    if success:
        print("\nSUCCESS: GPS randomization is working correctly")
        sys.exit(0)
    else:
        print("\nFAILURE: GPS randomization test failed")
        sys.exit(1) 