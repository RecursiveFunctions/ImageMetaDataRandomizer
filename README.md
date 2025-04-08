# 📷 Image Metadata Randomizer

A Python utility to randomize EXIF metadata in photos for enhanced privacy and security when sharing images online.

## 🔍 Overview

The Image Metadata Randomizer is designed to protect your privacy by replacing revealing EXIF metadata in your digital photos with randomly generated information. Digital photos often contain sensitive information like:

- Device make and model
- Exact date and time of capture
- Location data (GPS coordinates) 
- Serial numbers and unique device identifiers
- Camera settings that might identify your equipment

This tool creates a new copy of your image with completely randomized metadata, making it safer to share online.

## ✨ Features

- **Graphical User Interface (GUI)**: Easy-to-use interface with drag-and-drop support.
- **Complete Metadata Replacement**: Creates a new image with freshly generated metadata
- **Random Camera Information**: Generates fake camera make, model, and software info
- **Date/Time Randomization**: Randomizes all timestamps within the last two years
- **GPS Randomization**: Changes location data to random coordinates
- **Camera Settings Randomization**: Randomizes ISO, exposure time, aperture, etc.
- **Windows Explorer Compatible**: Creates metadata that displays correctly in Windows
- **Image Quality Preservation**: Maintains the visual quality of your original image
- **Enhanced Privacy**: Removes potentially identifying information
- **Non-destructive**: Original images remain untouched

## 🛠️ Installation

1. Ensure you have Python 3.6+ installed
2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # On Windows
   source venv/bin/activate     # On macOS/Linux
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt # Installs Pillow, piexif, ExifRead, PySide6
   ```

## 📋 Usage

### Graphical User Interface (Recommended)

The easiest way to use the tool is via the graphical interface:

1.  Ensure you have installed the dependencies (including PySide6) as shown above.
2.  Run the GUI script:
    ```bash
    python metadata_gui.py
    ```
3.  The application window will appear:
    - **Drag and Drop**: Drag image files or folders containing images directly onto the designated area.
    - **Select Buttons**: Click "Select Files" to browse for individual image files or "Select Folder" to choose a directory.
    - **File List**: Selected items will appear in the list.
    - **Randomize**: Click the "Randomize Metadata" button to process all images in the list.
4.  Modified images will be saved in their original directories with a `modified_` prefix.

### Command Line Interface

Alternatively, you can still use the command line interface:

```bash
# Process a single image
python image_metadata_randomizer.py "C:\path\to\your\image.jpg"

# Process multiple images
python image_metadata_randomizer.py "C:\path\to\image1.jpg" "C:\path\to\image2.jpg"

# Process all images in a folder
python image_metadata_randomizer.py --folder "C:\path\to\folder"
```

### Manual Script Editing

Alternatively, you can edit the script directly:

1. Update the `original_image` path variable to point to your image:
   ```python
   original_image = r"C:\path\to\your\image.jpg"
   ```

2. Run the script:
   ```bash
   python image_metadata_randomizer.py
   ```

3. The randomized image will be saved in the same directory as your original with a "modified_" prefix.

## 🔧 How It Works

The tool works in several steps:

1. **Complete Stripping**: First, the original image data is read into a new blank image, removing all metadata
2. **New Metadata Creation**: Fresh, randomly generated metadata is created from scratch
3. **Basic Info Randomization**: Camera make, model, and software information is randomized
4. **Image Data Preservation**: The pixel data is preserved exactly as in the original
5. **Windows Compatibility**: Special steps ensure Windows Explorer displays the new metadata correctly
6. **Windows Properties**: Additional metadata used by Windows is randomized (Title, Subject, etc.)

## 📊 Randomized Metadata Fields

| Category | Fields |
|----------|--------|
| **Basic Info** | Make, Model, Software |
| **Date & Time** | DateTime, DateTimeOriginal, DateTimeDigitized |
| **Camera Settings** | ISO, ExposureTime, FNumber, FocalLength |
| **Windows Fields** | Title, Subject, Author, Copyright, Tags |
| **Image IDs** | ImageUniqueID |

## 🔄 Output Example

```
Processing image: C:\Users\Ray\Pictures\example.jpg
Saved completely new image with randomized metadata to C:\Users\Ray\Pictures\modified_example.jpg
Changed metadata fields:
  - Make: Camera96
  - Model: Model62
  - Software: Software54
  - DateTime: 2023:05:27 11:41:28
  - ISO: 800
  - ExposureTime: 1/125s
  - FNumber: f/2.8
  - FocalLength: 18.0mm
  - ImageUniqueID: 95E4BAD386
```

## ⚠️ Limitations

- "Shared with" and other Windows security permissions are file system attributes, not EXIF metadata. These need to be modified manually.
- Some Windows metadata caching issues may require refreshing the Explorer cache or restarting Windows Explorer.
- GPS coordinates are randomized to any valid global coordinate which may be in the ocean or other unlikely locations.

## 🔐 Privacy Considerations

- Always verify the metadata has been properly changed before sharing sensitive images.
- Use a dedicated metadata viewer like ExifTool or IrfanView to verify changes.
- Windows Explorer properties view may cache metadata; use "Details" tab to confirm changes.

## 📝 License

This project is provided as open-source software. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or suggest new features.

## 🚀 Planned Features

- **Custom Randomization Profiles**: Ability to select which metadata fields to randomize
- **Batch Processing Enhancements**: Progress bar and more detailed reporting for CLI and GUI
- **Additional Image Format Support**: Extending beyond JPEG to support PNG, TIFF, and other formats

---

*This tool is designed for legitimate privacy protection when sharing images online. Please use responsibly.* 