import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QFileDialog,
                             QMessageBox, QTextEdit, QSplitter, QListWidgetItem)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from image_metadata_randomizer import randomize_metadata, get_metadata_string

class DragDropArea(QLabel):
    """Custom QLabel subclass to handle drag and drop."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag and Drop Images or Folders Here\nOr Click 'Select' Buttons")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                font-size: 14px;
                color: #888;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007bff; /* Highlight border on drag enter */
                    border-radius: 5px;
                    padding: 20px;
                    font-size: 14px;
                    color: #555;
                    background-color: #eaf2ff; /* Light blue background */
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                font-size: 14px;
                color: #888;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        self.parent().handle_dropped_files(paths) # Pass paths to parent widget
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                font-size: 14px;
                color: #888;
            }
        """)

class MetadataRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Metadata Randomizer")
        self.setGeometry(100, 100, 850, 550) # x, y, width, height
        self.selected_files = []
        self.currently_selected_path_for_metadata = None # Store path for post-randomization update

        self.init_ui()

    def init_ui(self):
        # Main layout is now horizontal for the splitter
        main_h_layout = QHBoxLayout(self)

        # Use a splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        main_h_layout.addWidget(splitter)

        # --- Left Panel (Input and File List) ---
        left_panel_widget = QWidget()
        left_v_layout = QVBoxLayout(left_panel_widget)
        left_v_layout.setContentsMargins(0,0,0,0) # Remove margins if needed

        # --- Input Area ---
        input_layout = QVBoxLayout()

        # Drag and Drop Area
        self.drag_drop_area = DragDropArea(self)
        input_layout.addWidget(self.drag_drop_area)

        # Selection Buttons
        button_layout = QHBoxLayout()
        self.select_files_button = QPushButton("Select Files")
        self.select_files_button.clicked.connect(self.select_files)
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_files_button)
        button_layout.addWidget(self.select_folder_button)
        input_layout.addLayout(button_layout)

        left_v_layout.addLayout(input_layout)

        # --- File List Area ---
        self.file_list_label = QLabel("Selected Files/Folders:")
        left_v_layout.addWidget(self.file_list_label)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setStyleSheet("QListWidget { border: 1px solid #ccc; border-radius: 3px; }")
        # Connect selection change signal
        self.file_list_widget.currentItemChanged.connect(self.update_metadata_display)
        left_v_layout.addWidget(self.file_list_widget, 1) # Give list more stretch factor

        # --- Action Button ---
        self.randomize_button = QPushButton("Randomize Metadata")
        self.randomize_button.clicked.connect(self.start_randomization)
        self.randomize_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745; /* Green */
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #218838; /* Darker green */
            }
            QPushButton:pressed {
                background-color: #1e7e34; /* Even darker green */
            }
        """)
        left_v_layout.addWidget(self.randomize_button, alignment=Qt.AlignCenter)

        # Add left panel to splitter
        splitter.addWidget(left_panel_widget)

        # --- Right Panel (Metadata Sidebar) ---
        right_panel_widget = QWidget()
        right_v_layout = QVBoxLayout(right_panel_widget)
        right_v_layout.setContentsMargins(5,0,0,0) # Add a small left margin

        self.metadata_label = QLabel("Metadata Preview:")
        right_v_layout.addWidget(self.metadata_label)

        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setLineWrapMode(QTextEdit.NoWrap) # Prevent wrapping long lines
        # Update stylesheet for black background and green text
        self.metadata_display.setStyleSheet("QTextEdit { border: 1px solid #ccc; border-radius: 3px; background-color: black; color: #00FF00; }") # Changed background and color
        right_v_layout.addWidget(self.metadata_display)

        # Add right panel to splitter
        splitter.addWidget(right_panel_widget)

        # Set splitter sizes (e.g., give more space to the left panel initially)
        splitter.setSizes([400, 250]) # Adjust initial sizes as needed

        # --- Status Bar ---
        # Placed under the left panel layout for better positioning
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; padding-top: 5px;")
        left_v_layout.addWidget(self.status_label, alignment=Qt.AlignRight)

    @Slot(QListWidgetItem, QListWidgetItem)
    def update_metadata_display(self, current_item, previous_item):
        # Clear previous selection tracking for post-randomization update
        self.currently_selected_path_for_metadata = None
        if current_item:
            path = current_item.text()
            self.currently_selected_path_for_metadata = path # Store for later use
            if os.path.isfile(path) and path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                metadata_str = get_metadata_string(path)
                self.metadata_display.setText(metadata_str)
            elif os.path.isdir(path):
                self.metadata_display.setText(f"Folder selected:\n{os.path.basename(path)}\n\n(Metadata preview is shown for individual image files)")
            else:
                 self.metadata_display.setText("(Select an image file to see its metadata)")
        else:
            self.metadata_display.clear()

    @Slot()
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "", # Start directory
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)" # Filter
        )
        if files:
            self.update_file_list(files)

    @Slot()
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing Images",
            "" # Start directory
        )
        if folder:
            self.update_file_list([folder]) # Add the folder path itself

    def handle_dropped_files(self, paths):
        self.update_file_list(paths)

    def update_file_list(self, paths):
        # Clear duplicates and add new paths
        current_items_text = {self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())}
        new_paths_added = []
        for path in paths:
            # Normalize path separators for consistency
            normalized_path = os.path.normpath(path)
            if normalized_path not in current_items_text:
                self.file_list_widget.addItem(normalized_path)
                new_paths_added.append(normalized_path)

        if new_paths_added:
            self.status_label.setText(f"Added {len(new_paths_added)} items.")
             # Select the first newly added item to trigger metadata display
            if len(new_paths_added) > 0:
                items = self.file_list_widget.findItems(new_paths_added[0], Qt.MatchExactly)
                if items:
                    self.file_list_widget.setCurrentItem(items[0])
        else:
            self.status_label.setText("No new valid items added.")


    def get_all_image_files(self):
        """Gets all image file paths from the list widget, expanding folders."""
        all_files = []
        # More specific image check for processing
        image_extensions = {'.jpg', '.jpeg'} # Limit processing to JPEG for now based on core logic
        items_to_process = []
        for i in range(self.file_list_widget.count()):
            items_to_process.append(self.file_list_widget.item(i).text())

        processed_folders = set() # Avoid processing subfolders multiple times if parent selected

        for path in items_to_process:
            normalized_path = os.path.normpath(path)
            if os.path.isdir(normalized_path):
                 # Check if this folder or a parent is already processed
                skip = False
                for processed in processed_folders:
                    if normalized_path.startswith(processed + os.sep) or normalized_path == processed:
                         skip = True
                         break
                if skip: continue

                processed_folders.add(normalized_path)
                # Recursively find images in the folder
                for root, _, files in os.walk(normalized_path):
                    for file in files:
                        if os.path.splitext(file)[1].lower() in image_extensions:
                            all_files.append(os.path.join(root, file))
            elif os.path.isfile(normalized_path) and os.path.splitext(normalized_path)[1].lower() in image_extensions:
                all_files.append(normalized_path)

        return list(set(all_files)) # Return unique file paths

    @Slot()
    def start_randomization(self):
        # Store the currently selected path *before* processing
        selected_original_path = self.currently_selected_path_for_metadata

        files_to_process = self.get_all_image_files()

        if not files_to_process:
            QMessageBox.warning(self, "No Files", "Please select valid JPEG image files or folders containing them.")
            return

        self.status_label.setText(f"Processing {len(files_to_process)} files...")
        self.randomize_button.setEnabled(False)
        self.file_list_widget.setEnabled(False) # Disable list during processing
        QApplication.processEvents()

        processed_count = 0
        errors = []

        try:
            print("Files to process:", files_to_process)
            for file_path in files_to_process:
                 print(f"Processing: {file_path}")
                 try:
                    # Corrected call based on user feedback:
                    output_path = randomize_metadata(image_path=file_path, randomize_all=True, randomize_windows_props=True)
                    if output_path:
                        print(f"Successfully created: {output_path}")
                        processed_count += 1
                    else:
                        print(f"Failed to process (returned None): {file_path}")
                        errors.append(os.path.basename(file_path))
                 except Exception as item_exc:
                     print(f"Error processing file {file_path}: {item_exc}")
                     errors.append(f"{os.path.basename(file_path)}: {item_exc}")


            if processed_count > 0:
                 QMessageBox.information(self, "Success", f"Successfully processed {processed_count} out of {len(files_to_process)} files.")
            if errors:
                 error_details = "\n".join(errors[:10]) # Show first 10 errors
                 if len(errors) > 10: error_details += "\n..."
                 QMessageBox.warning(self, "Processing Issues", f"Failed to process {len(errors)} files:\n{error_details}")

            # --- Update metadata display for the originally selected item ---
            if selected_original_path and os.path.isfile(selected_original_path):
                # Construct the expected modified path
                directory = os.path.dirname(selected_original_path)
                filename = os.path.basename(selected_original_path)
                modified_path = os.path.join(directory, f"modified_{filename}")

                # Check if the modified file exists (meaning processing likely succeeded for it)
                if os.path.exists(modified_path):
                    # Re-select the original item in the list to trigger update,
                    # but show the *modified* metadata
                    items = self.file_list_widget.findItems(selected_original_path, Qt.MatchExactly)
                    if items:
                        self.file_list_widget.setCurrentItem(items[0]) # Trigger signal again
                        # Explicitly set text to modified metadata
                        modified_metadata_str = get_metadata_string(modified_path)
                        self.metadata_display.setText(modified_metadata_str)
                else:
                     # If modified file doesn't exist, but original was selected, show error/info
                     self.metadata_display.setText(f"Metadata for: {filename}\n\n(Processing may have failed for this file, modified version not found)")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred during processing batch:\n{e}")
            print(f"Error during processing batch: {e}") # Log to console as well
        finally:
            self.status_label.setText("Ready")
            self.randomize_button.setEnabled(True)
            self.file_list_widget.setEnabled(True) # Re-enable list
            # Optionally clear the list after processing? Decide based on UX preference
            # self.file_list_widget.clear()
            # self.metadata_display.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MetadataRandomizerGUI()
    window.show()
    sys.exit(app.exec()) 