from PIL import Image
import piexif
import random
import os

def randomize_metadata(image_path):
    # Get the directory and filename from the input path
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    # Create output path in the same directory but with "modified_" prefix
    output_path = os.path.join(directory, f"modified_{filename}")
    
    image = Image.open(image_path)
    exif_dict = piexif.load(image.info['exif'])

    # Randomize some metadata fields
    exif_dict['0th'][piexif.ImageIFD.Make] = f"Camera{random.randint(1, 100)}"
    exif_dict['0th'][piexif.ImageIFD.Model] = f"Model{random.randint(1, 100)}"

    exif_bytes = piexif.dump(exif_dict)
    image.save(output_path, "jpeg", exif=exif_bytes)
    print(f"Saved image with randomized metadata to {output_path}")
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