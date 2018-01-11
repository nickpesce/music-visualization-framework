class Decorators:

    def __init__(self, music_app):
        self.music_app = music_app

    def on_beat(self, beat_type):
        def decorator(func):
            self.music_app.beat_listeners[beat_type].append(func)
        return decorator

    def on_level_change(self):
        def decorator(func):
            self.music_app.level_change_listeners.append(func)
        return decorator

    def on_threshold_change(self):
        def decorator(func):
            self.music_app.threshold_change_listeners.append(func)
        return decorator
