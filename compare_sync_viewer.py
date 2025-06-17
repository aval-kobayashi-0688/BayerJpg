import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QHBoxLayout, QVBoxLayout, QWidget, QLabel
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

class SyncGraphicsView(QGraphicsView):
    zoomed = pyqtSignal(float)
    scrolled = pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zoom = 1.0
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self._zoom *= zoom_factor
        self.scale(zoom_factor, zoom_factor)
        self.zoomed.emit(self._zoom)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        h = self.horizontalScrollBar().value()
        v = self.verticalScrollBar().value()
        self.scrolled.emit(h, v)

    def set_zoom(self, zoom):
        factor = zoom / self._zoom
        self.scale(factor, factor)
        self._zoom = zoom

    def set_scroll(self, h, v):
        self.horizontalScrollBar().setValue(h)
        self.verticalScrollBar().setValue(v)

class MainWindow(QMainWindow):
    def __init__(self, img1_path, img2_path):
        super().__init__()
        self.setWindowTitle("同期画像ビューア")

        # 画像読み込み
        pixmap1 = QPixmap(img1_path)
        pixmap2 = QPixmap(img2_path)

        # シーンとビュー作成
        self.scene1 = QGraphicsScene()
        self.scene1.addPixmap(pixmap1)
        self.view1 = SyncGraphicsView(self.scene1)

        self.scene2 = QGraphicsScene()
        self.scene2.addPixmap(pixmap2)
        self.view2 = SyncGraphicsView(self.scene2)

        # ファイル名ラベル
        label1 = QLabel(img1_path)
        label1.setAlignment(Qt.AlignCenter)
        label2 = QLabel(img2_path)
        label2.setAlignment(Qt.AlignCenter)

        # シグナル接続（ズーム・スクロール同期）
        self.view1.zoomed.connect(self.view2.set_zoom)
        self.view2.zoomed.connect(self.view1.set_zoom)
        self.view1.scrolled.connect(self.view2.set_scroll)
        self.view2.scrolled.connect(self.view1.set_scroll)

        # 画像＋ラベルのレイアウト
        vbox1 = QVBoxLayout()
        vbox1.addWidget(label1)
        vbox1.addWidget(self.view1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(label2)
        vbox2.addWidget(self.view2)

        # 横並びレイアウト
        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)

        container = QWidget()
        container.setLayout(hbox)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow('Mandrill_bayer_color_jpg_q25.bmp', 'Mandrill_bayer_color_jpg_q95.bmp')
    window.show()
    sys.exit(app.exec_())