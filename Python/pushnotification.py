import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QTextEdit, QCheckBox, QPushButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest
import requests


APPS = [
    {"name": "Android · App1",        "platform": "Android", "project": "app1-firebase-project",
     "key_path": "/path/to/service-account-app1.json"},
    {"name": "Android · App2",        "platform": "Android", "project": "app2-firebase-project",
     "key_path": "/path/to/service-account-app2.json"},
    {"name": "iOS · App3",            "platform": "iOS",     "project": "app3-firebase-project",
     "key_path": "/path/to/service-account-app3.json"},
    {"name": "iOS · App4",            "platform": "iOS",     "project": "app4-firebase-project",
     "key_path": "/path/to/service-account-app4.json"},
]


CARD_STYLE = """
    background-color: white;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
"""

COMBO_STYLE = """
    background-color: white;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    font-size: 14px;
    padding: 6px 10px;
"""

INPUT_STYLE = """
    background-color: white;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    font-size: 14px;
    padding: 8px;
"""


class SendWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, app_info, message):
        super().__init__()
        self.app_info = app_info
        self.message = message

    def run(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.app_info["key_path"],
                scopes=["https://www.googleapis.com/auth/firebase.messaging"]
            )
            creds.refresh(GoogleRequest())
            token = creds.token

            url = f"https://fcm.googleapis.com/v1/projects/{self.app_info['project']}/messages:send"
            payload = {"message": self.message}
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "Authorization": f"Bearer {token}"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.ok:
                self.finished.emit({"success": True, "text": f"Notification sent to {self.message['topic']}."})
            else:
                self.finished.emit({"success": False, "text": f"FCM failed: {resp.status_code} - {resp.text}"})
        except Exception as e:
            self.finished.emit({"success": False, "text": f"Error: {str(e)}"})


class PushNotificationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCM Push Sender")
        self.resize(1080, 800)
        self.setMinimumSize(1080, 800)
        self.setStyleSheet("background-color: #F3F6FB;")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ──
        header = QFrame()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #14213D, stop:1 #2456A6);
        """)
        header.setFixedHeight(112)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(38, 22, 0, 0)
        title = QLabel("FCM Push Sender")
        title.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        hl.addWidget(title)
        subtitle = QLabel("Send notifications to multiple apps without changing the code.")
        subtitle.setStyleSheet("color: #D9E7FF; font-size: 14px;")
        hl.addWidget(subtitle)
        root.addWidget(header)

        # ── BODY ──
        body = QHBoxLayout()
        body.setContentsMargins(30, 30, 30, 30)
        body.setSpacing(22)
        root.addLayout(body)

        # ── LEFT CARD ──
        left_card = QFrame()
        left_card.setStyleSheet(CARD_STYLE)
        left_card.setFixedSize(330, 560)
        lc = QVBoxLayout(left_card)
        lc.setContentsMargins(24, 22, 24, 0)
        lc.setSpacing(0)

        self._add_label(lc, "DESTINATION", "#14213D", 15, True, 0, 0)
        self._add_label(lc, "App and Firebase configuration", "#64748B", 12, False, 0, 8)
        lc.addSpacing(20)
        self._add_label(lc, "App", "#334155", 13, True, 0, 0)

        self.cmb_app = QComboBox()
        self.cmb_app.setStyleSheet(COMBO_STYLE)
        self.cmb_app.setFixedHeight(38)
        for a in APPS:
            self.cmb_app.addItem(a["name"])
        lc.addWidget(self.cmb_app)
        lc.addSpacing(28)

        self._add_label(lc, "Firebase Project", "#334155", 13, True, 0, 0)
        self.lbl_project = QLabel()
        self.lbl_project.setStyleSheet("""
            background-color: #EFF4FC; border-radius: 7px;
            color: #2456A6; font-size: 14px; font-weight: bold;
            padding: 10px 12px;
        """)
        self.lbl_project.setFixedHeight(42)
        lc.addWidget(self.lbl_project)
        lc.addSpacing(30)

        self._add_label(lc, "Android Priority", "#334155", 13, True, 0, 0)
        self.cmb_priority = QComboBox()
        self.cmb_priority.setStyleSheet(COMBO_STYLE)
        self.cmb_priority.setFixedHeight(38)
        self.cmb_priority.addItems(["high", "normal"])
        self.cmb_priority.setCurrentIndex(0)
        lc.addWidget(self.cmb_priority)
        lc.addSpacing(30)

        self._add_label(lc, "Badge iOS (default 1 for background)", "#334155", 13, True, 0, 0)
        self.cmb_badge = QComboBox()
        self.cmb_badge.setStyleSheet(COMBO_STYLE)
        self.cmb_badge.setFixedHeight(38)
        self.cmb_badge.addItems(["0", "1", "2", "3", "4", "5"])
        self.cmb_badge.setCurrentIndex(1)
        lc.addWidget(self.cmb_badge)
        lc.addSpacing(16)

        self.chk_sound = QCheckBox("With alert sound")
        self.chk_sound.setStyleSheet("color: #334155; font-size: 13px; font-weight: bold;")
        self.chk_sound.setChecked(True)
        lc.addWidget(self.chk_sound)
        lc.addSpacing(4)

        self.chk_reset_badge = QCheckBox("Reset badge on device (iOS)")
        self.chk_reset_badge.setStyleSheet("color: #334155; font-size: 13px; font-weight: bold;")
        lc.addWidget(self.chk_reset_badge)
        lc.addSpacing(8)

        ios_tip = QLabel("On iOS the ios_ prefix is automatically applied to the topic.")
        ios_tip.setStyleSheet("color: #64748B; font-size: 11px;")
        ios_tip.setWordWrap(True)
        lc.addWidget(ios_tip)

        body.addWidget(left_card)

        # ── RIGHT CARD ──
        right_card = QFrame()
        right_card.setStyleSheet(CARD_STYLE)
        right_card.setFixedSize(668, 560)
        rc = QVBoxLayout(right_card)
        rc.setContentsMargins(28, 22, 28, 0)
        rc.setSpacing(0)

        self._add_label(rc, "MESSAGE", "#14213D", 15, True, 0, 0)
        self._add_label(rc, "The fields below form the payload sent to FCM.", "#64748B", 12, False, 0, 8)
        rc.addSpacing(14)

        row1 = QHBoxLayout()
        row1.setSpacing(20)
        col1 = QVBoxLayout()
        col1.setSpacing(0)
        self._add_label(col1, "Topic", "#334155", 13, True, 0, 0)
        self.txt_topic = QLineEdit("teste12345")
        self.txt_topic.setStyleSheet(INPUT_STYLE)
        self.txt_topic.setFixedHeight(38)
        col1.addWidget(self.txt_topic)
        row1.addLayout(col1)

        col2 = QVBoxLayout()
        col2.setSpacing(0)
        self._add_label(col2, "Title", "#334155", 13, True, 0, 0)
        self.txt_title = QLineEdit()
        self.txt_title.setStyleSheet(INPUT_STYLE)
        self.txt_title.setFixedHeight(38)
        col2.addWidget(self.txt_title)
        row1.addLayout(col2)
        rc.addLayout(row1)
        rc.addSpacing(28)

        self._add_label(rc, "Message / HTML", "#334155", 13, True, 0, 0)
        self.txt_message = QTextEdit()
        self.txt_message.setStyleSheet("""
            background-color: white; border: 1px solid #CBD5E1;
            border-radius: 7px; font-size: 14px; padding: 8px;
        """)
        self.txt_message.setFixedHeight(170)
        rc.addWidget(self.txt_message)
        rc.addSpacing(30)

        row2 = QHBoxLayout()
        row2.setSpacing(28)
        self.btn_send = QPushButton("Send notification")
        self.btn_send.setStyleSheet("""
            background-color: #16A34A; border-radius: 7px;
            color: white; font-size: 15px; font-weight: bold;
            padding: 12px 20px;
        """)
        self.btn_send.setFixedSize(260, 48)
        self.btn_send.clicked.connect(self.send)
        row2.addWidget(self.btn_send)

        self.lbl_status = QLabel("Ready to send.")
        self.lbl_status.setStyleSheet("color: #475569; font-size: 13px;")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setFixedWidth(320)
        row2.addWidget(self.lbl_status)
        rc.addLayout(row2)
        rc.addSpacing(12)

        self._add_label(rc, "Sent Payload", "#334155", 13, True, 0, 0)
        self.txt_payload = QTextEdit()
        self.txt_payload.setReadOnly(True)
        self.txt_payload.setStyleSheet("""
            background-color: #F8FAFC; border: 1px solid #CBD5E1;
            border-radius: 7px; font-size: 12px; padding: 8px;
            font-family: Consolas, monospace;
        """)
        rc.addWidget(self.txt_payload, 1)

        body.addWidget(right_card)

        # initial selection
        self.cmb_app.currentIndexChanged.connect(self._on_app_selected)
        self.cmb_app.setCurrentIndex(0)

    def _add_label(self, parent, text, color, size, bold, left, top):
        lbl = QLabel(text)
        weight = "bold" if bold else "normal"
        lbl.setStyleSheet(f"color: {color}; font-size: {size}px; font-weight: {weight};")
        if left or top:
            lbl.setContentsMargins(left, top, 0, 0)
        parent.addWidget(lbl)

    def _fcm_topic(self, platform, topic):
        if platform == "iOS":
            return "ios_" + topic
        return topic

    def _on_app_selected(self):
        idx = self.cmb_app.currentIndex()
        if idx < 0:
            return
        app = APPS[idx]
        self.lbl_project.setText(app["project"])
        is_ios = app["platform"] == "iOS"
        self.cmb_priority.setEnabled(not is_ios)
        self.cmb_badge.setEnabled(is_ios)
        self.chk_reset_badge.setEnabled(is_ios)
        if not is_ios:
            self.chk_reset_badge.setChecked(False)

    def send(self):
        topic = self.txt_topic.text().strip()
        title = self.txt_title.text().strip()
        message_body = self.txt_message.toPlainText()

        idx = self.cmb_app.currentIndex()
        app = APPS[idx]
        with_sound = self.chk_sound.isChecked()
        reset_badge = self.chk_reset_badge.isChecked()

        if reset_badge:
            message = {"topic": self._fcm_topic(app["platform"], topic)}
            if app["platform"] == "iOS":
                aps = {"alert": "", "badge": 0, "content-available": 1}
                message["apns"] = {
                    "headers": {"apns-priority": "5"},
                    "payload": {"aps": aps}
                }
            else:
                message["android"] = {"priority": "high"}
        else:
            if not topic or not title or not message_body.strip():
                self._update_status("Fill in topic, title and message before sending.", False)
                return
            fcm_topic = self._fcm_topic(app["platform"], topic)
            data = {"title": title, "body": message_body}
            message = {"topic": fcm_topic, "data": data}
            if app["platform"] == "iOS":
                ios_alert = {"title": title, "body": message_body}
                message["notification"] = ios_alert
                aps = {"badge": int(self.cmb_badge.currentText())}
                if with_sound:
                    aps["sound"] = "default"
                message["apns"] = {
                    "headers": {"apns-priority": "10"},
                    "payload": {"aps": aps}
                }
            else:
                android_config = {"priority": self.cmb_priority.currentText()}
                if with_sound:
                    android_config["notification"] = {"sound": "default"}
                message["android"] = android_config

        payload_display = {"message": message}
        self.txt_payload.setText(json.dumps(payload_display, indent=2, ensure_ascii=False))

        self.btn_send.setEnabled(False)
        self._update_status(f"Sending notification to {app['name']}...", True)

        self.worker = SendWorker(app, message)
        self.worker.finished.connect(self._on_result)
        self.worker.start()

    def _on_result(self, result):
        self.btn_send.setEnabled(True)
        self._update_status(result["text"], result["success"])

    def _update_status(self, text, success):
        self.lbl_status.setText(text)
        color = "#15803D" if success else "#B91C1C"
        self.lbl_status.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PushNotificationWindow()
    win.show()
    sys.exit(app.exec())
