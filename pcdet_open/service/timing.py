import logging
from time import time


class Timing:
    def __init__(self, message=None, title_length=25) -> None:
        self.message = message
        self.title_length = title_length
        self.start = self.last = time()

    @property
    def interval(self):
        now = time()
        self.last, tp = now, now - self.last
        return tp

    def str_interval(self, title):
        format = f"{{:{self.title_length}}} {{:.2g}}s"
        return format.format(title + ": ", self.interval)

    def log_interval(self, title):
        logging.info(self.str_interval(title))

    @property
    def total_interval(self):
        now = time()
        self.last, tp = now, now - self.start
        return tp

    def __enter__(self):
        pass

    def __exit__(self, type, value, trace):
        logging.info(f"{self.message + ' ' if self.message else ''}{time() - self.start:.2g}s")
