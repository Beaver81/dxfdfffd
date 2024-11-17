import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QMessageBox, QCalendarWidget, QTimeEdit, QColorDialog, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QColor

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Планувальник завдань")
window.setFixedSize(500, 570)
window.setStyleSheet("""
    QWidget {
        background-color: #f1f2f6;
        color: #2f3542;
        font-family: Arial;
    }
    QLabel {
        font-size: 20px;
        font-weight: bold;
        color: #57606f;
        margin: 5px 0;
    }
    QLineEdit, QTimeEdit, QListWidget {
        padding: 8px;
        border: 1px solid #dfe4ea;
        border-radius: 5px;
        background: #ffffff;
        font-size: 14px;
    }
    QCalendarWidget {
        border: none;
        background: #f7f8fa;
        border-radius: 8px;
        font-size: 12px;
        margin-bottom: 10px;
    }
    QPushButton {
        padding: 10px;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
    }
    QPushButton#addButton {
        background-color: #2ed573;
        color: #ffffff;
    }
    QPushButton#deleteButton {
        background-color: #ff4757;
        color: #ffffff;
    }
    QPushButton#editButton {
        background-color: #ffa502;
        color: #ffffff;
    }
    QPushButton#completeButton {
        background-color: #3742fa;
        color: #ffffff;
    }
    QPushButton:hover {
        opacity: 0.9;
    }
""")

layout = QVBoxLayout()
layout.setContentsMargins(10, 10, 10, 10)
layout.setSpacing(8)

title = QLabel("Планувальник завдань")
title.setAlignment(Qt.AlignCenter)
layout.addWidget(title)

calendar = QCalendarWidget()
calendar.setGridVisible(True)
calendar.setMaximumHeight(180)
layout.addWidget(calendar)

input_layout = QHBoxLayout()
task_input = QLineEdit()
task_input.setPlaceholderText("Введіть завдання...")
task_input.setMaximumWidth(250)
input_layout.addWidget(task_input)

time_input = QTimeEdit()
time_input.setDisplayFormat("HH:mm")
time_input.setMaximumWidth(80)
input_layout.addWidget(time_input)

layout.addLayout(input_layout)

task_color = QColor("#3742fa")

def choose_color():
    global task_color
    color = QColorDialog.getColor()
    if color.isValid():
        task_color = color
        color_button.setStyleSheet(f"background-color: {color.name()}; color: #ffffff;")

color_button = QPushButton("Вибрати колір")
color_button.setObjectName("colorButton")
color_button.clicked.connect(choose_color)
layout.addWidget(color_button)

task_list = QListWidget()
task_list.setMinimumHeight(120)
layout.addWidget(task_list)

def add_task_item(text, task_time, task_date, color):
    task_text = f"{task_date.toString('dd.MM.yyyy')} {task_time.toString('HH:mm')} - {text}"
    item = QListWidgetItem(task_text)
    item.setForeground(color)
    item.setData(Qt.UserRole, {"time": task_time, "date": task_date})
    task_list.addItem(item)

def add_task():
    task_text = task_input.text()
    task_time = time_input.time()
    task_date = calendar.selectedDate()
    
    if not task_text:
        QMessageBox.warning(window, "Помилка", "Введіть завдання.")
        return

    add_task_item(task_text, task_time, task_date, task_color)
    task_input.clear()
    time_input.setTime(QTime.currentTime())

add_button = QPushButton("Додати завдання")
add_button.setObjectName("addButton")
add_button.clicked.connect(add_task)
layout.addWidget(add_button)

def delete_task():
    selected_task = task_list.currentRow()
    if selected_task != -1:
        task_list.takeItem(selected_task)
    else:
        QMessageBox.warning(window, "Помилка", "Виберіть завдання для видалення.")

delete_button = QPushButton("Видалити завдання")
delete_button.setObjectName("deleteButton")
delete_button.clicked.connect(delete_task)
layout.addWidget(delete_button)

def edit_task():
    selected_task = task_list.currentRow()
    if selected_task != -1:
        item = task_list.item(selected_task)
        task_text = item.text()
        if " - " in task_text:
            task_date, task_time, task_name = task_text.split(" ", 2)
            task_input.setText(task_name.split(" - ", 1)[-1])  # Safe split, handles missing dash gracefully
            time_input.setTime(QTime.fromString(task_time, "HH:mm"))
            task_list.takeItem(selected_task)
        else:
            QMessageBox.warning(window, "Помилка", "Неправильний формат завдання.")
    else:
        QMessageBox.warning(window, "Помилка", "Виберіть завдання для редагування.")

edit_button = QPushButton("Редагувати завдання")
edit_button.setObjectName("editButton")
edit_button.clicked.connect(edit_task)
layout.addWidget(edit_button)

def mark_task_complete():
    selected_task = task_list.currentRow()
    if selected_task != -1:
        item = task_list.item(selected_task)
        item.setForeground(QColor("#95a5a6"))
    else:
        QMessageBox.warning(window, "Помилка", "Виберіть завдання для завершення.")

complete_button = QPushButton("Завершити завдання")
complete_button.setObjectName("completeButton")
complete_button.clicked.connect(mark_task_complete)
layout.addWidget(complete_button)

def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
            for task_data in tasks:
                add_task_item(task_data["text"], QTime.fromString(task_data["time"], "HH:mm"), 
                              QDate.fromString(task_data["date"], "dd.MM.yyyy"), QColor(task_data["color"]))
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def save_tasks():
    tasks = []
    for i in range(task_list.count()):
        item = task_list.item(i)
        task_data = {
            "text": item.text(),
            "time": item.data(Qt.UserRole)["time"].toString("HH:mm"),
            "date": item.data(Qt.UserRole)["date"].toString("dd.MM.yyyy"),
            "color": item.foreground().color().name()
        }
        tasks.append(task_data)
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)

def check_tasks():
    current_time = QTime.currentTime()
    current_date = QDate.currentDate()
    for i in range(task_list.count()):
        item = task_list.item(i)
        task_date = item.data(Qt.UserRole)["date"]
        task_time = item.data(Qt.UserRole)["time"]

        if task_date == current_date and task_time == current_time:
            QMessageBox.information(window, "Нагадування", f"Пора виконати завдання: {item.text()}")
            task_list.takeItem(i)
            break

timer = QTimer()
timer.timeout.connect(check_tasks)
timer.start(60000)

app.aboutToQuit.connect(save_tasks)
load_tasks()

window.setLayout(layout)
window.show()
sys.exit(app.exec_())
