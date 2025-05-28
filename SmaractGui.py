import os, ctypes, sys
from datetime import datetime

def init_controller_dll(dll_name="MCSControl.dll"):
    """
    Locate, add to search path and preload the SmarAct controller DLL.
    Returns (ctypes_lib, absolute_path_to_dll). 
    This fixes the windows error 1114 "A dynamic link library (DLL) initialization routine failed". 
    Needs to be called before PyQt5 imports.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dll_dir  = os.path.join(base_dir, "dll")

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(dll_dir)

    dll_path = os.path.join(dll_dir, dll_name)
    ctypes.WinDLL(dll_path)
    return dll_path

DLL_PATH = init_controller_dll()

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGroupBox, QFormLayout,
    QSpinBox, QPushButton, QLabel,
    QTextEdit
)
from MCS1.smaract_mcs1 import SmarActMCS

class SmaractMSCApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCS Controller")

        self.mcs = SmarActMCS(DLL_PATH)
        self.system_open = False

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.open_btn = QPushButton("Open MCS System")
        self.open_btn.clicked.connect(self.open_system)
        self.status_label = QLabel("System closed")

        layout.addWidget(self.open_btn)
        layout.addWidget(self.status_label)

        self.channel_groups = []
        for ch in (1, 2, 3):
            grp, controls = self._make_channel_box(ch)
            grp.setEnabled(False)
            self.channel_groups.append((grp, controls))
            layout.addWidget(grp)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Log messages will appear here...")
        layout.addWidget(self.log, stretch=1)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _make_channel_box(self, channel):
        box = QGroupBox(f"Channel {channel}")
        form = QFormLayout()

        steps = QSpinBox()
        steps.setRange(-1_000_000, 1_000_000)
        steps.setValue(200)

        amp = QSpinBox()
        amp.setRange(1, 4095)
        amp.setValue(4095)

        freq = QSpinBox()
        freq.setRange(1, 20_000)
        freq.setValue(2000)

        btn = QPushButton("Move")
        btn.clicked.connect(
            lambda _, ch=channel, s=steps, a=amp, f=freq:
                self.move_channel(ch, s.value(), a.value(), f.value())
        )

        form.addRow("Steps:", steps)
        form.addRow("Amplitude:", amp)
        form.addRow("Frequency:", freq)
        form.addRow(btn)
        box.setLayout(form)

        return box, (steps, amp, freq, btn)

    def log_msg(self, text):
        ts = datetime.now().strftime("[%H:%M:%S]")
        self.log.append(f"{ts} {text}")

    def open_system(self):
        try:
            self.log_msg("Opening MCS system...")
            self.mcs.open()
            num = self.mcs.get_num_channels()
            self.status_label.setText(f"System open, {num} channels found")
            self.log_msg(f"System opened with {num} channels")
            self.open_btn.setEnabled(False)
            for grp, _ in self.channel_groups:
                grp.setEnabled(True)
            self.system_open = True
        except Exception as e:
            self.log_msg(f"ERROR: {e}")

    def move_channel(self, ch, steps, amp, freq):
        if not self.system_open:
            self.log_msg("WARNING: System not open")
            return
        try:
            self.log_msg(f"Moving channel {ch}: steps={steps}, amp={amp}, freq={freq}")
            self.mcs.step_move(ch, steps, amp, freq)
            self.log_msg(f"Channel {ch} move completed")
        except Exception as e:
            self.log_msg(f"ERROR: {e}")

    def closeEvent(self, event):
        if self.system_open:
            self.log_msg("Closing MCS system...")
            self.mcs.close()
            self.log_msg("System closed")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SmaractMSCApp()
    w.resize(400, 600)
    w.show()
    sys.exit(app.exec_())
