from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QMessageBox,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QStyle,
    QFileDialog,
)
from PySide6.QtCore import QStandardPaths, QUrl, QFile, QSaveFile, QDir, QIODevice, Slot
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
import sys
from pytube import YouTube
import os
import youtube_dl # client to many multimedia portals
import subprocess



class DownloaderWidget(QWidget):
    """A widget to download a http file to a destination file"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.link_box = QLineEdit()
        self.dest_box = QLineEdit()
        self.progress_bar = QProgressBar()

        self.start_button = QPushButton("Start")
        self.abort_button = QPushButton("Abort")

        self.link_box.setPlaceholderText("Download Link ...")

        self._open_folder_action = self.dest_box.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon), QLineEdit.TrailingPosition
        )
        self._open_folder_action.triggered.connect(self.on_open_folder)

        #  Current QFile
        self.file = None
        # Current QNetworkReply
        self.reply = None

        #  Default http url
        self.link_box.setText(
            "https://www.youtube.com/watch?v=8IEHNUCs7nU"
        )

        #  Default destination dir
        self.dest_box.setText(
            QDir.fromNativeSeparators(
                QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
            )
        )

        # buttons bar layout
        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.start_button)
        hlayout.addWidget(self.abort_button)

        # main layout
        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.link_box)
        vlayout.addWidget(self.dest_box)
        vlayout.addWidget(self.progress_bar)
        vlayout.addStretch()
        vlayout.addLayout(hlayout)

        self.resize(300, 100)

        self.start_button.clicked.connect(self.on_start)
        self.abort_button.clicked.connect(self.on_abort)

    @Slot()
    def on_start(self):

        #  http file
        yt = YouTube(self.link_box.text())

        # destination file
        dest_path = QDir.fromNativeSeparators(self.dest_box.text().strip())

        audio = yt.streams.filter(file_extension='mp4').first()

        
        # download the file 
        out_file = audio.download(output_path=dest_path) 
        print("hey")
        # save the file 
        base, ext = os.path.splitext(out_file) 
        new_file = base + '.mp4'
        os.rename(out_file, new_file) 
        new_file_mp3 = base + '.mp3'
        command = 'ffmpeg -i ' + '"'+new_file + '" -q:a 0 -map a "' + new_file_mp3 +'"' 
        result = subprocess.run(command,shell=True, stdout=subprocess.PIPE)
        print(result.stdout)

    @Slot()
    def on_abort(self):
        """When user press abort button"""
        if self.reply:
            self.reply.abort()
            self.progress_bar.setValue(0)

        if self.file:
            self.file.cancelWriting()

        self.start_button.setDisabled(False)

    @Slot()
    def on_ready_read(self):
        """ Get available bytes and store them into the file"""
        if self.reply:
            if self.reply.error() == QNetworkReply.NoError:
                self.file.write(self.reply.readAll())

    @Slot()
    def on_finished(self):
        """ Delete reply and close the file"""
        if self.reply:
            self.reply.deleteLater()

        if self.file:
            self.file.commit()

        self.start_button.setDisabled(False)

    @Slot(int, int)
    def on_progress(self, bytesReceived: int, bytesTotal: int):
        """ Update progress bar"""
        self.progress_bar.setRange(0, bytesTotal)
        self.progress_bar.setValue(bytesReceived)

    @Slot(QNetworkReply.NetworkError)
    def on_error(self, code: QNetworkReply.NetworkError):
        """ Show a message if an error happen """
        if self.reply:
            QMessageBox.warning(self, "Error Occurred", self.reply.errorString())

    @Slot()
    def on_open_folder(self):

        dir_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if dir_path:
            dest_dir = QDir(dir_path)
            self.dest_box.setText(QDir.fromNativeSeparators(dest_dir.path()))


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = DownloaderWidget()
    w.show()
    sys.exit(app.exec())