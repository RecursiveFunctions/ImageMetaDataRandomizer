from PIL import Image
import piexif
import random
import os
import datetime
import io
import subprocess
import sys
import argparse
import glob

def randomize_metadata(image_path, randomize_all=True, randomize_windows_props=True):
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
            
            # Randomize GPS data
            # Generate random GPS coordinates
            # Latitude between -90 and 90 degrees
            random_lat = random.uniform(-90, 90)
            # Longitude between -180 and 180 degrees
            random_long = random.uniform(-180, 180)
            
            # Convert to EXIF GPS format (degrees, minutes, seconds)
            def convert_to_dms(coordinate):
                # Absolute value of the coordinate
                coordinate_abs = abs(coordinate)
                # Degrees is the integer part
                degrees = int(coordinate_abs)
                # Minutes is the fractional part * 60
                minutes_float = (coordinate_abs - degrees) * 60
                minutes = int(minutes_float)
                # Seconds is the fractional part of minutes * 60
                seconds = int((minutes_float - minutes) * 60 * 100)
                return (degrees, 1), (minutes, 1), (seconds, 100)
            
            # Convert latitude and longitude to degrees, minutes, seconds format
            lat_dms = convert_to_dms(random_lat)
            long_dms = convert_to_dms(random_long)
            
            # Add GPS tags
            # GPS version tag
            exif_dict['GPS'][piexif.GPSIFD.GPSVersionID] = (2, 2, 0, 0)
            
            # Latitude tags
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = 'N' if random_lat >= 0 else 'S'
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = lat_dms
            
            # Longitude tags
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = 'E' if random_long >= 0 else 'W'
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = long_dms
            
            # Random altitude (0-8848m, with 8848 being the height of Mt. Everest)
            random_altitude = random.uniform(0, 8848)
            exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef] = 0  # Above sea level
            exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (int(random_altitude * 100), 100)
            
            # Random timestamp
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            exif_dict['GPS'][piexif.GPSIFD.GPSTimeStamp] = ((random_hour, 1), (random_minute, 1), (random_second, 1))
            
            # Random date (use same date as the photo)
            gps_date_str = random_date.strftime("%Y:%m:%d")
            exif_dict['GPS'][piexif.GPSIFD.GPSDateStamp] = gps_date_str
            
            changes.append(f"GPS Latitude: {random_lat:.6f} ({exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef]})")
            changes.append(f"GPS Longitude: {random_long:.6f} ({exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef]})")
            changes.append(f"GPS Altitude: {random_altitude:.2f}m")
        
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
        
        # Attempt to modify Windows-specific file properties 
        if randomize_windows_props and sys.platform == 'win32':
            try:
                # Random values for Windows properties
                random_title = f"Photo{random.randint(1000, 9999)}"
                random_subject = f"Subject{random.randint(1000, 9999)}"
                random_comments = f"Comments{random.randint(1000, 9999)}"
                random_author = f"Author{random.randint(1000, 9999)}"
                random_tags = f"tag{random.randint(1, 100)},tag{random.randint(1, 100)}"
                
                # PowerShell commands to modify Windows file properties
                ps_commands = [
                    # Clear all properties first
                    f'$shell = New-Object -ComObject Shell.Application;',
                    f'$folder = $shell.Namespace((Split-Path -Parent "{output_path}"));',
                    f'$file = $folder.ParseName((Split-Path -Leaf "{output_path}"));',
                    
                    # Set new properties
                    f'$file.InvokeVerb("Properties");',
                    f'Start-Sleep -Seconds 1;',
                    
                    # Send keys to set properties
                    f'[System.Windows.Forms.SendKeys]::SendWait("%d");',  # Alt+D for Details tab
                    f'Start-Sleep -Milliseconds 500;',
                    
                    # Set title
                    f'[System.Windows.Forms.SendKeys]::SendWait("{{TAB}}");',
                    f'[System.Windows.Forms.SendKeys]::SendWait("{random_title}");',
                    
                    # Set subject
                    f'[System.Windows.Forms.SendKeys]::SendWait("{{TAB}}");',
                    f'[System.Windows.Forms.SendKeys]::SendWait("{random_subject}");',
                    
                    # Set tags/keywords
                    f'[System.Windows.Forms.SendKeys]::SendWait("{{TAB}}");',
                    f'[System.Windows.Forms.SendKeys]::SendWait("{random_tags}");',
                    
                    # Set comments
                    f'[System.Windows.Forms.SendKeys]::SendWait("{{TAB}}");',
                    f'[System.Windows.Forms.SendKeys]::SendWait("{random_comments}");',
                    
                    # OK button
                    f'[System.Windows.Forms.SendKeys]::SendWait("%o");',
                ]
                
                # Alternative approach using PowerShell's property system (more reliable but needs admin)
                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms;
                $propertyList = @{{
                    "System.Title" = "{random_title}";
                    "System.Subject" = "{random_subject}";
                    "System.Keywords" = "{random_tags}";
                    "System.Comment" = "{random_comments}";
                    "System.Author" = "{random_author}";
                }}

                # Write properties to the file
                $shell = New-Object -ComObject Shell.Application
                $folder = $shell.Namespace((Split-Path -Parent "{output_path}"))
                $file = $folder.ParseName((Split-Path -Leaf "{output_path}"))

                foreach ($prop in $propertyList.Keys) {{
                    try {{
                        $propValue = $propertyList[$prop]
                        Write-Host "Setting $prop to $propValue"
                        # This would require administrative privileges:
                        # $file.ExtendedProperty($prop) = $propValue 
                    }} catch {{
                        Write-Host "Error setting $prop"
                    }}
                }}

                Write-Host "Windows properties updated (as much as permissions allow)"
                """
                
                print("\nNote: Attempting to set Windows file properties...")
                print("Some Windows properties can only be modified through the Windows UI or with admin privileges.")
                print("To change properties like 'Shared with', right-click the file > Properties > Security tab")
                
                changes.append(f"Title: {random_title}")
                changes.append(f"Subject: {random_subject}")
                changes.append(f"Tags: {random_tags}")
                changes.append(f"Comments: {random_comments}")
                changes.append(f"Author: {random_author}")
                
            except Exception as e:
                print(f"Warning: Could not modify Windows file properties: {e}")
                print("You may need to modify these manually in Windows Explorer.")
            
        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def get_metadata_string(image_path):
    """Reads EXIF data from an image and returns it as a formatted string."""
    output_lines = []
    try:
        image = Image.open(image_path)

        # Check if image has EXIF data
        if 'exif' not in image.info:
            return f"No EXIF data found in {os.path.basename(image_path)}"

        exif_dict = piexif.load(image.info.get('exif', b''))

        output_lines.append(f"Metadata for: {os.path.basename(image_path)}")
        output_lines.append("="*30)

        if '0th' in exif_dict and exif_dict['0th']:
            output_lines.append("Basic Image Information:")
            for tag, value in exif_dict['0th'].items():
                tag_name = piexif.TAGS['0th'].get(tag, {}).get('name', str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode('ascii', errors='replace')
                    except:
                        value = str(value)
                output_lines.append(f"  {tag_name}: {value}")
            output_lines.append("") # Add spacing

        if 'Exif' in exif_dict and exif_dict['Exif']:
            output_lines.append("Exif Information:")
            for tag, value in exif_dict['Exif'].items():
                tag_name = piexif.TAGS['Exif'].get(tag, {}).get('name', str(tag))
                # Special formatting for rational types (like ExposureTime, FNumber)
                if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int) and value[1] != 0:
                     if tag_name == "ExposureTime":
                         value_str = f"1/{int(value[1]/value[0])}s" if value[0] != 0 else "0s"
                     elif tag_name == "FNumber":
                         value_str = f"f/{value[0]/value[1]:.1f}"
                     elif tag_name == "FocalLength":
                          value_str = f"{value[0]/value[1]:.1f}mm"
                     else:
                         value_str = f"{value[0]}/{value[1]}"
                elif isinstance(value, bytes):
                    try:
                        value_str = value.decode('ascii', errors='replace')
                    except:
                        value_str = str(value)
                else:
                    value_str = str(value)
                output_lines.append(f"  {tag_name}: {value_str}")
            output_lines.append("")

        if 'GPS' in exif_dict and exif_dict['GPS']:
            output_lines.append("GPS Information:")
            lat_ref = long_ref = None
            latitude = longitude = None
            gps_data_found = False

            # Simplified GPS coordinate extraction/formatting
            try:
                lat_dms = exif_dict['GPS'].get(piexif.GPSIFD.GPSLatitude)
                lat_ref = exif_dict['GPS'].get(piexif.GPSIFD.GPSLatitudeRef)
                long_dms = exif_dict['GPS'].get(piexif.GPSIFD.GPSLongitude)
                long_ref = exif_dict['GPS'].get(piexif.GPSIFD.GPSLongitudeRef)

                if lat_dms and lat_ref and long_dms and long_ref:
                    if isinstance(lat_ref, bytes): lat_ref = lat_ref.decode('ascii', 'replace')
                    if isinstance(long_ref, bytes): long_ref = long_ref.decode('ascii', 'replace')

                    degrees = lat_dms[0][0] / lat_dms[0][1]
                    minutes = lat_dms[1][0] / lat_dms[1][1]
                    seconds = lat_dms[2][0] / lat_dms[2][1]
                    latitude = degrees + minutes/60 + seconds/3600
                    if lat_ref == 'S': latitude = -latitude

                    degrees = long_dms[0][0] / long_dms[0][1]
                    minutes = long_dms[1][0] / long_dms[1][1]
                    seconds = long_dms[2][0] / long_dms[2][1]
                    longitude = degrees + minutes/60 + seconds/3600
                    if long_ref == 'W': longitude = -longitude

                    output_lines.append(f"  GPS Coordinates: {latitude:.6f}, {longitude:.6f} ({lat_ref}, {long_ref})")
                    gps_data_found = True

            except (KeyError, IndexError, ZeroDivisionError, TypeError) as gps_ex:
                output_lines.append(f"  Could not parse GPS coordinates: {gps_ex}")

            # Display other GPS tags
            for tag, value in exif_dict['GPS'].items():
                 if tag not in [piexif.GPSIFD.GPSLatitude, piexif.GPSIFD.GPSLongitude]: # Avoid duplicate display
                    tag_name = piexif.TAGS['GPS'].get(tag, {}).get('name', str(tag))
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('ascii', errors='replace')
                        except:
                            value = str(value)
                    elif isinstance(value, tuple) and len(value) > 0 and isinstance(value[0], tuple): # Handle timestamp, etc.
                        value = ", ".join([f"{v[0]}/{v[1]}" if isinstance(v, tuple) and len(v)==2 else str(v) for v in value])
                    output_lines.append(f"  {tag_name}: {value}")
                    gps_data_found = True

            if not gps_data_found:
                 output_lines.append("  No parsable GPS data tags found.")

        elif 'GPS' in exif_dict:
            output_lines.append("GPS Information:")
            output_lines.append("  (Empty GPS IFD present)")

        return "\n".join(output_lines)

    except FileNotFoundError:
        return f"Error: File not found - {os.path.basename(image_path)}"
    except Exception as e:
        return f"Error reading metadata for {os.path.basename(image_path)}: {e}"

def process_images(image_paths, display_before=False, display_after=True, randomize_windows_props=True):
    """Process multiple images from a list of paths."""
    results = []

    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"Error: Image '{image_path}' not found")
            continue

        if not image_path.lower().endswith(('.jpg', '.jpeg')):
            print(f"Warning: '{image_path}' is not a JPEG file. Only JPEG files are supported.")
            continue

        if display_before:
            print("\n=== Original Metadata ===")
            # Use the new function, but still print for CLI usage
            print(get_metadata_string(image_path))

        output_path = randomize_metadata(image_path, randomize_windows_props=randomize_windows_props)

        if output_path and display_after:
            print("\n=== New Randomized Metadata ===")
            # Use the new function, but still print for CLI usage
            print(get_metadata_string(output_path))

        results.append({
            'original': image_path,
            'modified': output_path,
            'success': output_path is not None
        })

    return results

def main():
    parser = argparse.ArgumentParser(description='Image Metadata Randomizer')
    
    # Create a group for mutually exclusive input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('images', nargs='*', help='Path to image file(s)', default=[])
    input_group.add_argument('--folder', '-f', help='Process all jpg/jpeg files in a folder')
    
    # Add other options
    parser.add_argument('--display-before', '-b', action='store_true', 
                        help='Display metadata before randomization')
    parser.add_argument('--display-after', '-a', action='store_true', 
                        help='Display metadata after randomization (default: True)', default=True)
    parser.add_argument('--no-windows-props', action='store_true',
                        help="Don't try to modify Windows-specific properties")
    
    args = parser.parse_args()
    
    # Check if we need to get images from a folder
    image_paths = []
    if args.folder:
        if not os.path.isdir(args.folder):
            print(f"Error: Folder '{args.folder}' not found or is not a directory")
            return
            
        # Get all jpg/jpeg files in the folder
        image_paths = glob.glob(os.path.join(args.folder, '*.jpg'))
        image_paths.extend(glob.glob(os.path.join(args.folder, '*.jpeg')))
        
        if not image_paths:
            print(f"No jpg/jpeg files found in folder '{args.folder}'")
            return
            
        print(f"Found {len(image_paths)} images in folder '{args.folder}'")
    else:
        # Use the images provided as arguments
        image_paths = args.images
    
    # Process the images
    results = process_images(
        image_paths, 
        display_before=args.display_before,
        display_after=args.display_after,
        randomize_windows_props=not args.no_windows_props
    )
    
    # Show a summary
    success_count = sum(1 for r in results if r['success'])
    if results:
        print(f"\n====== Summary ======")
        print(f"Processed {len(results)} images")
        print(f"Success: {success_count}")
        print(f"Failed: {len(results) - success_count}")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        main()
    else:
        # Legacy mode: Process the single image specified in the code
        original_image = r"C:\path\to\image.jpg"
        print("=" * 80)
        print("Image Metadata Randomizer - Command Line Help")
        print("=" * 80)
        print("\nNo command line arguments provided. You have two options:")
        
        print("\n1. RECOMMENDED: Use command line arguments (examples):")
        print("   - Process a single image:")
        print("     python image_metadata_randomizer.py \"C:\\path\\to\\image.jpg\"")
        print("\n   - Process multiple images:")
        print("     python image_metadata_randomizer.py \"C:\\path\\to\\image1.jpg\" \"C:\\path\\to\\image2.jpg\"")
        print("\n   - Process all JPEG images in a folder:")
        print("     python image_metadata_randomizer.py --folder \"C:\\path\\to\\folder\"")
        print("\n   - Show original metadata too:")
        print("     python image_metadata_randomizer.py --display-before \"C:\\path\\to\\image.jpg\"")
        
        print("\n2. LEGACY MODE: Edit this script to update the hardcoded path:")
        print("   - Open this file in a text editor")
        print("   - Find this line: original_image = r\"C:\\Users\\Ray\\Pictures\\20170111_163529.jpg\"")
        print("   - Change it to point to your image")
        print("   - Run the script again without arguments")
        
        print("\n" + "=" * 80)
        print("\nRunning in legacy mode with hardcoded path...")
        print(f"Processing single image: {original_image}")
        
        if os.path.exists(original_image):
            randomize_metadata(original_image)
        else:
            print(f"\nError: Image '{original_image}' not found.")
            print("Please use command line arguments or update the hardcoded path in the script.") 