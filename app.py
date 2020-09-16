# coding=utf-8

from kivy.app import App
from kivy.lang import Builder

import WindowManager


class Kivy_pyzbar(App):
    def build(self):
        return Builder.load_file("WindowManager.kv")
