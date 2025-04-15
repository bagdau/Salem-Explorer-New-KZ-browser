class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window Setup
        self.setWindowTitle("Custom Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Web Engine
        self.browser = QWebEngineView()
        self.browser.setUrl("https://www.google.com")  # Default Start Page
        self.setCentralWidget(self.browser)

        # Create Downloads Panel
        self.downloads_panel = QListWidget()
        self.downloads_panel.hide()  # Initially Hidden

        # Create a Button to Toggle the Panel
        self.toggle_button = QPushButton("Show Downloads")
        self.toggle_button.clicked.connect(self.toggle_downloads_panel)

        # Layout for the Downloads Panel
        self.side_panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.downloads_panel)
        self.side_panel.setLayout(layout)

        # Dock Widget to Hold the Downloads Panel
        self.addDockWidget(3, self.side_panel)

        # Enable Download Handling
        profile = self.browser.page().profile()
        profile.downloadRequested.connect(self.handle_download_request)

    def toggle_downloads_panel(self):
        """Show or Hide the Downloads Panel"""
        if self.downloads_panel.isVisible():
            self.downloads_panel.hide()
        else:
            self.downloads_panel.show()

    def handle_download_request(self, download):
        """Handle File Download Requests"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path())

        if file_path:
            download.setPath(file_path)
            download.accept()
            self.update_downloads(file_path)

    def update_downloads(self, file_path):
        """Update the Downloads List"""
        self.downloads_panel.addItem(f"✅ Downloaded: {file_path}")
        self.downloads_panel.show()

# Run the Browser
app = QApplication([])
window = Browser()
window.show()
app.exec()
