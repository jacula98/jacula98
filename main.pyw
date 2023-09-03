import sys
import psutil
import GPUtil
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtSvg import QSvgWidget, QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import (
    QDialog, QWidget, QPushButton, QLabel, QApplication, QProgressBar
)

class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Dialog')
        self.setWindowFlags(
            self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(Stylesheet)
        self.setWindowOpacity(0.3)  # Początkowa wartość opacity
        self.dragging = False
        self.offset = None
        

        self.initUi()

        # Utwórz timer do aktualizacji informacji o zasobach co sekundę
        self.resource_timer = QTimer(self)
        self.resource_timer.timeout.connect(self.update_resource_info)
        self.resource_timer.start(1000)

        # Ustaw początkową pozycję okna
        self.set_initial_position()

    def set_initial_position(self):
        # Pobierz rozmiar głównego monitora
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_rect = self.frameGeometry()

        # Ustaw pozycję okna na prawej stronie monitora, 50 pikseli od góry
        window_rect.moveTopRight(screen_geometry.topRight() - QPoint(150, -30))
        self.move(window_rect.topRight())

    def initUi(self):
        # Important: this widget is used as background and rounded corners.
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')

        self.toggle_button = QPushButton('∧', self)
        self.toggle_button.setObjectName('toggleButton')
        self.toggle_button.setGeometry(12, 11, 20, 20)
        self.toggle_button.setStyleSheet('font-weight: bold; color: #33FFFF; font-size: 12px;')
        self.toggle_button.clicked.connect(self.toggle_progress_bars)

        # Add user interface to widget
        self.close_button = QPushButton('r', self)
        self.close_button.setObjectName('closeButton')
        self.close_button.clicked.connect(self.accept)
        

        # Pionowe paski postępu do wyświetlania informacji o CPU, GPU, temperaturze GPU, RAM
        self.cpu_progress = QProgressBar(self)
        self.cpu_progress.setOrientation(Qt.Vertical)
        self.cpu_progress.setObjectName('cpuProgressBar')
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setFormat('')  # Usuń liczbę z procentami

        self.gpu_progress = QProgressBar(self)
        self.gpu_progress.setOrientation(Qt.Vertical)
        self.gpu_progress.setObjectName('gpuProgressBar')
        self.gpu_progress.setRange(0, 100)
        self.gpu_progress.setFormat('')  # Usuń liczbę z procentami

        self.gpu_temp_progress = QProgressBar(self)
        self.gpu_temp_progress.setOrientation(Qt.Vertical)
        self.gpu_temp_progress.setObjectName('gpuTempProgressBar')
        self.gpu_temp_progress.setRange(0, 100)
        self.gpu_temp_progress.setFormat('')  # Usuń liczbę z procentami

        self.ram_progress = QProgressBar(self)
        self.ram_progress.setOrientation(Qt.Vertical)
        self.ram_progress.setObjectName('ramProgressBar')
        self.ram_progress.setRange(0, 100)
        self.ram_progress.setFormat('')  # Usuń liczbę z procentami

        self.cpu_label = QLabel('CPU', self)
        self.gpu_label = QLabel('GPU', self)
        self.gpu_temp_label = QLabel('GPU°C', self)
        self.ram_label = QLabel('RAM', self)

        # Label do wyświetlania informacji o CPU, GPU, temperaturze GPU, RAM
        self.resource_label = QLabel(self)

        # Ustaw pozycje elementów
        self.widget.setGeometry(0, 0, 150, 260) # MAIN WINDOW
        self.close_button.setGeometry(115, 7, 15, 15)
        self.close_button.setStyleSheet('font-weight: bold; color: #33FFFF;')
        
        self.gpu_temp_label.setGeometry(6, 184, 50, 15)
        self.gpu_label.setGeometry(46, 184, 40, 15)
        self.cpu_label.setGeometry(80, 184, 40, 15)
        self.ram_label.setGeometry(113, 184, 40, 15)

        self.gpu_temp_progress.setGeometry(11, 35, 25, 150)
        self.gpu_progress.setGeometry(45, 35, 25, 150)
        self.cpu_progress.setGeometry(79, 35, 25, 150)
        self.ram_progress.setGeometry(113, 35, 25, 150)
        
        self.emoji_label = QLabel("🔈", parent=self)
        self.emoji_label.setGeometry(85, 200, 55, 55)
        self.emoji_label.setStyleSheet("font-size: 36px;")


        self.cpu_label.setStyleSheet('font-weight: bold; color: #33FFFF;')
        self.gpu_label.setStyleSheet('font-weight: bold; color: #33FFFF;')
        self.gpu_temp_label.setStyleSheet('font-weight: bold; color: #33FFFF;')
        self.ram_label.setStyleSheet('font-weight: bold; color: #33FFFF;')


        self.resource_label.setGeometry(6, 190, 180, 80)

        self.progress_bars_visible = True

    def toggle_progress_bars(self):
        # Przełącz widoczność pasków postępu
        self.progress_bars_visible = not self.progress_bars_visible

        # Ustaw widoczność pasków postępu
        self.cpu_progress.setVisible(self.progress_bars_visible)
        self.gpu_progress.setVisible(self.progress_bars_visible)
        self.gpu_temp_progress.setVisible(self.progress_bars_visible)
        self.ram_progress.setVisible(self.progress_bars_visible)
        self.gpu_temp_label.setVisible(self.progress_bars_visible)
        self.gpu_label.setVisible(self.progress_bars_visible)
        self.cpu_label.setVisible(self.progress_bars_visible)
        self.ram_label.setVisible(self.progress_bars_visible)

        if self.progress_bars_visible:
            self.toggle_button.setText('∧')
            self.widget.setGeometry(0, 0, 150, 260)
            self.resource_label.setGeometry(6, 190, 180, 80)
            self.emoji_label.setGeometry(85, 200, 55, 55)
        else:
            self.toggle_button.setText('∨')
            self.widget.setGeometry(0, 0, 150, 150)
            self.resource_label.setGeometry(10, 35, 180, 80)
            self.emoji_label.setGeometry(45, 90, 55, 55)

        

    def update_resource_info(self):
        # Pobierz informacje o CPU, GPU, temperaturze GPU, RAM i mocy sieci Wi-Fi
        cpu_usage = int(psutil.cpu_percent())
        try:
            gpu_usage = int(GPUtil.getGPUs()[0].load * 100.0)
            gpu_temp = int(GPUtil.getGPUs()[0].temperature)
        except Exception:
            gpu_usage = 0
            gpu_temp = 0

        ram_usage = psutil.virtual_memory().percent

        # Aktualizuj paski postępu i etykietę z informacjami
        self.cpu_progress.setValue(cpu_usage)
        self.gpu_progress.setValue(gpu_usage)
        self.gpu_temp_progress.setValue(gpu_temp)
        self.ram_progress.setValue(int(ram_usage))

        info_text = f'GPU Temp: {gpu_temp}°C\nGPU: {gpu_usage}%\nCPU: {cpu_usage}%\nRAM: {ram_usage}%\n'
        self.resource_label.setText(info_text)
        self.resource_label.setStyleSheet('font-weight: bold; color: #33FFFF;')

        # Ustaw kolory pasków postępu na podstawie obciążenia
        self.set_progress_bar_color(self.cpu_progress, cpu_usage)
        self.set_progress_bar_color(self.gpu_progress, gpu_usage)
        self.set_progress_bar_color(self.gpu_temp_progress, gpu_temp)
        self.set_progress_bar_color(self.ram_progress, ram_usage)

    def set_progress_bar_color(self, progress_bar, value):
        if 0 <= value <= 40:
            color = 'green'
        elif 41 <= value <= 66:
            color = 'orange'
        else:
            color = 'red'

        stylesheet = f'QProgressBar::chunk {{ background-color: {color}; }}'
        progress_bar.setStyleSheet(stylesheet)

    def set_bold_color(self, label):
        label.setStyleSheet('font-weight: bold; color: #33FFFF;')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.pos() - self.offset)

    def enterEvent(self, event):
        # Zmiana opacity na 0.8 po najechaniu myszką
        self.setWindowOpacity(0.8)

    def leaveEvent(self, event):
        # Powrót do opacity na 0.3 po opuszczeniu obszaru okna myszką
        self.setWindowOpacity(0.3)

Stylesheet = """
#Custom_Widget {
    background-color: rgba(0, 32, 37, 50%);  /* Use rgba to set transparency (50% opacity) */
    border-radius: 20px;
    border: 2px solid #33FFFF;
}
#closeButton {
    min-width: 25px;
    min-height: 25px;
    font-family: "Webdings";
    qproperty-text: "r";
    border-radius: 7px;
}

#toggleButton {
    border-radius: 7px;
}


#closeButton:hover {
    color: #ccc;
    background: red;
}


#toggleButton:hover {
    color: #ccc;
    background: orange;
}

#cpuProgressBar, #gpuProgressBar, #gpuTempProgressBar, #ramProgressBar, {
    border: 2px solid #ff2025;
}
#cpuProgressBar::chunk, #gpuProgressBar::chunk, #gpuTempProgressBar::chunk, #ramProgressBar::chunk,  {
    background-color: green;
}
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Dialog()
    w.show()
    sys.exit(app.exec_())