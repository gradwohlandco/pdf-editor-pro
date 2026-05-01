import sys
import fitz
import PyPDF2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QScrollArea,
    QFrame, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QFont
from PySide6.QtCore import Qt, QSize

# --- STYLESHEET ---
MODERN_STYLE = """
QMainWindow {
    background-color: #1e1e1e;
}

/* Sidebar */
#Sidebar {
    background-color: #252526;
    border-right: 1px solid #3c3c3c;
    min-width: 200px;
}

#Sidebar QPushButton {
    background-color: #333333;
    color: #cccccc;
    border: none;
    padding: 10px;
    text-align: left;
    border-radius: 5px;
    font-size: 13px;
    margin: 5px 10px;
}

#Sidebar QPushButton:hover {
    background-color: #454545;
    color: white;
}

#Sidebar QPushButton#PrimaryBtn {
    background-color: #007acc;
    color: white;
}

#Sidebar QPushButton#PrimaryBtn:hover {
    background-color: #0062a3;
}

/* Page Card */
#PageCard {
    background-color: #2d2d2d;
    border: 1px solid #3f3f3f;
    border-radius: 8px;
}

#PageCard:hover {
    border: 1px solid #007acc;
}

#PageLabel {
    color: #aaaaaa;
    font-weight: bold;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: #1e1e1e;
}

QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #3e3e42;
    min-height: 20px;
    border-radius: 5px;
}
"""

class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Editor Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLE)

        self.pages = []
        self.previews = []

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        title = QLabel("PDF Editor PRO")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 18px; margin: 20px;")
        sidebar_layout.addWidget(title)

        self.load_btn = QPushButton("  📂  Datei öffnen")
        self.load_btn.setObjectName("PrimaryBtn")
        self.load_btn.clicked.connect(self.load_pdf)

        self.merge_btn = QPushButton("  ➕  Hinzufügen")
        self.merge_btn.clicked.connect(self.merge_pdfs)

        self.save_btn = QPushButton("  💾  Speichern unter")
        self.save_btn.clicked.connect(self.save_pdf)

        sidebar_layout.addWidget(self.load_btn)
        sidebar_layout.addWidget(self.merge_btn)
        sidebar_layout.addWidget(self.save_btn)
        sidebar_layout.addStretch()

        # ---------------- MAIN CONTENT ----------------
        content_layout = QVBoxLayout()
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll.setWidget(self.container)
        content_layout.addWidget(self.scroll)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_layout)

    def load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF laden", "", "PDF Files (*.pdf)")
        if path:
            self.pages = list(PyPDF2.PdfReader(path).pages)
            self.previews = self.render_previews(path, len(self.pages))
            self.refresh()

    def merge_pdfs(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "PDFs hinzufügen", "", "PDF Files (*.pdf)")
        if paths:
            for path in paths:
                reader = PyPDF2.PdfReader(path)
                pages = list(reader.pages)
                self.pages.extend(pages)
                self.previews.extend(self.render_previews(path, len(pages)))
            self.refresh()

    def save_pdf(self):
        if not self.pages: return
        path, _ = QFileDialog.getSaveFileName(self, "PDF speichern", "", "PDF Files (*.pdf)")
        if path:
            writer = PyPDF2.PdfWriter()
            for page in self.pages:
                writer.add_page(page)
            with open(path, "wb") as f:
                writer.write(f)

    def render_previews(self, path, count):
        doc = fitz.open(path)
        previews = []
        for i in range(count):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3)) # Scale down for performance
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            previews.append(QPixmap.fromImage(img))
        doc.close()
        return previews

    def refresh(self):
        # UI leeren
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Grid neu aufbauen (4 Spalten)
        columns = 4
        for i in range(len(self.pages)):
            row = i // columns
            col = i % columns
            card = self.create_page_card(i)
            self.grid_layout.addWidget(card, row, col)

    def create_page_card(self, i):
        card = QFrame()
        card.setObjectName("PageCard")
        card.setFixedSize(220, 320)
        
        layout = QVBoxLayout(card)

        # Preview Image
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        pix = self.previews[i].scaled(180, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img_label.setPixmap(pix)
        
        # Bottom Bar for Controls
        bottom_bar = QHBoxLayout()
        
        page_num = QLabel(f"#{i + 1}")
        page_num.setObjectName("PageLabel")
        
        btn_style = "background: transparent; color: white; font-size: 16px; border: none;"
        
        up_btn = QPushButton("◀")
        up_btn.setStyleSheet(btn_style)
        up_btn.setCursor(Qt.PointingHandCursor)
        up_btn.clicked.connect(lambda _, idx=i: self.move_up(idx))

        down_btn = QPushButton("▶")
        down_btn.setStyleSheet(btn_style)
        down_btn.setCursor(Qt.PointingHandCursor)
        down_btn.clicked.connect(lambda _, idx=i: self.move_down(idx))

        del_btn = QPushButton("🗑")
        del_btn.setStyleSheet("background: transparent; color: #ff5555; font-size: 16px; border: none;")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda _, idx=i: self.delete(idx))

        bottom_bar.addWidget(page_num)
        bottom_bar.addStretch()
        bottom_bar.addWidget(up_btn)
        bottom_bar.addWidget(down_btn)
        bottom_bar.addWidget(del_btn)

        layout.addWidget(img_label)
        layout.addLayout(bottom_bar)
        
        return card

    def move_up(self, i):
        if i > 0: self.swap(i, i - 1)

    def move_down(self, i):
        if i < len(self.pages) - 1: self.swap(i, i + 1)

    def swap(self, i, j):
        self.pages[i], self.pages[j] = self.pages[j], self.pages[i]
        self.previews[i], self.previews[j] = self.previews[j], self.previews[i]
        self.refresh()

    def delete(self, i):
        del self.pages[i]
        del self.previews[i]
        self.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Sorgt für einheitliches Look & Feel über OS-Grenzen hinweg
    window = PDFEditor()
    window.show()
    sys.exit(app.exec())