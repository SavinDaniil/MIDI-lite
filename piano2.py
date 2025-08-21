import keyboard
import mido
import pygame

from threading import Thread
from time import sleep
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from record import Ui_Form_record


class Piano():
    def __init__(self, parent):
        self.form = parent
        self.rec = Record()
        port = mido.get_output_names()
        self.port = mido.open_output(port[0])
        self.keys = {'1': 48, '2': 49, '3': 50, '4': 51, '5': 52, '6': 53, '7': 54, '8': 55, '9': 56, '0': 57, '-': 58,
                     '=': 59, 'q': 60, 'w': 61, 'e': 62, 'r': 63, 't': 64, 'y': 65, 'u': 66, 'i': 67, 'o': 68, 'p': 69,
                     '[': 70, ']': 71, 'a': 72, 's': 73, 'd': 74, 'f': 75, 'g': 76, 'h': 77, 'j': 78, 'k': 79, 'l': 80,
                     ';': 81, "'": 82, 'enter': 83,
                     'й': 60, 'ц': 61, 'у': 62, 'к': 63, 'е': 64, 'н': 65, 'г': 66, 'ш': 67, 'щ': 68, 'з': 69,
                     'х': 70, 'ъ': 71, 'ф': 72, 'ы': 73, 'в': 74, 'а': 75, 'п': 76, 'р': 77, 'о': 78, 'л': 79, 'д': 80,
                     'ж': 81, "э": 82}

        self.pressed_keys = {key: False for key in self.keys.keys()}
        self.sequence = []
        self.seq_time = []

    def start_piano(self):
        self.mode = 'piano'
        self.stop_thread = False
        self.proc = Thread(target=self.pressing)
        self.proc.start()

    def start_record(self):
        self.rec.show()
        self.mode = 'record'
        self.stop_thread = False
        self.proc = Thread(target=self.pressing)
        self.proc.start()

    def stop(self):
        self.stop_thread = True
        keyboard.send('esc')

    def is_active(self):
        return self.proc.is_alive()

    def pressing(self):
        if self.mode == 'piano':
            while not self.stop_thread:
                key = keyboard.read_event()
                if key.name.lower() == 'esc':
                    break
                if self.stop_thread:
                    break
                if key.event_type == 'down':
                    if key.name.lower() in self.keys:
                        if not self.pressed_keys[key.name.lower()]:
                            self.port.send(mido.Message('note_on', note=self.keys[key.name.lower()]))
                            self.pressed_keys[key.name.lower()] = True

                if key.event_type == 'up':
                    if key.name.lower() in self.keys:
                        self.port.send(mido.Message('note_off', note=self.keys[key.name.lower()]))
                        self.pressed_keys[key.name.lower()] = False
                sleep(0.01)
        elif self.mode == 'record':
            keyboard.send('x')
            self.sequence.clear()
            self.seq_time.clear()
            k = 0
            while not self.stop_thread:
                k += 1
                key = keyboard.read_event()

                if key.name.lower() in self.keys:
                    if k == 1:
                        press1 = datetime.now()
                    elif k != 1:
                        press2 = press1
                        press1 = datetime.now()
                        self.delta = press1 - press2

                if key.name.lower() == 'esc':
                    try:
                        self.seq_time.append(self.delta.total_seconds())
                    except:
                        pass
                    self.rec.hide()
                    self.form.lbl_melody_name.setText('Выбрана записанная мелодия')
                    self.stop_thread = True

                if key.event_type == 'down':
                    if key.name.lower() in self.keys:
                        if not self.pressed_keys[key.name.lower()]:
                            self.port.send(mido.Message('note_on', note=self.keys[key.name.lower()]))
                            self.pressed_keys[key.name.lower()] = True
                            self.sequence.append(mido.Message('note_on', note=self.keys[key.name.lower()]))
                            try:
                                self.seq_time.append(self.delta.total_seconds())
                            except:
                                pass

                if key.event_type == 'up':
                    if key.name.lower() in self.keys:
                        self.port.send(mido.Message('note_off', note=self.keys[key.name.lower()]))
                        self.pressed_keys[key.name.lower()] = False
                        self.sequence.append(mido.Message('note_off', note=self.keys[key.name.lower()]))
                sleep(0.01)

    def get_sequence(self):
        return self.sequence, self.seq_time

    def change_sequence(self, new_sequence, new_seq_time):
        self.sequence = new_sequence
        self.seq_time = new_seq_time

    def stop_melody(self):
        self.stop_thread_melody = True

    def playing_melody(self):
        self.stop_thread_melody = False
        self.proc_melody = Thread(target=self.play)
        self.proc_melody.start()

    def play(self):
        while not self.stop_thread_melody:
            try:
                for i in range(len(self.sequence)):
                    if self.stop_thread_melody:
                        break
                    self.port.send(self.sequence[i])
                    try:
                        if i % 2 == 0:
                            sleep(self.seq_time[i // 2])
                    except:
                        pass
                self.stop_thread_melody = True
            except:
                pass


class Music():
    def __init__(self):
        self.filenames = ['melodies/Never-Gonna-Give-You-Up-3.mp3', 'melodies/Star_Wars__Imperial_March.mp3',
                          'melodies/Classic-Song.mp3', 'melodies/Pirates-of-the-Caribbean.mp3',
                          'melodies/Vampire-Killer.mp3', 'melodies/Tetris.mp3']

    def start(self, number):
        self.filename = self.filenames[number]
        self.stop_thread = False
        self.proc = Thread(target=self.playback)
        self.proc.start()

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        try:
            pygame.mixer.music.pause()
        except:
            print('pause error')

    def resume(self):
        try:
            pygame.mixer.music.unpause()
        except:
            print('resume error')

    def set_volume(self, volume):
        self.volume = volume
        try:
            pygame.mixer.music.set_volume(self.volume / 100)
        except:
            pass

    def playback(self):
        pygame.mixer.init()
        try:
            pygame.mixer.music.set_volume(self.volume / 100)
        except:
            pygame.mixer.music.set_volume(0.4)
        clock = pygame.time.Clock()
        pygame.mixer.music.load(self.filename)
        pygame.mixer.music.play(-1)
        while pygame.mixer.music.get_busy():
            clock.tick(30)


class Record(QWidget, Ui_Form_record):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

    def closeEvent(self, event):
        QtWidgets.QMessageBox.question(self, "Предупреждение",
                                       "Во время записи мелодии нельзя закрыть окно",
                                       QtWidgets.QMessageBox.Ok)
        event.ignore()
