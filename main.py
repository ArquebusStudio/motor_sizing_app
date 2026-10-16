from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
import webbrowser


# Import screen layouts from modules
from ball_screw import get_screen_layout as get_ball_screw
from belt_drive import get_screen_layout as get_belt_drive
from index_table import get_screen_layout as get_index_table
from robot_arm import get_screen_layout as get_robot_arm


MODULES = {
    "Ball Screw": get_ball_screw,
    "Belt Drive": get_belt_drive,
    "Index Table": get_index_table,
    "Robot Arm": get_robot_arm
}


# Set window background color
Window.clearcolor = (0.9, 0.9, 0.9, 1)

# Screen and style scaling
screen_width = Window.width
screen_height = Window.height
FONT_SIZE = min(screen_width * 0.04, screen_height * 0.03)
LINEDIT_FONT_SIZE = min(screen_width * 0.03, screen_height * 0.025)
ROW_HEIGHT = screen_height * 0.06
LABEL_WIDTH = screen_width * 0.4
LINE_EDIT_WIDTH = screen_width * 0.5
CHECK_WIDTH = screen_width * 0.05
TOGGLE_WIDTH = screen_width * 0.9




class ModuleScreen(Screen):
    def __init__(self, layout_func, **kwargs):
        super().__init__(**kwargs)
        layout = layout_func()
        self.add_widget(layout)

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.img = Image(source='motor_sizing.png',
                         allow_stretch=True, keep_ratio=True,
                         size_hint=(1, 0.5))
        layout.add_widget(self.img)

        for name in MODULES:
            btn = Button(text=name, font_size=FONT_SIZE*1.5, size_hint_y=0.2)
            btn.bind(on_press=lambda btn, name=name: self.switch_to(name))
            layout.add_widget(btn)


        self.contact_btn = Button(
            text="Contact: arquebus.studio@gmail.com",
            size_hint=(1, None),
            height = FONT_SIZE *1.6,
            background_color=(0, 0, 0, 1),
            color=(1, 1, 1, 1),
            font_size=FONT_SIZE * 0.8
        )

        # Bind it to your action
        self.contact_btn.bind(on_release=self.open_contact_email)

        # Add to layout
        layout.add_widget(self.contact_btn)

        self.add_widget(layout)

    def switch_to(self, screen_name):
        app = App.get_running_app()
        app.root.current = screen_name

    def open_contact_email(self, instance):
        # This opens the user's email app to contact you
        webbrowser.open("mailto:arquebus.studio@gmail.com")

class MotionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        for name, layout_func in MODULES.items():
            sm.add_widget(ModuleScreen(name=name, layout_func=layout_func))
        return sm

if __name__ == "__main__":
    MotionApp().run()
