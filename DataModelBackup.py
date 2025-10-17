from PyQt5.QtCore import QObject, pyqtSignal

class DataModelBackup(QObject):
    new_data = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.latest_data = None

    def update_data(self, data: str):
        self.latest_data = data
        self.new_data.emit(data)