from PIL import Image
import piexif
import random

def randomize_metadata(image_path):
    image = Image.open(image_path)
    exif_dict = piexif.load(image.info['exif'])

    # Randomize some metadata fields
    exif_dict['0th'][piexif.ImageIFD.Make] = f"Camera{random.randint(1, 100)}"
    exif_dict['0th'][piexif.ImageIFD.Model] = f"Model{random.randint(1, 100)}"

    exif_bytes = piexif.dump(exif_dict)
    image.save("output.jpg", "jpeg", exif=exif_bytes)

# Use raw string for file path to avoid unicodeescape error
randomize_metadata(r"C:\Users\Ray\Pictures\20170111_163529.jpg") 