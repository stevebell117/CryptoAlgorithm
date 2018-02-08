import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import sys

kv_text = '''
<MyScreenManager>:
    HomeScreen:

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint: 1,.1
            orientation: "horizontal"
            Button:
                text:"1"
            Button:
                text:"2"
            Button:
                text:"3"
        ScrollView:
            GridLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height  #<<<<<<<<<<<<<<<<<<<<
                row_default_height: 60
                cols:1
                TextInput:
                    text:"1"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"2"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"3"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"4"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"5"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"6"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"7"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"8"
                    size_hint: .1, None
                    readonly: True
                TextInput:
                    text:"9"
                    size_hint: .1, None
                    readonly: True
                
    BoxLayout:
        size_hint: 1,.1
        orientation: "horizontal"
        TextInput:
            text:"3"
            readonly: True
    
        '''

class MyScreenManager(ScreenManager):
    pass

class HomeScreen(Screen):
    pass

class AppWindow(App):
    order_book = None
    gdax = None
    algorithm = None

    def update_class_values(self, **kwargs):
        if 'order_book' in kwargs:
            self.order_book = kwargs['order_book']
        if 'gdax' in kwargs:
            self.gdax = kwargs['gdax']
            self.algorithm = self.gdax.algorithm

    # layout
    def build(self):
        return HomeScreen()

    def on_stop(self):
        sys.exit()

class MainWindow():
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self):
        Builder.load_string(kv_text)
        app = AppWindow()
        app.update_class_values(**self.kwargs)
        app.run()
