import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit
)
from MCS1.smaract_mcs1 import SmarActMCS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmarAct GUI")
        self.mcs = None
        self._build_ui()
        
    def _build_ui(self):
        w = QWidget()
        v = QVBoxLayout()
        # Connect / Disconnect
        h0 = QHBoxLayout()
        self.btn_connect = QPushButton("Connect")
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setEnabled(False)
        h0.addWidget(self.btn_connect)
        h0.addWidget(self.btn_disconnect)
        v.addLayout(h0)
        # Channel selector
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Channel:"))
        self.cb_channel = QComboBox()
        self.cb_channel.setEnabled(False)
        h1.addWidget(self.cb_channel)
        v.addLayout(h1)
        # Relative move
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Δ (nm):"))
        self.le_delta = QLineEdit("1000")
        h2.addWidget(self.le_delta)
        self.btn_rel = QPushButton("Move Relative")
        self.btn_rel.setEnabled(False)
        h2.addWidget(self.btn_rel)
        v.addLayout(h2)
        # Step move
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Steps:"))
        self.le_steps = QLineEdit("10000")
        h3.addWidget(self.le_steps)
        h3.addWidget(QLabel("Amp:"))
        self.le_amp = QLineEdit("4095")
        h3.addWidget(self.le_amp)
        h3.addWidget(QLabel("Freq:"))
        self.le_freq = QLineEdit("2000")
        h3.addWidget(self.le_freq)
        self.btn_step = QPushButton("Step Move")
        self.btn_step.setEnabled(False)
        h3.addWidget(self.btn_step)
        v.addLayout(h3)
        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        v.addWidget(self.log)
        # signals
        self.btn_connect.clicked.connect(self.connect)
        self.btn_disconnect.clicked.connect(self.disconnect)
        self.btn_rel.clicked.connect(self.move_relative)
        self.btn_step.clicked.connect(self.step_move)
        w.setLayout(v)
        self.setCentralWidget(w)
        
    def log_msg(self, text):
        self.log.append(text)
        
    def connect(self):
        try:
            self.mcs = SmarActMCS("dll/MCSControl.dll")
            self.mcs.open()
            n = self.mcs.get_num_channels()
            self.cb_channel.clear()
            for i in range(n):
                self.cb_channel.addItem(str(i))
            self.log_msg(f"Connected: {n} channels found")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.cb_channel.setEnabled(True)
            self.btn_rel.setEnabled(True)
            self.btn_step.setEnabled(True)
        except Exception as e:
            self.log_msg(f"Error: {e}")
        
    def disconnect(self):
        if self.mcs:
            self.mcs.close()
            self.log_msg("Disconnected")
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            self.cb_channel.setEnabled(False)
            self.btn_rel.setEnabled(False)
            self.btn_step.setEnabled(False)
            self.mcs = None
        
    def move_relative(self):
        ch = int(self.cb_channel.currentText())
        dn = int(self.le_delta.text())
        def job():
            try:
                self.mcs.move_relative(ch, dn)
                self.log_msg(f"Relative move {dn} nm on ch {ch} done")
            except Exception as e:
                self.log_msg(f"Error: {e}")
        threading.Thread(target=job, daemon=True).start()
        
    def step_move(self):
        ch = int(self.cb_channel.currentText())
        steps = int(self.le_steps.text())
        amp = int(self.le_amp.text())
        freq = int(self.le_freq.text())
        def job():
            try:
                self.mcs.step_move(ch, steps, amp, freq)
                self.log_msg(f"Step move {steps} on ch {ch} done")
            except Exception as e:
                self.log_msg(f"Error: {e}")
        threading.Thread(target=job, daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
