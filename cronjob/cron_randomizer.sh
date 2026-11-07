#!/bin/bash

# --- Configuration ---
SOURCE_DIR="$HOME/Nextcloud/Misc/Randomizer"
DEST_DIR="$HOME/Nextcloud/Misc/Randomized"
PYTHON_SCRIPT="$HOME/Scripts/exif_randomizer.py"
LOG_FILE="$HOME/Logs/randomizer.log"
# Use mktemp to create a secure temporary file for the file list
ORIGINAL_FILES_LIST=$(mktemp)

# --- Cleanup function to remove temp file on exit ---
cleanup() {
    log "Cleaning up temporary file list."
    rm -f "$ORIGINAL_FILES_LIST"
}
# Register the cleanup function to run on script exit (success or error)
trap cleanup EXIT

# --- Main Script ---

# Create the log directory and destination directory if they don't exist
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$DEST_DIR"

# Function to log messages with a timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "--- Starting script execution ---"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    log "ERROR: Source directory '$SOURCE_DIR' not found. Exiting."
    exit 1
fi

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log "ERROR: Python script '$PYTHON_SCRIPT' not found. Exiting."
    exit 1
fi

# --- Step 1: Find and convert PNG files to JPG ---
log "Scanning for PNG files in '$SOURCE_DIR'..."
found_png=false

# Use find to locate all .png files, case-insensitively
find "$SOURCE_DIR" -type f -iname "*.png" -print0 | while IFS= read -r -d '' png_file; do
    found_png=true
    jpg_file="${png_file%.png}.jpg" # Create the new .jpg filename

    log "Converting '$png_file' to '$jpg_file'..."
    if convert "$png_file" "$jpg_file"; then
        log "Successfully converted '$png_file'. Deleting original."
        rm "$png_file" # Delete the original PNG after successful conversion
    else
        log "ERROR: Failed to convert '$png_file'. Original file will not be deleted."
    fi
done

if [ "$found_png" = false ]; then
    log "No PNG files found to convert."
fi

# --- Step 2: Create a list of all files currently in the directory ---
log "Creating a list of all files currently in '$SOURCE_DIR'..."
# Find all files and directories (excluding the top-level dir itself) and save their paths to the temp file
find "$SOURCE_DIR" -mindepth 1 -print0 > "$ORIGINAL_FILES_LIST"
log "File list created."

# --- Step 3: Run the Python script and log its output ---
log "Running Python script: '$PYTHON_SCRIPT --folder $SOURCE_DIR'"
# Execute the python script, redirecting both stdout and stderr to the log file
python3.10 "$PYTHON_SCRIPT" --folder "$SOURCE_DIR" >> "$LOG_FILE" 2>&1
log "Python script finished."

# --- Step 4: Delete the original files using the list ---
log "Deleting original files based on the generated list..."
# Read the list of original files and delete them if they still exist
# The loop handles filenames with spaces and special characters safely
while IFS= read -r -d '' file_to_delete; do
    if [ -e "$file_to_delete" ]; then
        log "Deleting original file: '$file_to_delete'"
        rm -rf "$file_to_delete" # Use rm -rf to handle both files and directories
    else
        log "File to delete not found (may have been replaced by Python script): '$file_to_delete'"
    fi
done < "$ORIGINAL_FILES_LIST"

# --- Step 5: Move all remaining (new) files to the destination ---
log "Moving remaining (new) files from '$SOURCE_DIR' to '$DEST_DIR'..."
# Find all remaining items in the source directory and move them
find "$SOURCE_DIR" -mindepth 1 -print0 | while IFS= read -r -d '' item; do
    log "Moving new file '$item' to '$DEST_DIR'"
    mv "$item" "$DEST_DIR"
done

log "--- Script execution finished ---"