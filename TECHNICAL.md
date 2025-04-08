# Technical Documentation: Image Metadata Randomizer

This document provides detailed technical information about the implementation of the Image Metadata Randomizer utility.

## Code Architecture

The Image Metadata Randomizer is built around three main functions:

1. `randomize_metadata()`: The core function that handles the metadata randomization process
2. `display_metadata()`: A utility function to display and compare metadata before and after randomization
3. `process_images()`: Handles batch processing of multiple images

## Dependencies

| Library | Purpose |
|---------|---------|
| **PIL (Pillow)** | Image handling and basic operations |
| **piexif** | Low-level EXIF metadata manipulation |
| **os** | File path handling |
| **datetime** | Date generation for timestamp randomization |
| **random** | Random value generation |
| **io** | Binary data handling |
| **subprocess** (optional) | For external command execution |
| **sys** | Platform detection |
| **argparse** | Command-line argument parsing |
| **glob** | File pattern matching for folder processing |

## Core Function: `randomize_metadata()`

```python
def randomize_metadata(image_path, randomize_all=True, randomize_windows_props=True):
```

### Parameters

- `image_path`: Path to the original image file
- `randomize_all`: Boolean flag to enable/disable full metadata randomization
- `randomize_windows_props`: Boolean flag to enable/disable Windows-specific property handling

### Implementation Details

The function follows a systematic approach to metadata randomization:

#### 1. File Path Handling

```python
directory = os.path.dirname(image_path)
filename = os.path.basename(image_path)
output_path = os.path.join(directory, f"modified_{filename}")
```

This ensures output files are created in the same directory as the input, with a distinguishable prefix.

#### 2. Complete Metadata Stripping

```python
image_without_exif = Image.new(image.mode, image.size)
image_without_exif.putdata(list(image.getdata()))
```

Instead of trying to modify existing metadata (which can be error-prone due to caching), we create a completely new image with identical pixel data but no metadata.

#### 3. Building New Metadata

```python
exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
```

We create a fresh EXIF dictionary with the standard structure expected by piexif.

#### 4. Basic Metadata Fields

```python
exif_dict['0th'][piexif.ImageIFD.Make] = random_make.encode('ascii')
exif_dict['0th'][piexif.ImageIFD.Model] = random_model.encode('ascii')
exif_dict['0th'][piexif.ImageIFD.Software] = random_software.encode('ascii')
```

These fields represent the most basic device identification information.

#### 5. Advanced Metadata Fields

When `randomize_all=True`, additional fields are randomized:

- **Date/Time Fields**: All three standard timestamp fields (creation, original, digitized)
- **Camera Settings**: ISO, exposure time, aperture, focal length
- **Technical Fields**: EXIF version, FlashPixVersion, color space
- **Windows-specific Fields**: Document name, description, artist, copyright

#### 6. Windows-specific Property Handling

When `randomize_windows_props=True` and on a Windows platform, the code attempts to set Windows-specific file properties that aren't stored in standard EXIF fields.

#### 7. File Output

```python
image_without_exif.save(output_path, "jpeg", exif=exif_bytes, quality=95)
```

Saves with high quality to preserve image details.

#### 8. Cache Busting

```python
with open(output_path, 'rb') as f:
    img_data = f.read()
with open(output_path, 'wb') as f:
    f.write(img_data)
```

This read/write cycle helps ensure Windows refreshes its metadata cache.

## Utility Function: `display_metadata()`

```python
def display_metadata(image_path):
```

This function provides a user-friendly display of metadata fields, organized by category:

- Basic Image Information (from the '0th' IFD)
- EXIF Information (from the 'Exif' IFD)
- GPS Information (presence check only)

## EXIF Dictionary Structure

The piexif library uses a nested dictionary structure for EXIF data:

```
{
  "0th": {...},       # Primary image data (Make, Model, etc.)
  "Exif": {...},      # EXIF-specific tags (camera settings)
  "GPS": {...},       # GPS/location data
  "1st": {...},       # Thumbnail metadata
  "thumbnail": None   # Thumbnail image data
}
```

## Randomization Logic

The code uses several techniques to ensure high-quality randomization:

### 1. Camera Identification

Make and Model fields are set to `Camera###` and `Model###` with random numbers.

### 2. Date Randomization

```python
random_days = random.randint(1, 730)  # Up to 2 years back
random_date = (datetime.datetime.now() - datetime.timedelta(days=random_days))
```

This creates a random date within the last two years.

### 3. Camera Settings

Settings are selected from realistic predefined options:

```python
# ISO values
random_iso = random.choice([100, 200, 400, 800, 1600, 3200])

# Exposure time values
exposure_options = [(1, 10), (1, 20), (1, 40), (1, 80), (1, 125), (1, 250), (1, 500), (1, 1000)]

# Aperture values (f-numbers)
fnumber_options = [(28, 10), (35, 10), (40, 10), (56, 10), (80, 10)]

# Focal length values
focal_options = [(180, 10), (240, 10), (350, 10), (500, 10), (700, 10)]
```

### 4. GPS Coordinates

The tool randomizes GPS data using a comprehensive approach:

```python
# Generate random GPS coordinates
random_lat = random.uniform(-90, 90)          # Latitude between -90 and 90 degrees
random_long = random.uniform(-180, 180)       # Longitude between -180 and 180 degrees
random_altitude = random.uniform(0, 8848)     # Altitude between 0 and height of Mt. Everest
```

Converting decimal coordinates to EXIF's degree-minute-second format:

```python
def convert_to_dms(coordinate):
    coordinate_abs = abs(coordinate)
    degrees = int(coordinate_abs)
    minutes_float = (coordinate_abs - degrees) * 60
    minutes = int(minutes_float)
    seconds = int((minutes_float - minutes) * 60 * 100)
    return (degrees, 1), (minutes, 1), (seconds, 100)
```

The GPS data includes:
- Latitude and longitude in DMS format
- Hemisphere references (N/S for latitude, E/W for longitude)
- Altitude (with reference above sea level)
- GPS timestamp (randomized hour, minute, second)
- GPS datestamp (synchronized with the photo's randomized date)

## Error Handling

The code implements a comprehensive try-except pattern:

1. The main function is wrapped in a try-except block to catch any unexpected errors
2. The metadata display function has its own try-except for robustness
3. Windows-specific property handling has separate error handling to prevent failure if these operations fail

## Windows Compatibility

Special attention is given to Windows compatibility:

1. ASCII encoding for all string values
2. Binary data handling with proper encoding/decoding
3. Orientation field set to standard value (1)
4. Resolution fields explicitly set
5. Error-resilient property display code

## Command Line Interface

The utility now supports a flexible command-line interface through the `argparse` library:

```python
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
```

### Command-Line Options

| Option | Short Flag | Description |
|--------|------------|-------------|
| `images` | - | One or more image paths to process |
| `--folder` | `-f` | Process all JPG/JPEG files in the specified folder |
| `--display-before` | `-b` | Show original metadata before randomization |
| `--display-after` | `-a` | Show new metadata after randomization (default: True) |
| `--no-windows-props` | - | Skip Windows-specific property modifications |

### Usage Examples

```bash
# Process a single image
python image_metadata_randomizer.py "C:\path\to\your\image.jpg"

# Process multiple images
python image_metadata_randomizer.py "C:\path\to\image1.jpg" "C:\path\to\image2.jpg"

# Process all images in a folder
python image_metadata_randomizer.py --folder "C:\path\to\folder"

# Process an image but don't show metadata after
python image_metadata_randomizer.py "C:\path\to\image.jpg" --display-after=False

# Process an image and show metadata before and after
python image_metadata_randomizer.py "C:\path\to\image.jpg" --display-before
```

## Batch Processing Implementation

The batch processing functionality is implemented in the `process_images()` function:

```python
def process_images(image_paths, display_before=False, display_after=True):
    """Process multiple images from a list of paths."""
    results = []
    
    for image_path in image_paths:
        # Validate file
        if not os.path.exists(image_path):
            print(f"Error: Image '{image_path}' not found")
            continue
            
        if not image_path.lower().endswith(('.jpg', '.jpeg')):
            print(f"Warning: '{image_path}' is not a JPEG file. Only JPEG files are supported.")
            continue
        
        # Process the file
        output_path = randomize_metadata(image_path)
        
        # Track results
        results.append({
            'original': image_path,
            'modified': output_path,
            'success': output_path is not None
        })
    
    return results
```

The function:
1. Validates each image path
2. Checks that the image is a supported JPEG file
3. Calls the core `randomize_metadata()` function on each valid image
4. Tracks the results of each operation
5. Returns a summary of the processing

## Folder Processing

When the `--folder` option is used, the tool uses the `glob` module to find all JPEG files in the specified directory:

```python
# Get all jpg/jpeg files in the folder
image_paths = glob.glob(os.path.join(args.folder, '*.jpg'))
image_paths.extend(glob.glob(os.path.join(args.folder, '*.jpeg')))
```

This enables processing of entire collections of images with a single command.

## Legacy Mode

For backward compatibility, the tool still supports the old hardcoded path method:

```python
if len(sys.argv) > 1:
    main()
else:
    # Legacy mode: Process the single image specified in the code
    original_image = r"C:\Users\Ray\Pictures\20170111_163529.jpg"
    # ...
```

If no command-line arguments are provided, the tool falls back to using the hardcoded path in the script.

## Graphical User Interface (GUI)

A GUI has been developed using PySide6 to provide a more user-friendly way to interact with the randomizer.

### File: `metadata_gui.py`

- **Framework**: PySide6 (Qt for Python)
- **Main Window**: `MetadataRandomizerGUI` (inherits from `QWidget`)
- **Key Components**:
    - `DragDropArea`: A custom `QLabel` subclass to handle drag-and-drop operations for files and folders.
    - `QListWidget`: Displays the list of selected files and folders.
    - `QPushButton`: Buttons for selecting files ("Select Files"), selecting folders ("Select Folder"), and initiating the process ("Randomize Metadata").
    - `QFileDialog`: Used for browsing and selecting files/folders.
    - `QVBoxLayout`, `QHBoxLayout`: Used for organizing widgets in the UI.
    - `QLabel`: Used for text labels and the status bar.
- **Functionality**:
    - Allows users to select individual image files or entire folders containing images.
    - Supports dragging and dropping files/folders directly onto the application window.
    - Collects all image files from selected items (recursively searching within selected folders).
    - Calls the core `randomize_metadata` function for each identified image file.
    - Provides user feedback via status messages and dialog boxes (e.g., success, error messages).
    - Basic styling is applied for a cleaner appearance.

### Interaction with Core Logic

The GUI's `start_randomization` method gathers the list of target image files from the `QListWidget` (using the `get_all_image_files` helper method) and then iterates through this list, calling `image_metadata_randomizer.randomize_metadata` for each file.

## Future Enhancements

Potential improvements to the codebase:

1. **Graphical User Interface (GUI)**: A user-friendly interface for non-technical users
2. **Custom randomization profiles**: Allow users to select which metadata fields to randomize
3. **Integration with ExifTool**: For more comprehensive metadata handling
4. **Preservation of selected metadata fields**: Option to keep certain metadata intact
5. **Smart GPS randomization**: Generate coordinates only in plausible locations (land vs. water)
6. **Additional format support**: Extend beyond JPEG to PNG, TIFF, and other formats 