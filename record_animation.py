import numpy as np
import time
import sys
import screeninfo
import pygame
import re
import os
from config import *


def get_screen_width_and_height():
    monitor_info = screeninfo.get_monitors()[0]
    if not monitor_info:
        sys.exit("couldn't find monitor")
    m = re.match("monitor\((\d+)x(\d+)\+\d+\+\d+\)", str(monitor_info))

    screen_width, screen_height = int(m.group(1)), int(m.group(2))
    return screen_width, screen_height


screen_width, screen_height = get_screen_width_and_height()
arrow = pygame.image.load(os.path.join("images", "arrow.png"))
arrow_right = pygame.transform.rotate(arrow, 270)
arrow_left = pygame.transform.rotate(arrow, 90)
arrow_up = pygame.transform.rotate(arrow, 0)
arrow_down = pygame.transform.rotate(arrow, 180)

arrow_height, arrow_width = arrow.get_size()
black = (0, 0, 0)

mid_pos = (screen_width // 2, screen_height // 2)
up_pos = (screen_width // 2, 0)
down_pos = (screen_width // 2, screen_height - arrow_height)
left_pos = (0, (screen_height - arrow_height) // 2)
right_pos = (screen_width - arrow_width, (screen_height - arrow_height) // 2)


class RecordApp:
    def __init__(self, recorder, labels):
        self._recorder = recorder
        self._labels = labels
        pygame.init()
        screen_width, screen_height = get_screen_width_and_height()
        screen = pygame.display.set_mode(
            (screen_width, screen_height), pygame.FULLSCREEN
        )
        screen.fill(black)
        pygame.display.update()
        self.screen = screen

    def run(self):
        for label in self._labels:
            self.run_trial(label)
        time.sleep(2)
        pygame.quit()
        sys.exit()

    def run_trial(self, label):
        self.screen.fill(black)
        if label == EyeMovement.UP:
            self.screen.blit(arrow_up, up_pos)
        elif label == EyeMovement.DOWN:
            self.screen.blit(arrow_down, down_pos)
        elif label == EyeMovement.RIGHT:
            self.screen.blit(arrow_right, right_pos)
        elif label == EyeMovement.LEFT:
            self.screen.blit(arrow_left, left_pos)
        elif label == EyeMovement.MID:
            pass
        else:
            raise "invalid label: {}".format(label)
        pygame.display.update()
        self._recorder.record_label(label)
        time.sleep(1.1)


def main():
    app = RecordApp()
    app.run()


if __name__ == "__main__":
    labels = ["mid", "up", "down", "left", "right"]
    app = RecordApp(None, labels)
    app.run_session()
