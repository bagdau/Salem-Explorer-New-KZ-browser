import os
import sys
import time
import ctypes
import win32gui
import win32api
import win32con
import win32com.client
from ctypes.wintypes import HWND, DWORD
from ctypes import windll, POINTER, byref
from utils.blur import enable_acrylic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from ctypes.wintypes import HWND, DWORD, BOOL
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QGraphicsBlurEffect
from PyQt5.QtCore import QPropertyAnimation, QPoint, QTimer
from PyQt5.QtWidgets import QFileDialog, QPlainTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLineEdit, QLabel, QTabWidget, QComboBox, QListWidget, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtCore import QTimer, QPropertyAnimation, QPoint
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog
from PyQt5.QtCore import QUrl, Qt, QTimer, QDateTime
from PyQt5.QtGui import QColor, QPalette
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from PyQt5.QtMultimedia import QSoundEffect
from google_auth_oauthlib.flow import InstalledAppFlow
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.parse import quote


class AccentPolicy(ctypes.Structure):
    _fields_ = [("nAccentState", DWORD), ("nFlags", DWORD), ("nColor", DWORD), ("nAnimationId", DWORD)]

class WindowCompositionAttributeData(ctypes.Structure):
    _fields_ = [("nAttribute", DWORD), ("pData", POINTER(AccentPolicy)), ("ulDataSize", DWORD)]

    def enable_acrylic(hwnd):
        accent_policy = AccentPolicy()
        accent_policy.nAccentState = 3  # ACCENT_ENABLE_BLURBEHIND
        accent_policy.nFlags = 2
        accent_policy.nColor = 0x99FFFFFF  # Цвет и уровень прозрачности
        accent_policy.nAnimationId = 0

        data = WindowCompositionAttributeData()
        data.nAttribute = 19  # WCA_ACCENT_POLICY
        data.pData = byref(accent_policy)
        data.ulDataSize = ctypes.sizeof(accent_policy)

        windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))


class SalemBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        hwnd = self.winId().__int__()  # Получаем HWND окна
        enable_acrylic(hwnd)  # Включаем Acrylic Blur

        self.setWindowIcon(QIcon("img/icons/DES.ico"))
        self.setStyleSheet("background-color: #1a1a1a;")
        self.setWindowTitle("Salem Corp. Browser (Бета - версия)")
        self.setGeometry(50, 50, 1000, 600)
        

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.setStyleSheet("QTabBar::tab { height: 30px; width: 120px; background-color: #282a36; color: #f8f8f2; border: 1px solid #44475a; border-radius: 4px; padding: 5px; } QTabBar::tab:selected { background-color: #6272a4; }")

        self.title_label = QLabel("S/alem Corp. Browser")
        self.title_label.setStyleSheet("color: rgb(48, 211, 252); font-weight: bold; padding: 10px;")



        banner = QWidget()
        banner_layout = QVBoxLayout()
        nav_layout = QHBoxLayout()
        banner.setStyleSheet("""
    background: rgba(40, 42, 54, 0.5); /* Полупрозрачный фон */
    border: 2px solid rgba(255, 0, 127, 0.6); /* Полупрозрачная граница */
    border-radius: 15px;
    padding: 15px;
    backdrop-filter: blur(12px); /* Размытие фона */
    transition: all 0.3s ease-in-out;
    """)
        
        
        self.add_new_tab(QUrl.fromLocalFile("https://start.duckduckgo.com/"), "Үй")

        nav_bar = QWidget()
        nav_layout = QHBoxLayout()
        nav_bar.setStyleSheet("background-color: #282a36; padding: 5px; border: 1px solid #44475a;")

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL мекенжай енгізіңіз...")
        self.url_bar.setFixedHeight(25)
        self.url_bar.setMinimumWidth(300)
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.url_bar.setStyleSheet("""
    QLineEdit {
        background-color: #44475a;
        color: #f8f8f2;
        border: 1px solid #6272a4;
        border-radius: 5px;
        padding: 5px;
        transition: all 0.3s ease-in-out; /* Плавный эффект */
    }
    
    QLineEdit:hover {
        border: 1px solid #8be9fd; /* Голубое свечение при наведении */
        background-color: #505a78;
    }
    
    QLineEdit:focus {
        border: 1px solid #ff79c6; /* Розовое свечение при фокусе */
        background-color: #6272a4;
    }
""")


        # Buttons with fixed sizes
        back_btn = self.create_nav_button("◀", self.navigate_back)
        forward_btn = self.create_nav_button("▶", self.navigate_forward)
        refresh_btn = self.create_nav_button("↻", self.refresh_page)
        home_btn = self.create_nav_button("⩎", self.navigate_home)
        new_tab_btn = self.create_nav_button("➕", self.open_new_tab)
        add_block_btn = self.create_nav_button("⨶", self.enable_add_block)
        anti_tracker_btn = self.create_nav_button("⩒", self.enable_anti_tracker)
        user_account_btn = self.create_nav_button("🧑", self.enable_user_account)
        menu_btn = self.create_nav_button("☰", self.open_menu)

        self.downloads_panel = QListWidget()
        self.downloads_panel.hide()  # Скрываем, пока не нужна


        downloads_btn = QPushButton("📥")
        downloads_btn.setFixedSize(50, 25)
        downloads_btn.clicked.connect(self.toggle_downloads_panel)
        downloads_btn.setStyleSheet(self.button_style())


        open_file_btn = self.create_nav_button("📂", self.open_file)
        nav_layout.addWidget(open_file_btn)


        # Adding widgets to navigation bar
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(refresh_btn)
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(new_tab_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(user_account_btn)
        nav_layout.addWidget(add_block_btn)
        nav_layout.addWidget(anti_tracker_btn)
        nav_layout.addWidget(downloads_btn)
        nav_layout.addWidget(menu_btn)

        nav_bar.setLayout(nav_layout)

        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(nav_bar)
        central_layout.addWidget(self.tabs)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Подключаем обработку загрузок
        self.tabs.currentWidget().page().profile().downloadRequested.connect(self.handle_download_request)

        # Open initial tab
        # Open initial tab
        self.add_new_tab(QUrl("https://start.duckduckgo.com/"), "Шаңырақ")
        self.set_user_agent()


    def set_user_agent(self):
        """
        Устанавливает кастомный User-Agent и включает JavaScript.
        """

        # Меняем User-Agent на Firefox (можно заменить на другой)
        custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


        profile = self.tabs.currentWidget().page().profile()
        profile.setHttpUserAgent(custom_user_agent)

        # Включаем JavaScript, WebGL и GPU-ускорение
        settings = self.tabs.currentWidget().settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)  # Локальное хранилище
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)  # Плагины
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)  # Небезопасный контент
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)  # Разрешить всплывающие окна
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)  # Доступ к буферу обмена
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, False)  # Отключить XSS-защиту (иногда мешает)


        print("✅ User-Agent установлен:", custom_user_agent)
        print("✅ JavaScript, WebGL и GPU включены")


         # Подключаем обработку загрузок
        self.tabs.currentWidget().page().profile().downloadRequested.connect(self.handle_download_request)

    def create_nav_button(self, text, callback):
        button = QPushButton(text)
        button.setFixedSize(40, 25)
        button.clicked.connect(callback)
        return button

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
            background: linear-gradient(135deg, #0ff0e4, #068ce6);
            color: #f8f8f2;
            border: 1px solid rgba(255, 255, 255, 0.3); /* Полупрозрачная обводка */
            border-radius: 5px;
            padding: 5px 5px;
            font-size: 18px;
            backdrop-filter: blur(8px); /* Размытие фона */
            transition: all 0.3s ease-in-out;
            min-width: 50px;
        }

        QPushButton:hover {
            background: rgba(98, 114, 164, 0.6); /* Светлее при наведении */
            border: 1px solid rgba(139, 233, 253, 0.8);
            color: #ffffff;
            transform: scale(1.05);
        }

        QPushButton:pressed {
            background: rgba(255, 121, 198, 0.6);
            border: 1px solid rgba(189, 147, 249, 0.8);
            color: #282a36;
            transform: scale(0.95); /* Легкое сжатие при нажатии */
        }
    """


    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def navigate_home(self):
        self.url_bar.setText("https://officialcorporationsalem.kz/browserMainPagePreview.html")
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
        self.add_new_tab(QUrl("https://officialcorporationsalem.kz/browserMainPagePreview.html"), "Жаңа бет")

    def eventFilter(self, obj, event):
        if event.type() == Qt.KeyPress:
            if event.key() == Qt.Key_F12:
                self.open_dev_tools()
                return True
            elif event.key() == Qt.Key_U and event.modifiers() & Qt.ControlModifier:
                self.view_page_source()
                return True
        return super().eventFilter(obj, event)

    def open_dev_tools(self):
        if self.tabs.count() > 0:
            current_webview = self.tabs.currentWidget()
            if isinstance(current_webview, QWebEngineView):
                current_webview.page().setDevToolsPage(QWebEngineView().page())
                dev_tools = QWebEngineView()
                dev_tools.setPage(current_webview.page().devToolsPage())
                dev_tools.setWindowTitle("DevTools")
                dev_tools.resize(800, 600)
                dev_tools.show()

    def view_page_source(self):
        if self.tabs.count() > 0:
            current_webview = self.tabs.currentWidget()
            if isinstance(current_webview, QWebEngineView):
                current_webview.page().toHtml(lambda html: self.show_source_code(html))

    def show_source_code(self, html):
        source_window = QWidget()
        source_window.setWindowTitle("Source Code")
        layout = QVBoxLayout()
        source_label = QLabel()
        source_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        source_label.setText(html)
        layout.addWidget(source_label)
        source_window.setLayout(layout)
        source_window.resize(800, 600)
        source_window.show()

    def enable_add_block(self):
        print("Жарнаманы бұғаттау іске қосылды")
    
                 # Check if browser attribute exists, initialize it if needed
        if not hasattr(self, 'browser'):
            print("Ошибка: browser attribute not initialized!")
            return

                   # Получаем текущую страницу
        page = self.browser.page()
    
                   # Фильтры для блокировки рекламы (можно расширять)
        ad_keywords = ["ads", "advert", "banner", "popup", "sponsored"]
    
                   # JavaScript-код для удаления элементов рекламы
        block_ads_script = """
                function blockAds() {
                    let adSelectors = ['iframe', 'div', 'span', 'section'];
                    let adKeywords = ['ads', 'advert', 'banner', 'popup', 'sponsored'];
        
                adSelectors.forEach(tag => {
                    document.querySelectorAll(tag).forEach(el => {
                        if (adKeywords.some(keyword => el.className.includes(keyword) || el.id.includes(keyword))) {
                            el.remove();
                        }
                    });
                });
        }
        blockAds();
        """
    
          # Выполнение скрипта на загруженной странице
        page.runJavaScript(block_ads_script)
        print("Реклама успешно заблокирована")
        

    def enable_anti_tracker(self):
        print("Анти-трекер іске қосылды (To be implemented)") 

    def enable_user_account(self):
        print("Есептік жазба іске қосылды (To be implemented)")
    
    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def toggle_downloads_panel(self):
        """Показывает или скрывает панель загрузок"""
        if self.downloads_panel.isVisible():
           self.downloads_panel.hide()
        else:
           self.downloads_panel.show()

    def handle_download_request(self, download):
        """Обрабатывает загрузку файлов"""
        suggested_path, _ = QFileDialog.getSaveFileName(self, "Файлды сақтау", "", "All Files (*.*)")

        if suggested_path:
           download.setPath(suggested_path)
           download.accept()
           self.update_downloads(suggested_path)

    def update_downloads(self, file_path):
        """Обновляет список загруженных файлов"""
        self.downloads_panel.addItem(f"✅ Жүктелді: {file_path}")
        self.downloads_panel.show()


    def open_menu(self):
        menu = QMenu(self)

        # Функции для меню
        actions = [
            ("Жаңа қойынды", self.open_new_tab),  # Новая вкладка
            ("Жаңа терезе", self.open_new_window),  # Новое окно
            ("Жаңа құпия терезе", self.open_incognito_window),  # Инкогнито
            ("Журнал", self.show_history),  # История
            ("Жүктеулер", self.toggle_downloads_panel),  # Загрузки
            ("Құпиясөздер", self.manage_passwords),  # Менеджер паролей
            ("Қосымшалар мен тақырыптар", self.open_extensions),  # Расширения
            ("Басып шығару", self.print_page),  # Печать страницы
            ("Қалай сақтау", self.save_page),  # Сохранить как...
            ("Беттен іздеу", self.search_on_page),  # Поиск по странице
            ("Экран масштабы", self.zoom_menu),  # Масштаб
            ("Баптаулар", self.open_settings),  # Настройки
            ("Басқа құралдар", self.open_dev_tools),  # DevTools
            ("Анықтама", self.open_help),  # Справка
            ("Шығу", self.close)  # Закрыть браузер
    ]

        # Добавляем кнопки в меню
        for label, function in actions:
            action = QAction(label, self)
            action.triggered.connect(function)
            menu.addAction(action)

        # Показываем меню
        menu.exec_(self.mapToGlobal(self.menuBar().pos()))

    def open_new_window(self):
        """Открывает новое окно браузера"""
        new_window = SalemBrowser()
        new_window.show()

    def open_incognito_window(self):
        """Открывает инкогнито-режим (пока просто новое окно)"""
        new_incognito = SalemBrowser()
        new_incognito.show()

    def show_history(self):
        """Открывает страницу истории"""
        self.add_new_tab(QUrl("chrome://history/"), "Журнал")

    def toggle_downloads_panel(self):
        """Показывает или скрывает панель загрузок"""
        if self.downloads_panel.isVisible():
           self.downloads_panel.hide()
        else:
            self.downloads_panel.show()

    def manage_passwords(self):
        """Открывает менеджер паролей"""
        self.add_new_tab(QUrl("chrome://passwords/"), "Құпиясөздер")

    def open_extensions(self):
        """Открывает страницу расширений"""
        self.add_new_tab(QUrl("chrome://extensions/"), "Қосымшалар")

    def print_page(self):
        """Открывает окно печати"""
        if self.tabs.currentWidget():
           self.tabs.currentWidget().page().printToPdf("saved_page.pdf")

    def search_on_page(self):
        """Позволяет искать текст на странице"""
        text, ok = QInputDialog.getText(self, "Іздеу", "Іздеу мәтінін енгізіңіз:")
        if ok and text:
           self.tabs.currentWidget().findText(text)

    def open_settings(self):
        """Открывает страницу настроек"""
        self.add_new_tab(QUrl("chrome://settings/"), "Баптаулар")

    def open_help(self):
        """Открывает страницу помощи"""
        self.add_new_tab(QUrl("https://support.google.com/"), "Анықтама")

    def zoom_menu(self):
        """Меню изменения масштаба"""
        zoom_levels = ["50%", "75%", "100%", "125%", "150%", "200%"]
        zoom, ok = QInputDialog.getItem(self, "Масштаб", "Таңдаңыз:", zoom_levels, 2, False)
        if ok:
           scale = int(zoom.replace("%", "")) / 100
           if self.tabs.currentWidget():
              self.tabs.currentWidget().setZoomFactor(scale)


    def open_file(self):
        """
        Открывает локальный файл (PDF, HTML, XML, YAML, CSS, JS, TS) без зависаний.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", 
            "Все поддерживаемые файлы (*.pdf *.html *.xml *.yaml *.yml *.css *.js *.ts);;PDF файлы (*.pdf);;HTML файлы (*.html);;XML файлы (*.xml);;YAML файлы (*.yaml *.yml);;CSS файлы (*.css);;JavaScript файлы (*.js);;TypeScript файлы (*.ts)", options=options)
    
        if file_path:
           file_extension = os.path.splitext(file_path)[1].lower()

           if file_extension == ".pdf":
               # Открываем PDF через QWebEngineView
              self.add_new_tab(QUrl.fromLocalFile(file_path), f"PDF: {os.path.basename(file_path)}")

        elif file_extension in [".html", ".xml", ".yaml", ".yml", ".css", ".js", ".ts"]:
                # Открываем текстовые файлы в QPlainTextEdit (без зависаний)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
                text_editor = QPlainTextEdit()
                text_editor.setPlainText(content)
                text_editor.setReadOnly(True)  # Только для просмотра

                index = self.tabs.addTab(text_editor, f"Файл: {os.path.basename(file_path)}")
                self.tabs.setCurrentIndex(index)
        
        else:
            print("⚠ Формат файла не поддерживается!")

    def handle_file_loaded(self, file_path, file_type, content):
        """
        Открывает загруженные файлы через `viewer.html` или PDF-вьюер.
        """
        if file_type == "pdf":
              # Открываем PDF в браузере
              self.add_new_tab(QUrl.fromLocalFile(file_path), f"PDF: {os.path.basename(file_path)}")

        elif file_type == "text":
              # Получаем полный путь к `viewer.html`
              local_viewer_path = os.path.abspath("viewer.html")
              local_viewer_url = QUrl.fromLocalFile(local_viewer_path).toString()

              # Кодируем путь к файлу (чтобы работали пробелы и спецсимволы)
              encoded_file_url = quote(QUrl.fromLocalFile(file_path).toString(), safe=':/')

              # Формируем корректный URL
              full_url = f"{local_viewer_url}?file={encoded_file_url}"

              # Открываем `viewer.html` с файлом
              self.add_new_tab(QUrl(full_url), f"Файл: {os.path.basename(file_path)}")

        else:
            print(f"⚠ Формат файла `{file_path}` не поддерживается!")


    
    def show_context_menu(self, pos):
        """Создает контекстное меню, как в Google Chrome."""
        menu = QMenu(self)

        # Добавляем действия
        back_action = QAction("⬅ Назад", self)
        back_action.triggered.connect(self.navigate_back)

        forward_action = QAction("➡ Вперёд", self)
        forward_action.triggered.connect(self.navigate_forward)

        reload_action = QAction("🔄 Обновить", self)
        reload_action.triggered.connect(self.refresh_page)

        save_action = QAction("💾 Сохранить как...", self)
        save_action.triggered.connect(self.save_page)

        copy_link_action = QAction("🔗 Копировать ссылку", self)
        copy_link_action.triggered.connect(self.copy_link)

        devtools_action = QAction("⚙ Открыть DevTools", self)
        devtools_action.triggered.connect(self.open_dev_tools)

        # Добавляем все действия в меню
        menu.addAction(back_action)
        menu.addAction(forward_action)
        menu.addAction(reload_action)
        menu.addSeparator()  # Разделитель
        menu.addAction(save_action)
        menu.addAction(copy_link_action)
        menu.addSeparator()
        menu.addAction(devtools_action)

        # Показываем меню там, где кликнули
        menu.exec_(self.mapToGlobal(pos))

    def navigate_back(self):
        """Назад"""
        if self.tabs.currentWidget():
           self.tabs.currentWidget().back()

    def navigate_forward(self):
        """Вперёд"""
        if self.tabs.currentWidget():
           self.tabs.currentWidget().forward()

    def refresh_page(self):
        """Обновить страницу"""
        if self.tabs.currentWidget():
           self.tabs.currentWidget().reload()

    def save_page(self):
        """Сохранение HTML страницы"""
        current_browser = self.tabs.currentWidget()
        if current_browser:
           file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить страницу как", "", "HTML файлы (*.html);;Все файлы (*.*)")
           if file_path:
              current_browser.page().toHtml(lambda html: open(file_path, "w", encoding="utf-8").write(html))

    def copy_link(self):
        """Копирует текущий URL в буфер обмена"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.url_bar.text())
        print("🔗 Ссылка скопирована:", self.url_bar.text())

    def open_dev_tools(self):
        """Открывает DevTools (панель разработчика)"""
        if self.tabs.count() > 0:
           current_webview = self.tabs.currentWidget()
           if isinstance(current_webview, QWebEngineView):
              current_webview.page().setDevToolsPage(QWebEngineView().page())

class FileLoaderThread(QThread):
    file_loaded = pyqtSignal(str, str, object)  # file_path, file_type, content

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Запускается в фоновом потоке и загружает файл"""
        file_extension = os.path.splitext(self.file_path)[1].lower()

        try:
            if file_extension == ".pdf":
                self.file_loaded.emit(self.file_path, "pdf", None)

            elif file_extension in [".html", ".xml", ".yaml", ".yml", ".css", ".js", ".ts"]:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.file_loaded.emit(self.file_path, "text", content)

            else:
                self.file_loaded.emit(self.file_path, "unsupported", None)

        except Exception as e:
            print(f"⚠ Ошибка при загрузке файла {self.file_path}: {e}")
    def open_file(self):
        """
        Открывает локальный файл (PDF, HTML, XML, YAML, CSS, JS, TS) без зависаний в отдельном потоке.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", 
            "Все поддерживаемые файлы (*.pdf *.html *.xml *.yaml *.yml *.css *.js *.ts);;PDF файлы (*.pdf);;HTML файлы (*.html);;XML файлы (*.xml);;YAML файлы (*.yaml *.yml);;CSS файлы (*.css);;JavaScript файлы (*.js);;TypeScript файлы (*.ts)", options=options)

        if file_path:
           self.loader_thread = FileLoaderThread(file_path)
           self.loader_thread.file_loaded.connect(self.handle_file_loaded)
           self.loader_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SalemBrowser()
    browser.show()
    sys.exit(app.exec_())   


