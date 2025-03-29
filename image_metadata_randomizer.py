from PIL import Image
import piexif
import random
import os
import datetime
import io

def randomize_metadata(image_path, randomize_all=True):
    # Get the directory and filename from the input path
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    # Create output path in the same directory but with "modified_" prefix
    output_path = os.path.join(directory, f"modified_{filename}")
    
    try:
        # Open the image
        print(f"Processing image: {image_path}")
        image = Image.open(image_path)
        
        # Step 1: Completely strip all metadata by saving to a new image without EXIF
        # This removes all metadata including the problematic ones Windows caches
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(list(image.getdata()))
        
        # Step 2: Create brand new EXIF data from scratch
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        changes = []
        
        # Generate random camera details
        random_make = f"Camera{random.randint(1, 100)}"
        random_model = f"Model{random.randint(1, 100)}"
        random_software = f"Software{random.randint(1, 100)}"
        
        # Basic device info that Windows Explorer will show
        exif_dict['0th'][piexif.ImageIFD.Make] = random_make.encode('ascii')
        exif_dict['0th'][piexif.ImageIFD.Model] = random_model.encode('ascii')
        exif_dict['0th'][piexif.ImageIFD.Software] = random_software.encode('ascii')
        changes.append(f"Make: {random_make}")
        changes.append(f"Model: {random_model}")
        changes.append(f"Software: {random_software}")
        
        # Add resolution info (needed for proper image display)
        exif_dict['0th'][piexif.ImageIFD.XResolution] = (72, 1)
        exif_dict['0th'][piexif.ImageIFD.YResolution] = (72, 1)
        exif_dict['0th'][piexif.ImageIFD.ResolutionUnit] = 2  # inches
        
        # Add orientation
        exif_dict['0th'][piexif.ImageIFD.Orientation] = 1  # Normal orientation
        
        if randomize_all:
            # Generate random date (within last 2 years)
            random_days = random.randint(1, 730)
            random_date = (datetime.datetime.now() - datetime.timedelta(days=random_days))
            random_date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
            
            # Add date/time 
            exif_dict['0th'][piexif.ImageIFD.DateTime] = random_date_str.encode('ascii')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = random_date_str.encode('ascii')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = random_date_str.encode('ascii')
            changes.append(f"DateTime: {random_date_str}")
            
            # Camera settings
            random_iso = random.choice([100, 200, 400, 800, 1600, 3200])
            exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings] = random_iso
            changes.append(f"ISO: {random_iso}")
            
            # Exposure settings
            exposure_options = [(1, 10), (1, 20), (1, 40), (1, 80), (1, 125), (1, 250), (1, 500), (1, 1000)]
            random_exposure = random.choice(exposure_options)
            exif_dict['Exif'][piexif.ExifIFD.ExposureTime] = random_exposure
            changes.append(f"ExposureTime: {random_exposure[0]}/{random_exposure[1]}s")
            
            # F-number (aperture)
            fnumber_options = [(28, 10), (35, 10), (40, 10), (56, 10), (80, 10)]
            random_fnumber = random.choice(fnumber_options)
            exif_dict['Exif'][piexif.ExifIFD.FNumber] = random_fnumber
            changes.append(f"FNumber: f/{random_fnumber[0]/random_fnumber[1]}")
            
            # Focal length
            focal_options = [(180, 10), (240, 10), (350, 10), (500, 10), (700, 10)]
            random_focal = random.choice(focal_options)
            exif_dict['Exif'][piexif.ExifIFD.FocalLength] = random_focal
            changes.append(f"FocalLength: {random_focal[0]/random_focal[1]}mm")
            
            # Required EXIF versions
            exif_dict['Exif'][piexif.ExifIFD.ExifVersion] = b'0230'
            exif_dict['Exif'][piexif.ExifIFD.FlashpixVersion] = b'0100'
            
            # Color space
            exif_dict['Exif'][piexif.ExifIFD.ColorSpace] = 1  # sRGB
            
            # Add title, subject, author and comments (Windows properties)
            exif_dict['0th'][piexif.ImageIFD.DocumentName] = f"Photo{random.randint(1000, 9999)}".encode('ascii')
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = f"Description{random.randint(1000, 9999)}".encode('ascii')
            exif_dict['0th'][piexif.ImageIFD.Artist] = f"Photographer{random.randint(1000, 9999)}".encode('ascii')
            exif_dict['0th'][piexif.ImageIFD.Copyright] = f"Copyright{random.randint(1000, 9999)}".encode('ascii')
            
            # Random camera ID
            random_id = ''.join(random.choice('0123456789ABCDEF') for _ in range(10))
            exif_dict['Exif'][piexif.ExifIFD.ImageUniqueID] = random_id.encode('ascii')
            changes.append(f"ImageUniqueID: {random_id}")
        
        # Dump EXIF data to bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Save the new image with the randomized EXIF data
        image_without_exif.save(output_path, "jpeg", exif=exif_bytes, quality=95)
        print(f"Saved completely new image with randomized metadata to {output_path}")
        print("Changed metadata fields:")
        for change in changes:
            print(f"  - {change}")
        
        # Create a Windows-friendly version by writing the image data directly
        with open(output_path, 'rb') as f:
            img_data = f.read()
        
        # Rewrite the file to force Windows to refresh metadata cache
        with open(output_path, 'wb') as f:
            f.write(img_data)
            
        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def display_metadata(image_path):
    try:
        image = Image.open(image_path)
        
        # Check if image has EXIF data
        if 'exif' not in image.info:
            print(f"No EXIF data found in {image_path}")
            return
            
        exif_dict = piexif.load(image.info.get('exif', b''))
        
        print(f"Metadata for {image_path}:")
        if '0th' in exif_dict and exif_dict['0th']:
            print("Basic Image Information:")
            for tag, value in exif_dict['0th'].items():
                tag_name = piexif.TAGS['0th'].get(tag, {}).get('name', str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode('ascii', errors='replace')
                    except:
                        value = str(value)
                print(f"  {tag_name}: {value}")
                
        if 'Exif' in exif_dict and exif_dict['Exif']:
            print("\nExif Information:")
            for tag, value in exif_dict['Exif'].items():
                tag_name = piexif.TAGS['Exif'].get(tag, {}).get('name', str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode('ascii', errors='replace')
                    except:
                        value = str(value)
                print(f"  {tag_name}: {value}")
                
        if 'GPS' in exif_dict and exif_dict['GPS']:
            print("\nGPS Information:")
            print("  GPS data present")
        elif 'GPS' in exif_dict:
            print("\nGPS Information:")
            print("  No GPS data")
    except Exception as e:
        print(f"Error reading metadata: {e}")

# File path for the original image
original_image = r"C:\Users\Ray\Pictures\20170111_163529.jpg"

# Randomize metadata and save a new image
output_image = randomize_metadata(original_image, randomize_all=True)

if output_image:
    # Display metadata of both the original and modified image
    print("\nOriginal image metadata:")
    display_metadata(original_image)

    print("\nModified image metadata:")
    display_metadata(output_image)
    
    print("\nPLEASE NOTE: To view the changes in Windows Explorer:")
    print("1. This version creates a completely new image with randomized metadata")
    print("2. To refresh Windows metadata cache, try right-click > Properties > Details tab")
    print("3. The modified image is saved with 'modified_' prefix in the same folder as the original")
    print("4. For stubborn cases, you might need to restart Windows Explorer or reboot your system") 