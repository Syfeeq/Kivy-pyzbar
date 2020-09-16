from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from pyzbar import pyzbar
from threading import Thread
from picamera import PiCamera
from picamera.array import PiRGBArray

Builder.load_file("MainScreen.kv")


class MainScreen(Screen):
    decoded_text = StringProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        self.camera = PiCamera()
        # https://picamera.readthedocs.io/en/release-1.12/fov.html#camera-modes
        self.camera.resolution = (1640, 1232)
        self.stream = PiRGBArray(self.camera, size=self.camera.resolution)
        self.decoded_text = "Code type:\n\nDecoded data:\n"

    def on_enter(self):
        self.read = True
        self.camera_thread = Thread(target=self.camera_preview)
        self.code_thread = Thread(target=self.code_parser)
        self.camera_thread.start()
        self.code_thread.start()

    def camera_preview(self):
        self.camera.start_preview(fullscreen=False, window=(0, 0, 640, 480))

    def code_parser(self):
        for frame in self.camera.capture_continuous(
            self.stream, format="bgr", use_video_port=True
        ):
            barcodes = pyzbar.decode(frame.array)
            for barcode in barcodes:
                self.decoded_text = "Code type: {}\n\nDecoded data: {}".format(
                    barcode.type, barcode.data.decode()
                )
            self.stream.truncate(0)
            if not self.read:
                break

    def quit_app(self):
        if self.code_thread.is_alive():
            self.read = False
            self.code_thread.join()
        self.camera.stop_preview()
        self.camera.close()
        self.code_thread.join()
        App.get_running_app().stop()
