import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QFileDialog,
                             QMessageBox)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from image_metadata_randomizer import randomize_metadata # Assuming this function exists

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
        self.setGeometry(100, 100, 600, 450) # x, y, width, height
        self.selected_files = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

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

        main_layout.addLayout(input_layout)

        # --- File List Area ---
        self.file_list_label = QLabel("Selected Files/Folders:")
        main_layout.addWidget(self.file_list_label)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setStyleSheet("QListWidget { border: 1px solid #ccc; border-radius: 3px; }")
        main_layout.addWidget(self.file_list_widget)

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
        main_layout.addWidget(self.randomize_button, alignment=Qt.AlignCenter)

        # --- Status Bar (Optional - Placeholder) ---
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666;")
        main_layout.addWidget(self.status_label, alignment=Qt.AlignRight)

        self.setLayout(main_layout)

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
        current_items = {self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())}
        new_paths_added = []
        for path in paths:
            if path not in current_items:
                self.file_list_widget.addItem(path)
                new_paths_added.append(path)
        if new_paths_added:
            self.status_label.setText(f"Added {len(new_paths_added)} items.")
        else:
            self.status_label.setText("No new items added.")


    def get_all_image_files(self):
        """Gets all image file paths from the list widget, expanding folders."""
        all_files = []
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
        for i in range(self.file_list_widget.count()):
            path = self.file_list_widget.item(i).text()
            if os.path.isdir(path):
                # Recursively find images in the folder
                for root, _, files in os.walk(path):
                    for file in files:
                        if os.path.splitext(file)[1].lower() in image_extensions:
                            all_files.append(os.path.join(root, file))
            elif os.path.isfile(path) and os.path.splitext(path)[1].lower() in image_extensions:
                all_files.append(path)
        return list(set(all_files)) # Return unique file paths

    @Slot()
    def start_randomization(self):
        files_to_process = self.get_all_image_files()

        if not files_to_process:
            QMessageBox.warning(self, "No Files", "Please select image files or folders first.")
            return

        self.status_label.setText(f"Processing {len(files_to_process)} files...")
        self.randomize_button.setEnabled(False) # Disable button during processing
        QApplication.processEvents() # Update UI

        try:
            # --- TODO: Integrate with your actual randomization logic ---
            # For now, just printing the files to be processed
            print("Files to process:", files_to_process)
            for file_path in files_to_process:
                 # Example call: Adjust arguments as needed by your function
                 # randomize_metadata(file_path, show_original=False, show_modified=True, modify_windows_properties=True)
                 # Corrected call based on user feedback:
                 randomize_metadata(image_path=file_path, randomize_all=True, randomize_windows_props=True)
                 print(f"Processed: {file_path}")

            QMessageBox.information(self, "Success", f"Successfully processed {len(files_to_process)} files.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during processing:\n{e}")
            print(f"Error during processing: {e}") # Log to console as well
        finally:
            self.status_label.setText("Ready")
            self.randomize_button.setEnabled(True) # Re-enable button
            # Optionally clear the list after processing
            # self.file_list_widget.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MetadataRandomizerGUI()
    window.show()
    sys.exit(app.exec()) 