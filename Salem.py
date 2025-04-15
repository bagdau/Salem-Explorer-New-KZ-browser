from PyQt5.QtCore import QPropertyAnimation, QPoint, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLineEdit, QLabel, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QPropertyAnimation, QPoint, QRect
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QColor, QPalette
from google_auth_oauthlib.flow import InstalledAppFlow
import sys


class SalemBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Salem Corp. Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #1e1e2e; color: #ffffff;")

        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("URL мекенжай енгізіңіз...")
        self.url_bar.setGeometry(50, 50, 300, 40)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 rgb(131, 58, 180),
                                            stop:0.5 rgb(253, 29, 29),
                                            stop:1 rgb(252, 176, 69));
                color: white;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                transition: 300ms ease-in-out;
            }
            QLineEdit:hover {
                background: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0,
                                            stop:0 rgb(252, 176, 69),
                                            stop:0.5 rgb(253, 29, 29),
                                            stop:1 rgb(131, 58, 180));
                border: 2px solid rgb(131, 58, 180);
            }
        """)

        self.url_bar_animation()

    def url_bar_animation(self):
        animation = QPropertyAnimation(self.url_bar, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(QRect(50, 50, 300, 40))
        animation.setEndValue(QRect(50, 50, 320, 45))
        animation.setLoopCount(2)
        animation.start()


        banner = QWidget()
        banner_layout = QVBoxLayout()
        banner.setStyleSheet("background-color: #282a36; border: 5px solid #ff007f; border-radius: 10px; padding: 10px;")

        banner_label = QLabel("Welcome to Salem Corp. Browser")
        banner_label.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; text-align: center;")
        banner_label.setAlignment(Qt.AlignCenter)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.browser.setStyleSheet("border: 5px solid #ff007f; border-radius: 5px;") 

        banner_layout.addWidget(banner_label)
        banner_layout.addWidget(self.browser)
        banner.setLayout(banner_layout)

        self.add_new_tab(QUrl("https://www.google.com"), "Home")

        nav_bar = QWidget()
        nav_layout = QHBoxLayout()
        nav_bar.setStyleSheet("background-color: #282a36; padding: 5px; border: 1px solid #44475a;")

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL мекенжай енгізіңіз...")
        self.url_bar.setFixedHeight(25) 
        self.url_bar.setMinimumWidth(300)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; border-radius: 5px; padding: 5px;")

        # Buttons with fixed sizes
        back_btn = self.create_nav_button("◀ Артқа", self.navigate_back)
        forward_btn = self.create_nav_button("Алға ▶", self.navigate_forward)
        refresh_btn = self.create_nav_button("🔄 Жаңарту", self.refresh_page)
        home_btn = self.create_nav_button("🏠 Шаңырақ", self.navigate_home)
        new_tab_btn = self.create_nav_button("➕ Жаңа бет", self.open_new_tab)
        pip_btn = self.create_nav_button("PiP", self.enable_picture_in_picture)
        add_block_btn = self.create_nav_button("Жарнаманы блоктау", self.enable_add_block)
        anti_tracker_btn = self.create_nav_button("Анти-трекер", self.enable_anti_tracker)
        user_account_btn = self.create_nav_button("Есептік жазба", self.enable_user_account)

        downloads_btn = QPushButton("Жүктеулер📥")
        downloads_btn.setFixedSize(50, 25)
        downloads_btn.clicked.connect(self.toggle_downloads_panel)
        downloads_btn.setStyleSheet(self.button_style())


        # Adding widgets to navigation bar
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(refresh_btn)
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(new_tab_btn)
        nav_layout.addWidget(pip_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(user_account_btn)
        nav_layout.addWidget(add_block_btn)
        nav_layout.addWidget(anti_tracker_btn)
        nav_layout.addWidget(downloads_btn)

        nav_bar.setLayout(nav_layout)

        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(nav_bar)
        central_layout.addWidget(self.tabs)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Open initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "Шаңырақ")

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def create_nav_button(self, text, callback):
        button = QPushButton(text)
        button.setFixedSize(90, 25)
        button.setStyleSheet(self.button_style())
        button.clicked.connect(callback)
        return button

    def button_style(self):
        return """
         QPushButton {
                background-color: #6272a4;
                color: #f8f8f2;
                border: 1px solid #ff79c6;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
        QPushButton:hover {
                background-color: rgb(9, 122, 122);
                color: #ffffff;
                transform: scale(1.05);
                transition: all 0.2s;
            }
        """

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def navigate_home(self):
        self.url_bar.setText("file://C:/Users/BAGDAULET PC/Desktop/UpdatedVersionsSSB/SalemSOFTWARE/homepageSalem.html")
        self.navigate_to_url()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "file://" + url
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def refresh_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def open_new_tab(self):
        self.add_new_tab(QUrl("https://www.google.com"), "Жаңа бет")

    def enable_picture_in_picture(self):
        print("Суреттегі сурет іске қосылды (To be implemented)")

    def enable_add_block(self):
        print("Жарнаманы бұғаттау іске қосылды (To be implemented)")

    def enable_anti_tracker(self):
        print("Анти-трекер іске қосылды (To be implemented)")

    def enable_user_account(self):
        print("Есептік жазба іске қосылды (To be implemented)")
    
    def enable_google_account(self):
        SCOPES = ["https://www.googleapis.com/auth/userinfo.profile"]
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        credentials = flow.run_local_server(port=0)
        print("Google account enabled:", credentials.token)
    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)


    def toggle_downloads_panel(self):
        """Toggle the Downloads Panel with animation."""
        if self.downloads_panel.isVisible():
           # Скрыть панель с анимацией
           animation = QPropertyAnimation(self.downloads_panel, b"pos")
           animation.setEndValue(QPoint(1200, 100))  # Выход за пределы экрана
           animation.setDuration(500)  # Длительность анимации
        
           # Используем QTimer для отложенного начала анимации
           QTimer.singleShot(0, lambda: animation.start())
           self.downloads_panel.setVisible(False)
        else:
           # Показать панель с анимацией
           self.downloads_panel.setVisible(True)
           animation = QPropertyAnimation(self.downloads_panel, b"pos")
           animation.setEndValue(QPoint(950, 100))  # Позиция панели на экране
           animation.setDuration(200)  # Длительность анимации
        
           # Используем QTimer для отложенного начала анимации
           QTimer.singleShot(0, lambda: animation.start())

        try:
           download_dir = QFileDialog.getExistingDirectory(self, "нақты қалташаны таңдаңыз")
           if download_dir:
             print(f"Таңдалған қалташа: {download_dir}")
           else:
             print("Қалташа таңдалмады.")
        except Exception as e:
             print(f"Қате: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SalemBrowser()
    browser.show()
    sys.exit(app.exec_())   


