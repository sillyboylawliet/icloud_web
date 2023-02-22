import sys
import os
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineDownloadItem
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("1234")

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('iCloud')
        self.setMinimumHeight(800)
        self.setMinimumWidth(700)
        self.setWindowIcon(QIcon('favicon.ico'))
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.close_Tab)
        self.setCentralWidget(self.tabWidget)

        self.webview = WebEngineView(self)  # self必须要有，是将主窗口作为参数，传给浏览器
        self.webview.load(QUrl("https://beta.icloud.com/"))
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars,False)
        self.create_tab(self.webview)


    def create_tab(self, webview):
        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, None)
        self.tabWidget.setCurrentWidget(self.tab)
        self.Layout = QHBoxLayout(self.tab)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.addWidget(webview)

    def close_Tab(self, index):
        if self.tabWidget.count() > 1:
            self.tabWidget.removeTab(index)
        else:
            self.close()


class WebEngineView(QWebEngineView):

    def __init__(self, mainwindow, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.mainwindow = mainwindow
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.page().windowCloseRequested.connect(self.on_windowCloseRequested)
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)

    def on_windowCloseRequested(self):
        the_index = self.mainwindow.tabWidget.currentIndex()
        self.mainwindow.tabWidget.removeTab(the_index)

    def on_downloadRequested(self, downloadItem):
        if downloadItem.isFinished() == False and downloadItem.state() == 0:
            the_filename = downloadItem.url().fileName()
            if len(the_filename) == 0 or "." not in the_filename:
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                the_filename = "下载文件" + cur_time
            self.showOutDialog()
            the_sourceFile = os.path.join(self.default_out_dir, the_filename)
            downloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            downloadItem.setPath(the_sourceFile)
            downloadItem.accept()
            downloadItem.finished.connect(self.on_downloadfinished)

    def showOutDialog(self):
        self.outdir = QFileDialog.getExistingDirectory(self, "选择保存的目录", os.getcwd())
        if self.outdir != "":
            self.default_out_dir = self.outdir

        else:
            self.default_out_dir = os.getcwd()

    def on_downloadfinished(self):
        QMessageBox.information(self, '下载成功', '下载成功', QMessageBox.Ok)


    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView(self.mainwindow)
        self.mainwindow.create_tab(new_webview)
        return new_webview


if __name__ == "__main__":
    app = QApplication(sys.argv)
    the_mainwindow = MainWindow()
    the_mainwindow.show()
    sys.exit(app.exec())