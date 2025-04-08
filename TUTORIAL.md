# 📚 Image Metadata Randomizer Tutorial

This tutorial will guide you through using the Image Metadata Randomizer to protect your privacy when sharing photos online.

## 🏁 Quick Start Guide

### Step 1: Install the Required Software

1. Install Python from [python.org](https://python.org/downloads) (version 3.6 or higher)
2. Open a command prompt or terminal
3. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows: `.\venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
5. Install the required libraries:
   ```
   pip install -r requirements.txt # Installs Pillow, piexif, ExifRead, PySide6
   ```

### Step 2: Run the GUI (Recommended)

1. With your virtual environment activated, run:
   ```
   python metadata_gui.py
   ```
2. The application window will open.
3. **Add Files/Folders**:
    - Drag image files or folders directly onto the "Drag and Drop" area.
    - *Or*, click "Select Files" or "Select Folder" to browse.
4. **Review List**: Check the list to ensure the correct items are added.
5. **Randomize**: Click the "Randomize Metadata" button.
6. **Done**: Modified images are saved in their original locations with a `modified_` prefix.

### Alternative: Use the Command Line

If you prefer the command line:

1. Run the script providing the image path(s):
   ```
   python image_metadata_randomizer.py "C:\Users\YourName\Pictures\vacation.jpg"
   ```
   Replace the path with the path to your image in quotes.

2. You'll see output showing the metadata changes.
3. The new image is saved in the same folder as your original with a "modified_" prefix.

### Command Line Batch Processing

To process multiple images at once via command line:

```
python image_metadata_randomizer.py "C:\Path\To\Image1.jpg" "C:\Path\To\Image2.jpg"
```

Or to process all images in a folder:

```
python image_metadata_randomizer.py --folder "C:\Users\YourName\Pictures\Vacation"
```

### Old Method: Edit the Script Directly (Not Recommended)

Previously, you could edit the script directly:

1. Open `image_metadata_randomizer.py` in a text editor
2. Locate this line near the bottom:
   ```python
   original_image = r"C:\Users\Ray\Pictures\20170111_163529.jpg"
   ```
3. Replace it with the path to your image:
   ```python
   original_image = r"C:\Users\YourName\Pictures\vacation.jpg"
   ```
   (Keep the `r` prefix before the path string - it's important!)

## 🔄 Before and After Comparison

### Original Metadata

When you share a photo directly from your camera or phone, it typically contains information like this:

```
Metadata for C:\Users\YourName\Pictures\vacation.jpg:
Basic Image Information:
  Make: Apple
  Model: iPhone 13 Pro
  Software: iOS 15.4.1
  DateTime: 2023:06:15 14:22:33
  
Exif Information:
  DateTimeOriginal: 2023:06:15 14:22:33
  DateTimeDigitized: 2023:06:15 14:22:33
  GPSLatitude: 34.052235
  GPSLongitude: -118.243683
  ...
```

### After Randomization

After running the script, the metadata looks like this:

```
Metadata for C:\Users\YourName\Pictures\modified_vacation.jpg:
Basic Image Information:
  Make: Camera42
  Model: Model78
  Software: Software23
  DateTime: 2022:11:03 09:15:47
  
Exif Information:
  DateTimeOriginal: 2022:11:03 09:15:47
  DateTimeDigitized: 2022:11:03 09:15:47
  ExposureTime: 1/250s
  FNumber: f/4.0
  ...
```

## 📋 Verifying the Changes

### Using Windows Explorer

1. Right-click on your modified image
2. Select "Properties"
3. Click on the "Details" tab
4. You should see the randomized information

![Windows Properties Example](https://i.imgur.com/example.png)

### Using Another Image Viewer

If you have IrfanView, XnView, or another metadata-capable image viewer:

1. Open your modified image
2. Look for a menu option like "Image Properties" or "EXIF Information"
3. Verify the metadata has been changed

## 🚧 Troubleshooting

### Windows Still Shows Old Metadata

If Windows Explorer still displays the original metadata:

1. Try right-clicking the file > Properties > Details tab
2. Click "Remove Properties and Personal Information" at the bottom
3. Choose "Create a copy with all possible properties removed"
4. Run the randomizer on this new copy

### Other Issues

- Ensure you're using the `r` prefix before file paths to avoid escape character issues
- Check that your image actually contains EXIF data (some web images don't)
- Make sure the image file isn't read-only or locked by another application

## 🛡️ Best Practices

1. **Always verify** the metadata has been properly changed before sharing
2. Consider using batch processing for multiple images
3. Keep the original files in a secure location
4. Use dedicated privacy tools like this one before uploading to social media
5. Remember that some platforms may strip metadata anyway, but don't rely on this behavior

## 🔍 What to Look For

When checking if your metadata has been properly randomized, focus on these key fields:

- **Device information**: Make, Model, Software
- **Timestamps**: All date/time fields 
- **GPS data**: Should be completely removed
- **Unique identifiers**: SerialNumber, ImageUniqueID, etc.

By following this tutorial, you'll be able to better protect your privacy when sharing images online by removing potentially sensitive metadata. 