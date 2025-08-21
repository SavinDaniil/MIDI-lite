import sys
import sqlite3

from mido import Message
from time import sleep
from json import loads

from midi_interface import Ui_MainWindow
from login import Ui_Form_login
from saving import Ui_Form_save
from open import Ui_Form_open

from piano2 import Piano, Music

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class Midi(QMainWindow, Ui_MainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModal)
        self.show()
        self.user_id = user_id
        self.piano = Piano(self)
        self.music = Music()
        self.initUI()

    def initUI(self):
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.play_melody.clicked.connect(self.playing)
        self.record_melody.clicked.connect(self.recording)
        self.save_melody.clicked.connect(self.saving)
        self.open_melody.clicked.connect(self.open)
        self.music1.clicked.connect(self.music_run)
        self.music2.clicked.connect(self.music_run)
        self.music3.clicked.connect(self.music_run)
        self.music4.clicked.connect(self.music_run)
        self.music5.clicked.connect(self.music_run)
        self.music6.clicked.connect(self.music_run)
        self.btn_play.clicked.connect(self.music_resume)
        self.btn_pause.clicked.connect(self.music_pause)
        self.slider_volume.valueChanged.connect(self.set_volume)

    def tab_changed(self):
        try:
            self.piano.stop()
        except:
            pass
        try:
            if self.tabWidget.currentIndex() == 2:
                self.change_tab_to_piano()
        except:
            pass

    def recording(self):
        try:
            self.piano.stop()
        except:
            pass
        try:
            self.music.stop()
        except:
            pass
        self.piano.start_record()

    def playing(self):
        try:
            self.music.stop()
        except:
            pass
        self.piano.stop_melody()
        sleep(0.5)
        self.piano.playing_melody()

    def music_run(self):
        self.piano.stop_melody()
        if self.sender() == self.music1:
            number = 0
        if self.sender() == self.music2:
            number = 1
        if self.sender() == self.music3:
            number = 2
        if self.sender() == self.music4:
            number = 3
        if self.sender() == self.music5:
            number = 4
        if self.sender() == self.music6:
            number = 5
        self.music.start(number)

    def music_pause(self):
        try:
            self.music.pause()
        except:
            print('music_pause error')

    def music_resume(self):
        try:
            self.music.resume()
        except:
            print('music_resume error')

    def set_volume(self):
        self.lbl_volume.setText(f'Громкость: {self.slider_volume.value()}%')
        self.music.set_volume(self.slider_volume.value())

    def saving(self):
        self.saving = Save(self, self.user_id, self.piano.get_sequence())

    def open(self):
        self.opening = Open(self, self.user_id, self.piano)

    def change_tab_to_piano(self):
        try:
            self.music.stop()
        except:
            pass
        self.piano.start_piano()

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self, "Подтверждение закрытия окна",
                                                "Вы действительно хотите закрыть окно?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            try:
                self.piano.stop()
                self.piano.stop_melody()
            except:
                print('closeEvent error (piano)')
            try:
                self.music.stop()
            except:
                print('closeEvent error (music)')
        else:
            event.ignore()
        QApplication.closeAllWindows()


class LoginForm(QWidget, Ui_Form_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.initUI()

    def initUI(self):
        try:
            file = open('log.txt', 'r').readlines()
            self.lineEdit_usr.setText(file[0].strip())
            self.lineEdit_psw.setText(file[1])
        except:
            pass

        self.btn_login.clicked.connect(self.confirm)

    def confirm(self):
        user = self.lineEdit_usr.text().strip()
        password = self.lineEdit_psw.text().strip()
        if password and user:
            con = sqlite3.connect('midi_base.sqlite')
            cur = con.cursor()
            query = """SELECT login FROM users"""
            result = cur.execute(query).fetchall()
            if (user,) not in result:
                query = f"INSERT INTO users(login, password) VALUES('{user}', '{password}')"
                cur.execute(query)
                con.commit()
                file = open('log.txt', 'w')
                file.write(f'{user}\n{password}')
                file.close()
            else:
                query = f"SELECT password FROM users WHERE login = '{user}'"
                result = cur.execute(query).fetchone()[0]
                if password == result:
                    query = f"SELECT id FROM users WHERE login = '{user}'"
                    result = cur.execute(query).fetchone()[0]
                    self.hide()
                    self.form = Midi(result)
                    file = open('log.txt', 'w')
                    file.write(f'{user}\n{password}')
                    file.close()
                self.lbl_login_error.setText('Неправильный пароль')
                con.close()
        else:
            self.lbl_login_error.setText('Некорректный ввод')


class Save(QWidget, Ui_Form_save):
    def __init__(self, parent, user_id, *sequence):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.user_id = user_id
        self.sequence = sequence[0][0]
        self.seq_time = sequence[0][1]
        self.form = parent
        self.initUI()

    def initUI(self):
        self.btn_save.clicked.connect(self.saving)
        self.btn_cansel.clicked.connect(self.close)

    def saving(self):
        if self.lineEdit_name.text().strip() and self.sequence:
            con = sqlite3.connect('midi_base.sqlite')
            cur = con.cursor()

            name = self.lineEdit_name.text().strip()
            result = cur.execute(f"SELECT title FROM melodies WHERE user_id = {self.user_id}").fetchall()
            result = [i[0] for i in result]

            if name in result:
                confirm = QtWidgets.QMessageBox.question(self, "Подтверждение сохранения мелодии",
                                                         """Мелодия с таким именем уже есть.
Вы действительно хотите перезаписать мелодию?""",
                                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                         QtWidgets.QMessageBox.No)
                if confirm == QtWidgets.QMessageBox.Yes:
                    query = f"""UPDATE melodies SET sequence = "{self.sequence}"
WHERE user_id = {self.user_id} AND title = '{name}'"""
                    cur.execute(query)
                    con.commit()
                    query = f"""UPDATE melodies SET seq_time = "{self.seq_time}"
WHERE user_id = {self.user_id} AND title = '{name}'"""
                    cur.execute(query)
                    con.commit()
                else:
                    return

            else:
                query = f"""INSERT INTO melodies(title, sequence, seq_time, user_id) 
VALUES('{name}', "{self.sequence}", "{self.seq_time}", {self.user_id})"""
                cur.execute(query)
                con.commit()

            self.hide()
            self.lineEdit_name.setText('')
            self.lbl_saving_error.setText('')
            con.close()
            self.form.lbl_melody_name.setText(f'Выбранная мелодия: {name}')
        else:
            if not self.lineEdit_name.text().strip():
                self.lbl_saving_error.setText('Некорректное имя')
            else:
                self.lbl_saving_error.setText('Мелодия не записана')

    def close(self):
        self.hide()
        self.lbl_saving_error.setText('')
        self.lineEdit_name.setText('')


class Open(QWidget, Ui_Form_open):
    def __init__(self, parent, user_id, piano):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.show()
        self.piano = piano
        self.lineEdit_search.setStyleSheet('color: #808080;')
        self.user_id = user_id
        self.form = parent
        self.tableWidget.hideColumn(0)
        self.tableWidget.setSortingEnabled(True)
        self.initUI()

    def initUI(self):
        self.btn_search.clicked.connect(self.searching)
        self.lineEdit_search.installEventFilter(self)
        self.btn_choose.clicked.connect(self.choosing)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.lineEdit_search.setStyleSheet('color: black;')
            if self.lineEdit_search.text() == 'Введите имя':
                self.lineEdit_search.setText('')
        return super(Open, self).eventFilter(obj, event)

    def searching(self):
        self.tableWidget.setRowCount(0)
        if self.lineEdit_search.text() and self.lineEdit_search.text() != 'Введите имя':
            name = self.lineEdit_search.text()
            query = f"""SELECT id, title FROM melodies WHERE user_id = {self.user_id} AND title LIKE '%{name}%'"""
        else:
            query = f"""SELECT id, title FROM melodies WHERE user_id = {self.user_id}"""

        con = sqlite3.connect('midi_base.sqlite')
        cur = con.cursor()
        result = cur.execute(query).fetchall()

        for i, row in enumerate(result):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        con.close()

    def choosing(self):
        row = self.tableWidget.currentRow()
        self.tableWidget.showColumn(0)
        item = self.tableWidget.item(row, 0)
        self.tableWidget.hideColumn(0)
        id = item.text()

        query = f"""SELECT sequence, seq_time, title FROM melodies WHERE id = {id}"""
        con = sqlite3.connect('midi_base.sqlite')
        cur = con.cursor()
        result = cur.execute(query).fetchone()
        con.close()

        result_seq = result[0]
        result_seq = result_seq[1:-1]
        result_seq = result_seq.split('), ')
        result_seq = [i[8:] for i in result_seq]
        result_seq = [i.split(', ')[2] for i in result_seq]

        sequence = []
        for k, i in enumerate(result_seq):
            if k % 2 == 0:
                sequence.append(Message('note_on', note=int(i[5:])))
            else:
                sequence.append(Message('note_off', note=int(i[5:])))

        result_time = result[1]
        seq_time = loads(result_time)

        name = result[2]
        self.form.lbl_melody_name.setText(f'Выбранная мелодия: {name}')

        self.piano.change_sequence(sequence, seq_time)
        self.tableWidget.setRowCount(0)
        self.lineEdit_search.setText('Введите имя')
        self.lbl_error.setText('')
        self.hide()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginForm()
    sys.excepthook = except_hook
    sys.exit(app.exec())
