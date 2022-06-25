import sys, os, sqlite3, random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pygame import mixer
from mutagen.mp3 import MP3
import styles

connection = sqlite3.connect("music_player.db")
cursor = connection.cursor()


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        # MAIN CONFIGURATIONS
        self.setWindowTitle("Music Player")
        # self.setStyleSheet("background-color: black")
        self.setGeometry(800, 400, 480, 700)
        self.setMaximumSize(480, 700)
        self.setMinimumSize(480, 700)
        self.setWindowIcon(QIcon("icons/music_icon.png"))
        # LAYOUTS
        main_vertical_layout = QVBoxLayout()
        vertical_layout = QVBoxLayout()
        horizontal_layout_1 = QHBoxLayout()
        horizontal_layout_2 = QHBoxLayout()
        # WIDGETS
        self.group_box = QGroupBox("Track", self)
        self.progress_bar = QProgressBar()
        self.upload_button = QToolButton()
        self.shuffle_button = QToolButton()
        self.play_button = QToolButton()
        self.previous_button = QToolButton()
        self.next_button = QToolButton()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.mute_button = QToolButton()
        self.music_play_list = QListWidget()
        self.timer = QTimer()
        self.timer2 = QTimer()
        # self.progress_bar_label = QLabel("00:00/00:00")
        # WIDGETS CONFIGURATIONS
        self.group_box.setLayout(vertical_layout)
        self.upload_button.setIcon(QIcon("icons/add.png"))
        self.upload_button.setIconSize(QSize(30, 30))
        self.upload_button.setToolTip("Upload Track")
        self.shuffle_button.setIcon(QIcon("icons/shuffle.png"))
        self.shuffle_button.setIconSize(QSize(40, 40))
        self.shuffle_button.setToolTip("Shuffle Track")
        self.play_button.setIcon(QIcon("icons/play.png"))
        self.play_button.setIconSize(QSize(50, 50))
        self.play_button.setToolTip("Pause/Unpause Track")
        self.previous_button.setIcon(QIcon("icons/previous.png"))
        self.previous_button.setIconSize(QSize(40, 40))
        self.previous_button.setToolTip("Previous Track")
        self.next_button.setIcon(QIcon("icons/next.png"))
        self.next_button.setIconSize(QSize(30, 30))
        self.next_button.setToolTip("Next Track")
        self.mute_button.setIcon(QIcon("icons/unmuted.png"))
        self.mute_button.setIconSize(QSize(20, 20))
        self.mute_button.setToolTip("Mute Track")
        self.upload_button.clicked.connect(self.upload_track)
        self.music_play_list.itemDoubleClicked.connect(self.item_double_clicked)
        self.play_button.clicked.connect(self.track_action)
        self.group_box.setStyleSheet(styles.group_box_style())
        self.music_play_list.setStyleSheet(styles.play_list_style())
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.setValue(60)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.mute_button.clicked.connect(self.mute_track)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_progress_bar)
        self.timer2.timeout.connect(self.play_next_track)
        self.previous_button.clicked.connect(self.play_previous_track)
        self.next_button.clicked.connect(self.play_next_track)
        self.shuffle_button.clicked.connect(self.toggle_random)
        self.progress_bar.setStyleSheet(styles.progress_bar_style())
        # LAYOUT CONFIGURATIONS
        main_vertical_layout.addWidget(self.group_box, 25)
        main_vertical_layout.addWidget(self.music_play_list, 75)
        vertical_layout.addLayout(horizontal_layout_1)
        vertical_layout.addLayout(horizontal_layout_2)
        horizontal_layout_1.addWidget(self.progress_bar)
        # horizontal_layout_1.addWidget(self.progress_bar_label)
        horizontal_layout_2.addWidget(self.upload_button)
        horizontal_layout_2.addWidget(self.shuffle_button)
        horizontal_layout_2.addWidget(self.play_button)
        horizontal_layout_2.addWidget(self.previous_button)
        horizontal_layout_2.addWidget(self.next_button)
        horizontal_layout_2.addWidget(self.volume_slider)
        horizontal_layout_2.addWidget(self.mute_button)
        self.setLayout(main_vertical_layout)
        self.show()
        # OTHER INITIALIZATIONS
        self.clicked_track_title = None
        self.clicked_track_index = 0
        self.track_state = "paused"
        self.volume_state = "unmuted"
        self.last_volume = 60
        self.track_sequence = []
        self.track_titles = []
        self.show_play_list()
        self.progress_bar_counter = 0
        self.is_shuffled = False
        print(self.is_shuffled)
        mixer.init()
        mixer.music.set_volume(0.6)

    def upload_track(self):
        track = QFileDialog().getOpenFileName()
        track_name = os.path.basename(track[0][:-4])
        track_location = track[0]
        query = "INSERT INTO music (title, location) VALUES(?, ?)"
        cursor.execute(query, (track_name, track_location))
        connection.commit()
        self.show_play_list()

    def show_play_list(self):
        self.track_sequence = []
        self.track_titles = []
        self.music_play_list.clear()
        cursor.execute("SELECT * FROM music")
        for music in cursor.fetchall():
            self.track_sequence.append(music[2])
            self.track_titles.append(music[1])
            self.music_play_list.addItem(music[1])

    def item_double_clicked(self, item):
        self.clicked_track_title = "Playing [{}]".format(item.text())
        self.clicked_track_index = self.music_play_list.currentRow()
        self.play_track()

    def play_track(self):
        if self.track_sequence and self.clicked_track_index is not None:
            self.progress_bar_counter = 0
            self.progress_bar.setValue(0)
            self.track_state = "play"
            self.play_button.setIcon(QIcon("icons/pause.png"))
            self.group_box.setTitle(self.clicked_track_title)
            self.music_length = round(MP3(self.track_sequence[self.clicked_track_index]).info.length)
            self.progress_bar.setMaximum(self.music_length)
            self.timer2.setInterval(self.music_length * 1000)
            mixer.music.load(self.track_sequence[self.clicked_track_index])
            mixer.music.play(loops = 0, start = 0)
            self.timer.start()
            self.timer2.start()

    def track_action(self):
        if self.track_state == "paused":
            mixer.music.unpause()
            self.timer.start()
            self.timer2.start()
            self.play_button.setIcon(QIcon("icons/pause.png"))
            self.track_state = "play"
        else:
            mixer.music.pause()
            self.timer.stop()
            self.timer2.stop()
            self.play_button.setIcon(QIcon("icons/play.png"))
            self.track_state = "paused"

    def change_volume(self):
        volume = self.volume_slider.value()
        if volume == 0:
            self.mute_button.setIcon(QIcon("icons/mute.png"))
            self.volume_state = "muted"
        else:
            self.mute_button.setIcon(QIcon("icons/unmuted.png"))
            self.volume_state = "unmuted"
            self.last_volume = self.volume_slider.value()
        mixer.music.set_volume(volume/100)

    def mute_track(self):
        if self.volume_state == "unmuted":
            self.last_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
            mixer.music.set_volume(0)
            self.mute_button.setIcon(QIcon("icons/mute.png"))
            self.volume_state = "muted"
        else:
            self.volume_slider.setValue(self.last_volume)
            mixer.music.set_volume(self.last_volume/100)
            self.mute_button.setIcon(QIcon("icons/unmuted.png"))
            self.volume_state = "unmuted"

    def update_progress_bar(self):
        self.progress_bar_counter += 1
        self.progress_bar.setValue(self.progress_bar_counter)
        if self.progress_bar.value() == self.music_length:
            self.timer.stop()

    def play_previous_track(self):
        current_index = self.clicked_track_index - 1
        if current_index < 0:
            current_index = len(self.track_sequence) - 1
        self.music_play_list.setCurrentRow(current_index)
        self.clicked_track_title = "Playing [{}]".format(self.track_titles[current_index])
        self.clicked_track_index = current_index
        self.play_track()

    def play_next_track(self):
        if not self.is_shuffled:
            current_index = self.clicked_track_index + 1
            if current_index  == len(self.track_sequence):
                current_index = 0
            self.music_play_list.setCurrentRow(current_index)
            self.clicked_track_title = "Playing [{}]".format(self.track_titles[current_index])
            self.clicked_track_index = current_index
            self.play_track()
        else:
            self.play_random_track()

    def play_random_track(self):
        current_index = random.randint(0, len(self.track_sequence) - 1)
        self.music_play_list.setCurrentRow(current_index)
        self.clicked_track_title = "Playing [{}]".format(self.track_titles[current_index])
        self.clicked_track_index = current_index
        self.play_track()
    
    def toggle_random(self):
        if not self.is_shuffled:
            self.is_shuffled = True
        else:
            self.is_shuffled = False
        print(self.is_shuffled)


def main():
    application = QApplication(sys.argv)
    music_player = MusicPlayer()
    sys.exit(application.exec_())


if __name__ == "__main__":
    main()
