import time

class TickCounter():
    def __init__(self):
        self._start_time = time.perf_counter()

    def get_current_ms(self):
        return time.perf_counter() * 500