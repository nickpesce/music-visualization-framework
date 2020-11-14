from collections import defaultdict
import threading

from . import music_input
from . import music_decorators


NUM_INPUT_BANDS= 14

class Analyzer:
    def __init__(self, port, stereo=False, smoothing=.6, threshold_acceleration=.02, beat_cooldown=3):
        self.stereo = stereo
        self.num_bands = 14 if self.stereo else 7
        self.smoothing = smoothing
        self.threshold_acceleration = threshold_acceleration
        self.beat_cooldown = beat_cooldown
        self.beat_listeners = defaultdict(list)
        self.level_change_listeners = []
        self.threshold_change_listeners = []
        self.bands = [0]*self.num_bands
        self.prev_bands = [0]*self.num_bands
        self.prev_thresholds = [0]*self.num_bands
        self.thresholds = [0]*self.num_bands
        self.beats = [False]*self.num_bands
        self.time_since_last_beat = [0]*self.num_bands

        self.total_volume = 0
        self.total_volume_threshold = 0
        self.total_beat_listeners = []
        self.total_volume_beat = False
        self.prev_total_volume_threshold = 0
        self.time_since_last_total_volume_beat = 0

        self.decorators = music_decorators.Decorators(self)
        self.input = music_input.Input(port)
        self.input.receive_input(self.process_raw_line)

    def start(self, threaded=True, stop_event=None):
        if threaded:
            threading.Thread(target=self.input.start_listening, args=(stop_event,)).start()
        else:
            self.input.start_listening(stop_event)
            
    def process_raw_line(self, line):
        if len(line) < NUM_INPUT_BANDS:
            return
        self.prev_bands = self.bands
        if not self.stereo:
            for i in range(0, self.num_bands):
                line[i] = (line[2*i] + line[2*i+1]) / 2
        for i in range(0, self.num_bands):
            self.bands[i] = self.smoothing * self.prev_bands[i] + (1 - self.smoothing) * line[i]
        self.total_volume = sum(self.bands)
        for l in self.level_change_listeners:
            l()
        self.on_update()

    def on_update(self):
        self.process_band_beats()
        self.process_total_beat()

    def process_total_beat(self):
        self.prev_total_volume_threshold = self.total_volume_threshold
        self.total_volume_beat = False
        if self.total_volume > self.prev_total_volume_threshold:
            if self.time_since_last_total_volume_beat > self.beat_cooldown:
                self.total_volume_beat = True
                self.time_since_last_total_volume_beat = 0
                for l in self.total_beat_listeners:
                    l()
            self.total_volume_threshold = self.total_volume

        else:
            self.total_volume_threshold = max(0, self.prev_total_volume_threshold - (self.threshold_acceleration * abs(self.prev_total_volume_threshold - self.total_volume - 20)))
            self.time_since_last_total_volume_beat += 1

    def process_band_beats(self):
        self.beats = [False]*self.num_bands
        self.prev_thresholds = self.thresholds
        for i in range(0, self.num_bands):
            if self.bands[i] > self.prev_thresholds[i]:
                if self.time_since_last_beat[i] > self.beat_cooldown:
                    self.beats[i] = True
                    self.time_since_last_beat[i] = 0
                    for l in self.beat_listeners[i]:
                        l()
                self.thresholds[i] = self.bands[i]
            else:
                self.thresholds[i] = max(0, self.prev_thresholds[i] - (self.threshold_acceleration * abs(self.prev_thresholds[i] - self.bands[i] - 20)))
                self.time_since_last_beat[i] += 1
        for l in self.threshold_change_listeners:
            l()
