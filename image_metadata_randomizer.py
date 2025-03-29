from PIL import Image
import piexif
import random
import os
import datetime

def randomize_metadata(image_path):
    # Get the directory and filename from the input path
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    # Create output path in the same directory but with "modified_" prefix
    output_path = os.path.join(directory, f"modified_{filename}")
    
    image = Image.open(image_path)
    exif_dict = piexif.load(image.info['exif'])

    # Track changes
    changes = []
    
    # Randomize camera make and model
    random_make = f"Camera{random.randint(1, 100)}"
    random_model = f"Model{random.randint(1, 100)}"
    random_software = f"Software{random.randint(1, 100)}"
    
    exif_dict['0th'][piexif.ImageIFD.Make] = random_make.encode('ascii')
    exif_dict['0th'][piexif.ImageIFD.Model] = random_model.encode('ascii')
    
    if piexif.ImageIFD.Software in exif_dict['0th']:
        exif_dict['0th'][piexif.ImageIFD.Software] = random_software.encode('ascii')
    
    changes.append(f"Make: {random_make}")
    changes.append(f"Model: {random_model}")
    changes.append(f"Software: {random_software}")
    
    # Randomize dates
    if piexif.ImageIFD.DateTime in exif_dict['0th']:
        # Generate a random date within the last 2 years
        random_days = random.randint(1, 730)  # Up to 2 years
        random_date = (datetime.datetime.now() - datetime.timedelta(days=random_days))
        random_date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = random_date_str.encode('ascii')
        changes.append(f"DateTime: {random_date_str}")
    
    # Randomize Exif dates
    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        random_days = random.randint(1, 730)
        random_date = (datetime.datetime.now() - datetime.timedelta(days=random_days))
        random_date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = random_date_str.encode('ascii')
        changes.append(f"DateTimeOriginal: {random_date_str}")

    if 'Exif' in exif_dict and piexif.ExifIFD.DateTimeDigitized in exif_dict['Exif']:
        random_days = random.randint(1, 730)
        random_date = (datetime.datetime.now() - datetime.timedelta(days=random_days))
        random_date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = random_date_str.encode('ascii')
        changes.append(f"DateTimeDigitized: {random_date_str}")

    exif_bytes = piexif.dump(exif_dict)
    image.save(output_path, "jpeg", exif=exif_bytes)
    print(f"Saved image with randomized metadata to {output_path}")
    print("Changed metadata fields:")
    for change in changes:
        print(f"  - {change}")
    return output_path

def display_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_dict = piexif.load(image.info.get('exif', b''))
        
        print(f"Metadata for {image_path}:")
        if '0th' in exif_dict and exif_dict['0th']:
            print("Basic Image Information:")
            for tag, value in exif_dict['0th'].items():
                tag_name = piexif.TAGS['0th'].get(tag, {}).get('name', str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                print(f"  {tag_name}: {value}")
                
        if 'Exif' in exif_dict and exif_dict['Exif']:
            print("\nExif Information:")
            for tag, value in exif_dict['Exif'].items():
                tag_name = piexif.TAGS['Exif'].get(tag, {}).get('name', str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                print(f"  {tag_name}: {value}")
    except Exception as e:
        print(f"Error reading metadata: {e}")

# Use raw string for file path to avoid unicodeescape error
original_image = r"C:\Users\Ray\Pictures\20170111_163529.jpg"
output_image = randomize_metadata(original_image)

# Display metadata of both the original and modified image
print("\nOriginal image metadata:")
display_metadata(original_image)

print("\nModified image metadata:")
display_metadata(output_image) 