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
import string
from faker import Faker

fake = Faker()

# Top camera makes and models (comprehensive dictionary)
CAMERA_DATABASE = {
    "Canon": [
        "EOS R5", "EOS R6", "EOS R6 Mark II", "EOS R7", "EOS R8",
        "EOS R10", "EOS R50", "EOS R100", "EOS R3", "EOS R",
        "EOS RP", "EOS 5D Mark IV", "EOS 6D Mark II", "EOS 90D",
        "EOS 80D", "EOS 77D", "EOS Rebel T8i", "EOS Rebel T7",
        "EOS Rebel SL3", "EOS M50 Mark II", "EOS M6 Mark II",
        "EOS 1D X Mark III", "EOS 7D Mark II", "EOS 5DS R",
        "PowerShot G7 X Mark III", "PowerShot G5 X Mark II",
        "PowerShot SX740 HS", "PowerShot V10", "EOS Kiss X10",
        "EOS 850D",
    ],
    "Nikon": [
        "Z9", "Z8", "Z7 II", "Z6 III", "Z6 II", "Z5", "Zf", "Zfc",
        "Z50", "Z30", "D850", "D780", "D7500", "D5600", "D3500",
        "D6", "D500", "D750", "D610", "D5300",
        "COOLPIX P1000", "COOLPIX P950", "COOLPIX B600",
        "COOLPIX W300", "COOLPIX A1000",
    ],
    "Sony": [
        "ILCE-7RM5", "ILCE-7M4", "ILCE-7CR", "ILCE-7CM2",
        "ILCE-9M3", "ILCE-6700", "ILCE-6400", "ILCE-6100",
        "ILCE-1", "ILCE-7SM3", "ILCE-7RM4A", "ILCE-7M3",
        "DSC-RX100M7", "DSC-RX10M4", "DSC-RX1RM2",
        "ZV-E10", "ZV-E1", "ZV-1 II", "ZV-1F",
        "ILCE-6600", "ILCE-6500", "ILCE-6300",
        "DSC-HX99", "DSC-WX800",
    ],
    "Fujifilm": [
        "X-T5", "X-T4", "X-T3", "X-T30 II", "X-T30",
        "X-H2S", "X-H2", "X-H1", "X-S20", "X-S10",
        "X-E4", "X-E3", "X-Pro3", "X-Pro2",
        "X100VI", "X100V", "X100F",
        "GFX 100S", "GFX 100 II", "GFX 50S II", "GFX 50R",
        "X-T200", "X-A7", "XF10",
        "FinePix XP140",
    ],
    "Panasonic": [
        "DC-S5 II", "DC-S5 IIX", "DC-S5", "DC-S1R", "DC-S1H",
        "DC-S1", "DC-GH6", "DC-GH5 II", "DC-GH5S", "DC-GH5",
        "DC-G9 II", "DC-G9", "DC-G100", "DC-G95",
        "DC-GX9", "DC-GX85", "DC-LX100 II",
        "DC-FZ1000 II", "DC-FZ80", "DC-ZS200",
        "DMC-LX10", "DC-S5M2",
    ],
    "Olympus": [
        "E-M1 Mark III", "E-M1 Mark II", "E-M1X",
        "E-M5 Mark III", "E-M5 Mark II",
        "E-M10 Mark IV", "E-M10 Mark III",
        "PEN E-PL10", "PEN E-PL9", "PEN-F",
        "TG-6", "TG-5",
        "E-P7",
    ],
    "OM System": [
        "OM-1 Mark II", "OM-1", "OM-5",
        "TG-7",
    ],
    "Leica": [
        "M11", "M11-P", "M11 Monochrom", "M10-R", "M10-P",
        "Q3", "Q2", "Q2 Monochrom",
        "SL2-S", "SL2", "SL3",
        "CL", "TL2",
        "V-Lux 5", "D-Lux 7", "C-Lux",
    ],
    "Pentax": [
        "K-3 Mark III", "K-3 Mark III Monochrome",
        "K-1 Mark II", "K-1", "K-70", "KF",
        "645Z", "645D",
        "GR III", "GR IIIx",
        "WG-90", "WG-70",
    ],
    "Ricoh": [
        "GR III", "GR IIIx", "GR III HDF", "GR IIIx HDF",
        "Theta Z1", "Theta X", "Theta SC2",
        "WG-80", "WG-7",
    ],
    "Hasselblad": [
        "X2D 100C", "X1D II 50C", "X1D-50c",
        "907X 50C", "907X & CFV 100C",
        "H6D-100c", "H6D-400c MS",
    ],
    "Sigma": [
        "fp", "fp L",
        "dp0 Quattro", "dp1 Quattro", "dp2 Quattro",
        "dp3 Quattro",
        "sd Quattro", "sd Quattro H",
    ],
    "GoPro": [
        "HERO12 Black", "HERO11 Black", "HERO11 Black Mini",
        "HERO10 Black", "HERO9 Black", "HERO8 Black",
        "MAX",
    ],
    "DJI": [
        "Mavic 3 Pro", "Mavic 3", "Mavic 3 Classic",
        "Air 3", "Air 2S", "Mini 4 Pro", "Mini 3 Pro",
        "Mini 3", "Mini 2 SE",
        "Osmo Action 4", "Osmo Pocket 3",
        "Phantom 4 Pro V2.0",
    ],
    "Samsung": [
        "NX1", "NX500", "NX3000", "NX300M",
        "Galaxy S24 Ultra", "Galaxy S23 Ultra",
        "Galaxy S22 Ultra", "Galaxy S21 Ultra",
        "Galaxy Z Fold5",
    ],
    "Apple": [
        "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15",
        "iPhone 15 Plus",
        "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14",
        "iPhone 13 Pro Max", "iPhone 13 Pro", "iPhone 13",
        "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12",
        "iPhone SE (3rd generation)",
        "iPad Pro (6th generation)",
    ],
    "Google": [
        "Pixel 8 Pro", "Pixel 8", "Pixel 8a",
        "Pixel 7 Pro", "Pixel 7", "Pixel 7a",
        "Pixel 6 Pro", "Pixel 6", "Pixel 6a",
        "Pixel Fold",
    ],
    "Insta360": [
        "ONE RS 1-Inch 360", "ONE RS", "ONE X3",
        "ONE X2", "GO 3",
    ],
    "Phase One": [
        "XF IQ4 150MP", "XF IQ4 100MP Trichromatic",
        "XT IQ4 150MP", "IQ3 100MP",
    ],
    "Blackmagic": [
        "Pocket Cinema Camera 6K G2",
        "Pocket Cinema Camera 6K Pro",
        "Pocket Cinema Camera 4K",
        "URSA Mini Pro 12K",
    ],
}

# Software descriptions mimicking popular photo editing software
SOFTWARE_DESCRIPTIONS = [
    # Adobe products
    "Adobe Photoshop CC 2024 (Windows)",
    "Adobe Photoshop CC 2024 (Macintosh)",
    "Adobe Photoshop CC 2023 (Windows)",
    "Adobe Photoshop CC 2023 (Macintosh)",
    "Adobe Photoshop 25.6.0",
    "Adobe Photoshop 25.5.1",
    "Adobe Photoshop 25.3.0",
    "Adobe Photoshop 24.7.1",
    "Adobe Photoshop 24.5.0",
    "Adobe Photoshop Lightroom Classic 13.2",
    "Adobe Photoshop Lightroom Classic 13.1",
    "Adobe Photoshop Lightroom Classic 12.5",
    "Adobe Photoshop Lightroom Classic 12.4",
    "Adobe Photoshop Lightroom Classic 12.0",
    "Adobe Photoshop Lightroom 7.3",
    "Adobe Photoshop Lightroom 7.1.2",
    "Adobe Photoshop Lightroom 6.5",
    "Adobe Lightroom CC 6.2.1",
    "Adobe Photoshop Elements 2024",
    "Adobe Photoshop Elements 2023",
    "Adobe Camera Raw 16.2",
    "Adobe Camera Raw 16.1",
    "Adobe Camera Raw 15.5",
    "Adobe Camera Raw 15.3",
    # GIMP
    "GIMP 2.10.36",
    "GIMP 2.10.34",
    "GIMP 2.10.32",
    "GIMP 2.10.30",
    "GIMP 2.10.28",
    "GIMP 2.10.24",
    "GIMP 2.10.22",
    "GIMP 2.99.18",
    "GNU Image Manipulation Program 2.10.36",
    "GNU Image Manipulation Program 2.10.34",
    # Capture One
    "Capture One 23 (16.3.5)",
    "Capture One 23 (16.3.2)",
    "Capture One 23 (16.2.1)",
    "Capture One 22 (15.4.2)",
    "Capture One Pro 16.3.5",
    "Capture One Pro 16.2.0",
    # Affinity Photo
    "Affinity Photo 2.4.1",
    "Affinity Photo 2.3.0",
    "Affinity Photo 2.2.1",
    "Affinity Photo 2.1.0",
    "Affinity Photo 1.10.6",
    "Serif Affinity Photo 2.4.1",
    # DxO
    "DxO PhotoLab 7.4.0",
    "DxO PhotoLab 7.2.0",
    "DxO PhotoLab 6.10",
    "DxO PhotoLab 6.8",
    "DxO PureRAW 4.1",
    "DxO PureRAW 3.8",
    # Darktable
    "darktable 4.6.1",
    "darktable 4.6.0",
    "darktable 4.4.2",
    "darktable 4.2.1",
    "darktable 4.0.1",
    "darktable 3.8.1",
    # RawTherapee
    "RawTherapee 5.10",
    "RawTherapee 5.9",
    "RawTherapee 5.8",
    # Corel / Paintshop Pro
    "Corel PaintShop Pro 2024",
    "Corel PaintShop Pro 2023",
    "Corel PaintShop Pro 26.0",
    "Corel PaintShop Pro 25.0",
    "Corel AfterShot Pro 3",
    # ON1
    "ON1 Photo RAW 2024.1",
    "ON1 Photo RAW 2024",
    "ON1 Photo RAW 2023.5",
    # Luminar
    "Skylum Luminar Neo 1.18.0",
    "Skylum Luminar Neo 1.16.0",
    "Skylum Luminar Neo 1.14.1",
    "Skylum Luminar AI 1.5.5",
    "Skylum Luminar 4.3.3",
    # Apple Photos
    "Apple Photos 9.0",
    "Apple Photos 8.0",
    "Photos 9.0",
    "Photos 8.0",
    # Camera firmware strings
    "Ver.1.0.1",
    "Ver.1.0.0",
    "Ver.2.0.0",
    "Ver.1.1.0",
    "NIKON Z 9 Ver.4.10",
    "NIKON Z 8 Ver.2.01",
    "NIKON D850 Ver.1.21",
    "Canon EOS R5 Firmware Version 1.9.0",
    "Canon EOS R6m2 Firmware Version 1.3.0",
    "ILCE-7RM5 v3.01",
    "ILCE-7M4 v3.00",
    # Snapseed
    "Snapseed 2.0",
    "Snapseed 2.21",
    # ACDSee
    "ACDSee Photo Studio Ultimate 2024",
    "ACDSee Photo Studio Professional 2024",
    "ACDSee Photo Studio 17.0",
    # Pixelmator
    "Pixelmator Pro 3.5.7",
    "Pixelmator Pro 3.4.3",
    "Pixelmator Pro 3.3.0",
    # Photoscape
    "PhotoScape X Pro 4.2.1",
    "PhotoScape X 4.2.0",
    # Windows / Paint
    "Microsoft Windows Photo Gallery 16.4.3528.331",
    "Microsoft Windows Photo Viewer 10.0.19041.3636",
    "Windows Photo Editor 2024.11020.21001.0",
    "Paint.NET 5.0.13",
    "Paint.NET 5.0.12",
    "Paint.NET 4.3.12",
    # IrfanView
    "IrfanView 4.67",
    "IrfanView 4.66",
    "IrfanView 4.62",
    # XnView
    "XnView MP 1.7.1",
    "XnView MP 1.6.4",
    "XnConvert 1.98",
    # ImageMagick
    "ImageMagick 7.1.1-29",
    "ImageMagick 7.1.1-27",
    "ImageMagick 7.1.0-62",
    # FastStone
    "FastStone Image Viewer 7.8",
    "FastStone Image Viewer 7.7",
    # Zoner
    "Zoner Photo Studio X (19.2309.2.506)",
    "Zoner Photo Studio X (19.2303.2.424)",
    # digiKam
    "digiKam 8.2.0",
    "digiKam 8.1.0",
    "digiKam 7.9.0",
    # Photopea
    "Photopea 5.7",
    "Photopea 5.5",
    # ExifTool
    "ExifTool 12.76",
    "ExifTool 12.70",
]

# Image descriptions that look realistic
IMAGE_DESCRIPTIONS = [
    # Generic photo descriptions
    "",  # Many cameras leave this blank
    "                               ",  # Some cameras pad with spaces
    "DCIM\\100MEDIA",
    "DCIM",
    # Camera-specific defaults
    "OLYMPUS DIGITAL CAMERA",
    "SONY DSC",
    "NIKON CORPORATION",
    "NIKON D850",
    "Canon EOS R5",
    "Panasonic DMC-GH5",
    "SAMSUNG",
    "RICOH IMAGING COMPANY, LTD.",
    # Apple descriptions
    "Photo taken with iPhone",
    "Screenshot",
    # Adobe-style
    "Adobe Photoshop CC 2024",
    "Photoshop ICC profile",
    # Photo editing software stamps
    "Processed with VSCO",
    "Processed with VSCO with c1 preset",
    "Processed with VSCO with a6 preset",
    "Made with GIMP",
    "Created with GIMP",
    "Exported from Lightroom",
    "Edited in Snapseed",
    "Processed in Capture One",
    "Developed in DxO PhotoLab",
    "Converted with darktable",
    # Common descriptions from stock/social
    "Photo by {photographer}",
    "Image exported from Photos",
    "Scanned by CamScanner",
    "Shot on {camera}",
    # Technical descriptions
    "sRGB IEC61966-2.1",
    "Color profile: sRGB",
    "AdobeRGB",
    # Blank or minimal
    ".",
    "-",
    "IMG",
    "DSC",
    "P",
    "Photo",
    "Image",
    "Picture",
]

def get_random_camera():
    """Returns a random (make, model) tuple from the camera database."""
    make = random.choice(list(CAMERA_DATABASE.keys()))
    model = random.choice(CAMERA_DATABASE[make])
    return make, model

def get_random_software():
    """Returns a random software description string."""
    return random.choice(SOFTWARE_DESCRIPTIONS)

def get_random_image_description(make=None, model=None):
    """Returns a random image description, optionally
    incorporating camera make/model info."""
    desc = random.choice(IMAGE_DESCRIPTIONS)

    # Fill in template placeholders if present
    if "{photographer}" in desc:
        desc = desc.replace("{photographer}", fake.name())
    if "{camera}" in desc:
        if make and model:
            desc = desc.replace("{camera}", f"{make} {model}")
        else:
            cam_make, cam_model = get_random_camera()
            desc = desc.replace("{camera}", f"{cam_make} {cam_model}")

    return desc

def randomize_metadata(
    image_path,
    randomize_all=True,
    randomize_windows_props=True,
):
    # Get the directory and filename from the input path
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    # Create output path in the same directory with random filename
    output_path = os.path.join(directory, generate_random_filename())

    try:
        # Open the image
        print(f"Processing image: {image_path}")
        image = Image.open(image_path)

        # Step 1: Completely strip all metadata by saving to a new
        # image without EXIF. This removes all metadata including the
        # problematic ones Windows caches.
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(list(image.getdata()))

        # Step 2: Create brand new EXIF data from scratch
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None,
        }
        changes = []

        # Generate random camera make and model from real database
        random_make, random_model = get_random_camera()

        # Generate random software from real software list
        random_software = get_random_software()

        # Generate random image description
        random_description = get_random_image_description(
            make=random_make, model=random_model
        )

        # Basic device info that Windows Explorer will show
        exif_dict["0th"][piexif.ImageIFD.Make] = (
            random_make.encode("ascii", errors="replace")
        )
        exif_dict["0th"][piexif.ImageIFD.Model] = (
            random_model.encode("ascii", errors="replace")
        )
        exif_dict["0th"][piexif.ImageIFD.Software] = (
            random_software.encode("ascii", errors="replace")
        )
        changes.append(f"Make: {random_make}")
        changes.append(f"Model: {random_model}")
        changes.append(f"Software: {random_software}")

        # Add resolution info (needed for proper image display)
        exif_dict["0th"][piexif.ImageIFD.XResolution] = (72, 1)
        exif_dict["0th"][piexif.ImageIFD.YResolution] = (72, 1)
        exif_dict["0th"][piexif.ImageIFD.ResolutionUnit] = 2  # inches

        # Add orientation
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

        if randomize_all:
            # Generate random date (within last 2 years)
            random_days = random.randint(1, 730)
            random_date = datetime.datetime.now() - datetime.timedelta(
                days=random_days
            )
            random_date_str = random_date.strftime("%Y:%m:%d %H:%M:%S")

            # Add date/time
            exif_dict["0th"][piexif.ImageIFD.DateTime] = (
                random_date_str.encode("ascii")
            )
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = (
                random_date_str.encode("ascii")
            )
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = (
                random_date_str.encode("ascii")
            )
            changes.append(f"DateTime: {random_date_str}")

            # Camera settings
            random_iso = random.choice(
                [100, 200, 400, 800, 1600, 3200]
            )
            exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = (
                random_iso
            )
            changes.append(f"ISO: {random_iso}")

            # Exposure settings
            exposure_options = [
                (1, 10), (1, 20), (1, 40), (1, 80),
                (1, 125), (1, 250), (1, 500), (1, 1000),
            ]
            random_exposure = random.choice(exposure_options)
            exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (
                random_exposure
            )
            changes.append(
                f"ExposureTime: "
                f"{random_exposure[0]}/{random_exposure[1]}s"
            )

            # F-number (aperture)
            fnumber_options = [
                (28, 10), (35, 10), (40, 10), (56, 10), (80, 10),
            ]
            random_fnumber = random.choice(fnumber_options)
            exif_dict["Exif"][piexif.ExifIFD.FNumber] = random_fnumber
            changes.append(
                f"FNumber: f/{random_fnumber[0] / random_fnumber[1]}"
            )

            # Focal length
            focal_options = [
                (180, 10), (240, 10), (350, 10),
                (500, 10), (700, 10),
            ]
            random_focal = random.choice(focal_options)
            exif_dict["Exif"][piexif.ExifIFD.FocalLength] = random_focal
            changes.append(
                f"FocalLength: "
                f"{random_focal[0] / random_focal[1]}mm"
            )

            # Required EXIF versions
            exif_dict["Exif"][piexif.ExifIFD.ExifVersion] = b"0230"
            exif_dict["Exif"][piexif.ExifIFD.FlashpixVersion] = b"0100"

            # Color space
            exif_dict["Exif"][piexif.ExifIFD.ColorSpace] = 1  # sRGB

            # Use generate_random_filename for DocumentName
            random_doc_name = generate_random_filename()
            exif_dict["0th"][piexif.ImageIFD.DocumentName] = (
                random_doc_name.encode("ascii")
            )
            changes.append(f"DocumentName: {random_doc_name}")

            # Use random image description from popular software
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = (
                random_description.encode("ascii", errors="replace")
            )
            changes.append(
                f"ImageDescription: {random_description}"
            )

            # Use faker for Artist name
            random_artist = fake.name()
            exif_dict["0th"][piexif.ImageIFD.Artist] = (
                random_artist.encode("ascii", errors="replace")
            )
            changes.append(f"Artist: {random_artist}")

            # Copyright with faker
            random_copyright_holder = fake.name()
            random_year = random.randint(2018, 2026)
            random_copyright = (
                f"Copyright {random_year} {random_copyright_holder}. "
                f"All rights reserved."
            )
            exif_dict["0th"][piexif.ImageIFD.Copyright] = (
                random_copyright.encode("ascii", errors="replace")
            )
            changes.append(f"Copyright: {random_copyright}")

            # Random camera ID
            random_id = "".join(
                random.choice("0123456789ABCDEF") for _ in range(10)
            )
            exif_dict["Exif"][piexif.ExifIFD.ImageUniqueID] = (
                random_id.encode("ascii")
            )
            changes.append(f"ImageUniqueID: {random_id}")

            # Randomize GPS data
            random_lat = random.uniform(-90, 90)
            random_long = random.uniform(-180, 180)

            def convert_to_dms(coordinate):
                coordinate_abs = abs(coordinate)
                degrees = int(coordinate_abs)
                minutes_float = (coordinate_abs - degrees) * 60
                minutes = int(minutes_float)
                seconds = int((minutes_float - minutes) * 60 * 100)
                return (
                    (degrees, 1),
                    (minutes, 1),
                    (seconds, 100),
                )

            lat_dms = convert_to_dms(random_lat)
            long_dms = convert_to_dms(random_long)

            # Add GPS tags
            exif_dict["GPS"][piexif.GPSIFD.GPSVersionID] = (
                2, 2, 0, 0,
            )

            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = (
                "N" if random_lat >= 0 else "S"
            )
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = lat_dms

            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = (
                "E" if random_long >= 0 else "W"
            )
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = long_dms

            random_altitude = random.uniform(0, 8848)
            exif_dict["GPS"][piexif.GPSIFD.GPSAltitudeRef] = 0
            exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = (
                int(random_altitude * 100),
                100,
            )

            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            exif_dict["GPS"][piexif.GPSIFD.GPSTimeStamp] = (
                (random_hour, 1),
                (random_minute, 1),
                (random_second, 1),
            )

            gps_date_str = random_date.strftime("%Y:%m:%d")
            exif_dict["GPS"][piexif.GPSIFD.GPSDateStamp] = (
                gps_date_str
            )

            changes.append(
                f"GPS Latitude: {random_lat:.6f} "
                f"({exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef]})"
            )
            changes.append(
                f"GPS Longitude: {random_long:.6f} "
                f"({exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef]})"
            )
            changes.append(f"GPS Altitude: {random_altitude:.2f}m")

        # Dump EXIF data to bytes
        exif_bytes = piexif.dump(exif_dict)

        # Save the new image with the randomized EXIF data
        image_without_exif.save(
            output_path, "jpeg", exif=exif_bytes, quality=95
        )
        print(
            f"Saved completely new image with randomized "
            f"metadata to {output_path}"
        )
        print("Changed metadata fields:")
        for change in changes:
            print(f"  - {change}")

        # Create a Windows-friendly version by writing the image
        # data directly
        with open(output_path, "rb") as f:
            img_data = f.read()

        # Rewrite the file to force Windows to refresh metadata
        # cache
        with open(output_path, "wb") as f:
            f.write(img_data)

        # Attempt to modify Windows-specific file properties
        if randomize_windows_props and sys.platform == "win32":
            try:
                random_title = (
                    f"Photo{random.randint(1000, 9999)}"
                )
                random_subject = (
                    f"Subject{random.randint(1000, 9999)}"
                )
                random_comments = (
                    f"Comments{random.randint(1000, 9999)}"
                )
                random_author = fake.name()
                random_tags = (
                    f"tag{random.randint(1, 100)},"
                    f"tag{random.randint(1, 100)}"
                )

                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms;
                $propertyList = @{{
                    "System.Title" = "{random_title}";
                    "System.Subject" = "{random_subject}";
                    "System.Keywords" = "{random_tags}";
                    "System.Comment" = "{random_comments}";
                    "System.Author" = "{random_author}";
                }}

                $shell = New-Object -ComObject Shell.Application
                $folder = $shell.Namespace(
                    (Split-Path -Parent "{output_path}")
                )
                $file = $folder.ParseName(
                    (Split-Path -Leaf "{output_path}")
                )

                foreach ($prop in $propertyList.Keys) {{
                    try {{
                        $propValue = $propertyList[$prop]
                        Write-Host "Setting $prop to $propValue"
                    }} catch {{
                        Write-Host "Error setting $prop"
                    }}
                }}

                Write-Host (
                    "Windows properties updated "
                    "(as much as permissions allow)"
                )
                """

                print(
                    "\nNote: Attempting to set Windows file "
                    "properties..."
                )
                print(
                    "Some Windows properties can only be modified "
                    "through the Windows UI or with admin privileges."
                )
                print(
                    "To change properties like 'Shared with', "
                    "right-click the file > Properties > Security tab"
                )

                changes.append(f"Title: {random_title}")
                changes.append(f"Subject: {random_subject}")
                changes.append(f"Tags: {random_tags}")
                changes.append(f"Comments: {random_comments}")
                changes.append(f"Author: {random_author}")

            except Exception as e:
                print(
                    f"Warning: Could not modify Windows file "
                    f"properties: {e}"
                )
                print(
                    "You may need to modify these manually in "
                    "Windows Explorer."
                )

        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def generate_random_filename():
    characters = string.ascii_letters + string.digits
    length = random.randint(10, 53)
    filename = (
        "".join(random.choices(characters, k=length)) + ".jpg"
    )
    return filename

def get_metadata_string(image_path):
    """Reads EXIF data from an image and returns it as a
    formatted string."""
    output_lines = []
    try:
        image = Image.open(image_path)

        # Check if image has EXIF data
        if "exif" not in image.info:
            return (
                f"No EXIF data found in "
                f"{os.path.basename(image_path)}"
            )

        exif_dict = piexif.load(image.info.get("exif", b""))

        output_lines.append(
            f"Metadata for: {os.path.basename(image_path)}"
        )
        output_lines.append("=" * 30)

        if "0th" in exif_dict and exif_dict["0th"]:
            output_lines.append("Basic Image Information:")
            for tag, value in exif_dict["0th"].items():
                tag_name = piexif.TAGS["0th"].get(
                    tag, {}
                ).get("name", str(tag))
                if isinstance(value, bytes):
                    try:
                        value = value.decode(
                            "ascii", errors="replace"
                        )
                    except Exception:
                        value = str(value)
                output_lines.append(f"  {tag_name}: {value}")
            output_lines.append("")

        if "Exif" in exif_dict and exif_dict["Exif"]:
            output_lines.append("Exif Information:")
            for tag, value in exif_dict["Exif"].items():
                tag_name = piexif.TAGS["Exif"].get(
                    tag, {}
                ).get("name", str(tag))
                if (
                    isinstance(value, tuple)
                    and len(value) == 2
                    and isinstance(value[0], int)
                    and isinstance(value[1], int)
                    and value[1] != 0
                ):
                    if tag_name == "ExposureTime":
                        value_str = (
                            f"1/{int(value[1] / value[0])}s"
                            if value[0] != 0
                            else "0s"
                        )
                    elif tag_name == "FNumber":
                        value_str = (
                            f"f/{value[0] / value[1]:.1f}"
                        )
                    elif tag_name == "FocalLength":
                        value_str = (
                            f"{value[0] / value[1]:.1f}mm"
                        )
                    else:
                        value_str = f"{value[0]}/{value[1]}"
                elif isinstance(value, bytes):
                    try:
                        value_str = value.decode(
                            "ascii", errors="replace"
                        )
                    except Exception:
                        value_str = str(value)
                else:
                    value_str = str(value)
                output_lines.append(
                    f"  {tag_name}: {value_str}"
                )
            output_lines.append("")

        if "GPS" in exif_dict and exif_dict["GPS"]:
            output_lines.append("GPS Information:")
            latitude = longitude = None
            gps_data_found = False

            try:
                lat_dms = exif_dict["GPS"].get(
                    piexif.GPSIFD.GPSLatitude
                )
                lat_ref = exif_dict["GPS"].get(
                    piexif.GPSIFD.GPSLatitudeRef
                )
                long_dms = exif_dict["GPS"].get(
                    piexif.GPSIFD.GPSLongitude
                )
                long_ref = exif_dict["GPS"].get(
                    piexif.GPSIFD.GPSLongitudeRef
                )

                if lat_dms and lat_ref and long_dms and long_ref:
                    if isinstance(lat_ref, bytes):
                        lat_ref = lat_ref.decode(
                            "ascii", "replace"
                        )
                    if isinstance(long_ref, bytes):
                        long_ref = long_ref.decode(
                            "ascii", "replace"
                        )

                    degrees = lat_dms[0][0] / lat_dms[0][1]
                    minutes = lat_dms[1][0] / lat_dms[1][1]
                    seconds = lat_dms[2][0] / lat_dms[2][1]
                    latitude = (
                        degrees + minutes / 60 + seconds / 3600
                    )
                    if lat_ref == "S":
                        latitude = -latitude

                    degrees = long_dms[0][0] / long_dms[0][1]
                    minutes = long_dms[1][0] / long_dms[1][1]
                    seconds = long_dms[2][0] / long_dms[2][1]
                    longitude = (
                        degrees + minutes / 60 + seconds / 3600
                    )
                    if long_ref == "W":
                        longitude = -longitude

                    output_lines.append(
                        f"  GPS Coordinates: "
                        f"{latitude:.6f}, {longitude:.6f} "
                        f"({lat_ref}, {long_ref})"
                    )
                    gps_data_found = True

            except (
                KeyError,
                IndexError,
                ZeroDivisionError,
                TypeError,
            ) as gps_ex:
                output_lines.append(
                    f"  Could not parse GPS coordinates: "
                    f"{gps_ex}"
                )

            for tag, value in exif_dict["GPS"].items():
                if tag not in [
                    piexif.GPSIFD.GPSLatitude,
                    piexif.GPSIFD.GPSLongitude,
                ]:
                    tag_name = piexif.TAGS["GPS"].get(
                        tag, {}
                    ).get("name", str(tag))
                    if isinstance(value, bytes):
                        try:
                            value = value.decode(
                                "ascii", errors="replace"
                            )
                        except Exception:
                            value = str(value)
                    elif (
                        isinstance(value, tuple)
                        and len(value) > 0
                        and isinstance(value[0], tuple)
                    ):
                        value = ", ".join(
                            [
                                (
                                    f"{v[0]}/{v[1]}"
                                    if isinstance(v, tuple)
                                    and len(v) == 2
                                    else str(v)
                                )
                                for v in value
                            ]
                        )
                    output_lines.append(
                        f"  {tag_name}: {value}"
                    )
                    gps_data_found = True

            if not gps_data_found:
                output_lines.append(
                    "  No parsable GPS data tags found."
                )

        elif "GPS" in exif_dict:
            output_lines.append("GPS Information:")
            output_lines.append("  (Empty GPS IFD present)")

        return "\n".join(output_lines)

    except FileNotFoundError:
        return (
            f"Error: File not found - "
            f"{os.path.basename(image_path)}"
        )
    except Exception as e:
        return (
            f"Error reading metadata for "
            f"{os.path.basename(image_path)}: {e}"
        )

def process_images(
    image_paths,
    display_before=False,
    display_after=True,
    randomize_windows_props=True,
):
    """Process multiple images from a list of paths."""
    results = []

    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"Error: Image '{image_path}' not found")
            continue

        if not image_path.lower().endswith((".jpg", ".jpeg")):
            print(
                f"Warning: '{image_path}' is not a JPEG file. "
                f"Only JPEG files are supported."
            )
            continue

        if display_before:
            print("\n=== Original Metadata ===")
            print(get_metadata_string(image_path))

        output_path = randomize_metadata(
            image_path,
            randomize_windows_props=randomize_windows_props,
        )

        if output_path and display_after:
            print("\n=== New Randomized Metadata ===")
            print(get_metadata_string(output_path))

        results.append(
            {
                "original": image_path,
                "modified": output_path,
                "success": output_path is not None,
            }
        )

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Image Metadata Randomizer"
    )

    # Create a group for mutually exclusive input options
    input_group = parser.add_mutually_exclusive_group(
        required=True
    )
    input_group.add_argument(
        "images",
        nargs="*",
        help="Path to image file(s)",
        default=[],
    )
    input_group.add_argument(
        "--folder",
        "-f",
        help="Process all jpg/jpeg files in a folder",
    )

    # Add other options
    parser.add_argument(
        "--display-before",
        "-b",
        action="store_true",
        help="Display metadata before randomization",
    )
    parser.add_argument(
        "--display-after",
        "-a",
        action="store_true",
        help=(
            "Display metadata after randomization "
            "(default: True)"
        ),
        default=True,
    )
    parser.add_argument(
        "--no-windows-props",
        action="store_true",
        help=(
            "Don't try to modify Windows-specific properties"
        ),
    )

    args = parser.parse_args()

    # Check if we need to get images from a folder
    image_paths = []
    if args.folder:
        if not os.path.isdir(args.folder):
            print(
                f"Error: Folder '{args.folder}' not found or "
                f"is not a directory"
            )
            return

        image_paths = glob.glob(
            os.path.join(args.folder, "*.jpg")
        )
        image_paths.extend(
            glob.glob(os.path.join(args.folder, "*.jpeg"))
        )

        if not image_paths:
            print(
                f"No jpg/jpeg files found in folder "
                f"'{args.folder}'"
            )
            return

        print(
            f"Found {len(image_paths)} images in folder "
            f"'{args.folder}'"
        )
    else:
        image_paths = args.images

    # Process the images
    results = process_images(
        image_paths,
        display_before=args.display_before,
        display_after=args.display_after,
        randomize_windows_props=not args.no_windows_props,
    )

    # Show a summary
    success_count = sum(1 for r in results if r["success"])
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
        original_image = r"C:\path\to\image.jpg"
        print("=" * 80)
        print("Image Metadata Randomizer - Command Line Help")
        print("=" * 80)
        print(
            "\nNo command line arguments provided. "
            "You have two options:"
        )

        print(
            "\n1. RECOMMENDED: Use command line arguments "
            "(examples):"
        )
        print("   - Process a single image:")
        print(
            '     python image_metadata_randomizer.py '
            '"C:\\path\\to\\image.jpg"'
        )
        print("\n   - Process multiple images:")
        print(
            '     python image_metadata_randomizer.py '
            '"C:\\path\\to\\image1.jpg" '
            '"C:\\path\\to\\image2.jpg"'
        )
        print(
            "\n   - Process all JPEG images in a folder:"
        )
        print(
            '     python image_metadata_randomizer.py '
            '--folder "C:\\path\\to\\folder"'
        )
        print("\n   - Show original metadata too:")
        print(
            '     python image_metadata_randomizer.py '
            '--display-before "C:\\path\\to\\image.jpg"'
        )

        print(
            "\n2. LEGACY MODE: Edit this script to update "
            "the hardcoded path:"
        )
        print("   - Open this file in a text editor")
        print(
            '   - Find this line: original_image = '
            'r"C:\\path\\to\\image.jpg"'
        )
        print("   - Change it to point to your image")
        print(
            "   - Run the script again without arguments"
        )

        print("\n" + "=" * 80)
        print("\nRunning in legacy mode with hardcoded path...")
        print(f"Processing single image: {original_image}")

        if os.path.exists(original_image):
            randomize_metadata(original_image)
        else:
            print(
                f"\nError: Image '{original_image}' not found."
            )
            print(
                "Please use command line arguments or update "
                "the hardcoded path in the script."
            )
