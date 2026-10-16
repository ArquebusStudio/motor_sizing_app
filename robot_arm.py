from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.window import Window
#from kivy.uix.togglebutton import ToggleButton
import math

#   oooooooooooo    ooooo     ooo    ooooo      ooo
#   `888'     `8    `888'     `8'    `888b.     `8'
#    888             888       8      8 `88b.    8
#    888oooo8        888       8      8   `88b.  8
#    888    "        888       8      8     `88b.8
#    888             `88.    .8'      8       `888
#   o888o              `YbodP'       o8o        `8


def float_input(*args):
    result = []
    for val in args:
        try: result.append(float(val))
        except (ValueError, TypeError): result.append(None)
    return tuple(result)



def load_inertia(j_arm, mass_arm, r_arm, j_counter, mass_counter, r_counter, reduct_ratio, j_reduct):
    j_arm, mass_arm, r_arm, j_counter, mass_counter, r_counter, reduct_ratio, j_reduct = float_input(j_arm, mass_arm, r_arm, j_counter, mass_counter, r_counter, reduct_ratio, j_reduct)
    if None in (j_arm, mass_arm, r_arm, j_counter, mass_counter, r_counter, reduct_ratio, j_reduct): return ""
    if any(x <= 0 for x in (j_arm, mass_arm, reduct_ratio)): return ""
    if any(x < 0 for x in ( r_arm, j_counter, mass_counter, r_counter ,j_reduct)): return ""

    j_arm_total = (j_arm + mass_arm * r_arm ** 2) + (j_counter + mass_counter * r_counter ** 2)  # 10^-6 kg·m²
    j_load = j_arm_total / reduct_ratio ** 2 + j_reduct          # 10^-6 kg·m²

    return "{:.4g}".format(float(j_load))


def required_rpm(ang_v_max, reduct_ratio):
    ang_v_max, reduct_ratio = float_input(ang_v_max, reduct_ratio)
    if None in (ang_v_max, reduct_ratio): return ""
    if any(x <= 0 for x in (ang_v_max, reduct_ratio)): return ""
    req_rpm = ang_v_max/360 *60 * reduct_ratio     # v_max: deg/s
    return "{:.4g}".format(float(req_rpm))


def acceleration_torque(req_rpm, acc_time, j_load, j_motor):
    req_rpm, acc_time, j_load, j_motor = float_input(req_rpm, acc_time, j_load, j_motor)
    if None in (req_rpm, acc_time, j_load, j_motor): return ""
    if any(x <= 0 for x in (req_rpm, acc_time, j_load)): return ""
    if j_motor < 0 : return ""
    ang_acc = ( 2*math.pi * req_rpm / 60 ) / acc_time    # rad²/s
    j_total = j_load + j_motor      # 10^-6 kg·m²
    j_total_m = j_total *1e-6        # kg·m²
    acc_tq = j_total_m * ang_acc      # N·m
    return "{:.4g}".format(float(acc_tq))


def load_toruqe(incl_ang, mass_arm, r_arm, mass_counter, r_counter, tq_resist, rotary_eff, reduct_ratio):
    incl_ang, mass_arm, r_arm, mass_counter, r_counter, tq_resist, rotary_eff, reduct_ratio = float_input(incl_ang, mass_arm, r_arm, mass_counter, r_counter, tq_resist, rotary_eff, reduct_ratio)
    if None in (incl_ang, mass_arm, r_arm, mass_counter, r_counter, tq_resist, rotary_eff, reduct_ratio): return ""
    if any(x <= 0 for x in (mass_arm, reduct_ratio)): return ""
    if any(x < 0 for x in (tq_resist, mass_counter, r_counter, r_arm)): return ""
    if incl_ang > 90 or incl_ang < 0: return ""
    if rotary_eff > 1 or rotary_eff <=0: return ""
    alpha = math.radians(incl_ang)        #rad
    r_arm_m = r_arm / 1000            #m
    r_counter_m = r_counter / 1000     #m
    weight_tq = abs(mass_arm * 9.8 * math.sin(alpha) * r_arm_m - mass_counter * 9.8 * math.sin(alpha) * r_counter_m)   #N*m
    load_tq = (tq_resist + weight_tq) / rotary_eff / reduct_ratio

    return "{:.4g}".format(float(load_tq))



def required_torque(acc_tq, load_tq, n_sf):
    acc_tq, load_tq, n_sf = float_input(acc_tq, load_tq, n_sf)
    if None in (acc_tq, load_tq, n_sf): return ""
    if any(x <= 0 for x in (acc_tq, n_sf)): return ""
    if load_tq < 0: return ""
    if n_sf <1: return ""
    req_tq = (acc_tq + load_tq) * n_sf    # N*m
    return "{:.4g}".format(float(req_tq))


def required_angular_resolution (ang_res, reduct_ratio):
    ang_res, reduct_ratio = float_input(ang_res, reduct_ratio)
    if None in (ang_res, reduct_ratio): return ""
    if any(x <= 0 for x in (ang_res, reduct_ratio)): return ""
    req_ang_res = ang_res * reduct_ratio # deg/step
    return "{:.4g}".format(float(req_ang_res))



#   ooooo     ooo    ooooo                   oooooo   oooooo     oooo    ooooo    ooooo      ooo    oooooooooo.        .oooooo.      oooooo   oooooo     oooo
#   `888'     `8'    `888'                    `888.    `888.     .8'     `888'    `888b.     `8'    `888'   `Y8b      d8P'  `Y8b      `888.    `888.     .8'
#    888       8      888                      `888.   .8888.   .8'       888      8 `88b.    8      888      888    888      888      `888.   .8888.   .8'
#    888       8      888                       `888  .8'`888. .8'        888      8   `88b.  8      888      888    888      888       `888  .8'`888. .8'
#    888       8      888                        `888.8'  `888.8'         888      8     `88b.8      888      888    888      888        `888.8'  `888.8'
#    `88.    .8'      888                         `888'    `888'          888      8       `888      888     d88'    `88b    d88'         `888'    `888'
#      `YbodP'       o888o    ooooooooooo          `8'      `8'          o888o    o8o        `8     o888bood8P'       `Y8bood8P'           `8'      `8'

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





#   ooooo     ooo    ooooo                   oooooooooooo    ooooo           oooooooooooo    ooo        ooooo    oooooooooooo    ooooo      ooo    ooooooooooooo
#   `888'     `8'    `888'                   `888'     `8    `888'           `888'     `8    `88.       .888'    `888'     `8    `888b.     `8'    8'   888   `8
#    888       8      888                     888             888             888             888b     d'888      888             8 `88b.    8          888
#    888       8      888                     888oooo8        888             888oooo8        8 Y88. .P  888      888oooo8        8   `88b.  8          888
#    888       8      888                     888    "        888             888    "        8  `888'   888      888    "        8     `88b.8          888
#    `88.    .8'      888                     888       o     888       o     888       o     8    Y     888      888       o     8       `888          888
#      `YbodP'       o888o    ooooooooooo    o888ooooood8    o888ooooood8    o888ooooood8    o8o        o888o    o888ooooood8    o8o        `8         o888o

class LabelInput(BoxLayout):
    def __init__(self, label_text, hint_text, readonly, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.label = Label(
            text=label_text,
            color=(0, 0, 0, 1), font_size=FONT_SIZE, size_hint_x=None, width=LABEL_WIDTH,
            size_hint_y=None, height=ROW_HEIGHT, halign='left', valign='middle', text_size=(LABEL_WIDTH, None)
        )
        self.textinput = TextInput(
            hint_text=hint_text, readonly=readonly,
            font_size=LINEDIT_FONT_SIZE, background_color=(0.8, 0.9, 1, 1) if readonly else (1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1), size_hint_x=None, width=LINE_EDIT_WIDTH, size_hint_y=None, height=ROW_HEIGHT,
            input_type = 'number'   # Number keyboard in Android
        )
        self.check = Label(
            text="",
            color=(1, 0, 0, 1), font_size=FONT_SIZE*0.8, size_hint_x=None, width=CHECK_WIDTH,
            size_hint_y=None, height=ROW_HEIGHT, halign='left', valign='middle', text_size=(CHECK_WIDTH, None)
        )
        self.add_widget(self.label)
        self.add_widget(self.textinput)
        self.add_widget(self.check)

        self.textinput.multiline = False #prevent "\n"

    @property
    def value(self):
        return self.textinput.text

    @value.setter
    def value(self, new_val):
        self.textinput.text = new_val

    @property
    def readonly(self):
        return self.textinput.readonly

    @readonly.setter
    def readonly(self, flag):
        self.textinput.readonly = flag
        self.textinput.background_color = (0.8, 0.9, 1, 1) if flag else (1, 1, 1, 1)

    @property
    def color(self):
        return self.textinput.foreground_color

    @color.setter
    def color(self, rgba):
        self.textinput.foreground_color = rgba

    @property
    def background(self):
        return self.textinput.background_color

    @background.setter
    def background(self, rgba):
        self.textinput.background_color = rgba

    @property
    def check_val(self):
        return self.check.text

    @check_val.setter
    def check_val(self, new_check):
        self.check.text = new_check



#   ooooo     ooo    ooooo                   ooooo                 .o.          oooooo   oooo      .oooooo.      ooooo     ooo    ooooooooooooo
#   `888'     `8'    `888'                   `888'                .888.          `888.   .8'      d8P'  `Y8b     `888'     `8'    8'   888   `8
#    888       8      888                     888                .8"888.          `888. .8'      888      888     888       8          888
#    888       8      888                     888               .8' `888.          `888.8'       888      888     888       8          888
#    888       8      888                     888              .88ooo8888.          `888'        888      888     888       8          888
#    `88.    .8'      888                     888       o     .8'     `888.          888         `88b    d88'     `88.    .8'          888
#      `YbodP'       o888o    ooooooooooo    o888ooooood8    o88o     o8888o        o888o         `Y8bood8P'        `YbodP'           o888o

class Table(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=1, spacing=ROW_HEIGHT + screen_height * 0.02, padding=[screen_width * 0.05, 50, screen_width * 0.05, 50], **kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))


        #Motion
        self.add_widget(
            Label(text="[i][u][b]MOTION[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None,
                  width=LABEL_WIDTH,
                  size_hint_y=None, font_size=FONT_SIZE * 1.2, text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT,
                  halign='left', valign='middle'))

        self.add_dataitem("incl_ang", "Inclination Angle (deg)", "Horizontal 0, vertical 90", False)
        self.add_dataitem("tq_resist", "Resistance Torque (N*m)", "Due to friction and external force", False)
        self.add_dataitem("ang_v_max", "Max Angular Speed (deg/s)", "", False)
        self.add_dataitem("acc_time", "Acceleration Time (s)", "Time to reach max speed", False)




        # Robot Arm
        self.add_widget(
            Label(text="[i][u][b]ROBOT ARM[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None,
                  width=LABEL_WIDTH,
                  size_hint_y=None, font_size=FONT_SIZE * 1.2, text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT,
                  halign='left', valign='middle'))

        self.add_dataitem("rotary_eff", "Rotary System Efficiency", "", False)
        self.add_dataitem("j_arm", "Arm Inertia\n(10^-6 kg*m^2)", "Around CG", False)
        self.add_dataitem("mass_arm", "Arm Mass (kg)", "", False)
        self.add_dataitem("r_arm", "Arm Center Offset (mm)", "", False)
        self.add_dataitem("j_counter", "Counter Mass Inertia\n(10^-6 kg*m^2)", "Around CG; put 0 if NA", False)
        self.add_dataitem("mass_counter", "Counter Mass (kg)", "Put 0 if NA", False)
        self.add_dataitem("r_counter", "Counter Mass Center Offset (mm)", "Put 0 if NA", False)



        # Transmission
        self.add_widget(Label(text="[i][u][b]TRANSMISSION[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                              size_hint_y=None, font_size=FONT_SIZE*1.2,text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT, halign='left', valign='middle'))

        self.add_dataitem("reduct_ratio", "Reduction Ratio", "Put 1 for direct coupling", False)
        self.add_dataitem("j_reduct", "Reduction Inertia\n(10^-6 kg*m^2)", "Put 0 for direct coupling", False)
        self.add_dataitem("ang_res", "Angular Resolution (deg/step)", "", False)
        self.add_dataitem("j_motor", "Motor Rotor Inertia\n(10^-6 kg*m^2)", "Input an initial guess", False)
        self.add_dataitem("n_sf", "Safety Factor", "", False)

        self.add_widget(Label(
            text="Reduction Drive Inertia:\n"
                 "The total inertia of all gears, pulleys, or reduction mechanisms, calculated from[/i] [i][b]the motor side[/b][/i]\n"
                 "[u]sum(J motor side) + sum(J shaft side) / (speed ratio)^2[/u]\n"
                 "Set as 0 for direct coupling[/i]",
            markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=TOGGLE_WIDTH, size_hint_y=None,
            font_size=FONT_SIZE * 0.8, text_size=(TOGGLE_WIDTH, None), height=ROW_HEIGHT,
            halign='left', valign='middle'
        ))

        self.add_widget(Label(text="",size_hint_x=None,width=TOGGLE_WIDTH,size_hint_y=None, height=ROW_HEIGHT))



        # Warning Text
        self.warning = Label(text="", markup=True, color=(1, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                  size_hint_y=None, font_size=FONT_SIZE, text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT,
                  halign='left', valign='middle')
        self.add_widget(self.warning)


        # Required Motor Specs
        self.add_widget(Label(text="[i][u][b]REQUIRED MOTOR SPECS[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                              size_hint_y=None, font_size=FONT_SIZE*1.2,text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT, halign='left', valign='middle'))

        self.add_dataitem("j_motor_display", "Motor Rotor Inertia\n(10^-6 kg*m^2)", "", True)
        self.add_dataitem("j_load", "Load Inertia\n(10^-6 kg*m^2)", "", True)
        self.add_dataitem("n_sf_display", "Safety Factor", "", True)
        self.add_dataitem("req_rpm", "Required Motor RPM", "", True)
        self.add_dataitem("req_tq", "Required Torque (N*m)", "", True)
        self.add_dataitem("acc_tq", "Acceleration Torque (N*m)", "", True)
        self.add_dataitem("load_tq", "Load Torque (N*m)", "", True)
        self.add_dataitem("req_ang_res", "Required Resolution (deg/step)", "", True)



    def add_dataitem(self, var_name, label_text, hint_text, readonly):
        widget = LabelInput(label_text, hint_text, readonly=readonly)
        setattr(self, var_name, widget)
        self.add_widget(widget)

    def check_data(self, data_item, lower, upper, lower_equal, upper_equal):
        data, = float_input(data_item.value)
        if data is None: data_item.check_val = "X"
        elif (data > lower or (lower_equal and data == lower)) and \
                (data < upper or (upper_equal and data == upper)):
            data_item.check_val = ""
        else:
            data_item.check_val = "X"

    def calculate_update(self, instance):

        input_text = (
            self.incl_ang.value,self.tq_resist.value, self.ang_v_max.value, self.acc_time.value,
            self.rotary_eff.value, self.j_arm.value, self.mass_arm.value, self.r_arm.value, self.j_counter.value, self.mass_counter.value, self.r_counter.value,
            self.reduct_ratio.value, self.j_reduct.value, self.ang_res.value, self.j_motor.value, self.n_sf.value)

        print(input_text)

        self.check_data(self.incl_ang, 0, 90, True, True)  # 0<=incl_ang<=90
        self.check_data(self.tq_resist, 0, math.inf, True,False)            # 0<=  <inf
        self.check_data(self.ang_v_max, 0, math.inf, False, False)         # 0<  <inf
        self.check_data(self.acc_time, 0, math.inf, False, False)     # 0<acc_time<inf

        self.check_data(self.rotary_eff, 0, 1, False, True)  # 0<  <=1
        self.check_data(self.j_arm, 0, math.inf, False, False)        # 0<   <inf
        self.check_data(self.mass_arm, 0, math.inf, False, False)       # 0<   <inf
        self.check_data(self.r_arm, 0, math.inf, True, False)        # 0<=   <inf
        self.check_data(self.j_counter, 0, math.inf, True, False)        # 0<=   <inf
        self.check_data(self.mass_counter, 0, math.inf, True, False)       # 0<=   <inf
        self.check_data(self.r_counter, 0, math.inf, True, False)        # 0<=   <inf


        self.check_data(self.reduct_ratio, 0, math.inf, False, False)  # 0<reduct_ratio<inf
        self.check_data(self.j_reduct, 0, math.inf, True, False)  # 0<j_reduct<inf
        self.check_data(self.ang_res, 0, math.inf, False, False)  # 0< <inf
        self.check_data( self.j_motor, 0, math.inf, True, False)  # 0<=j_motor<inf   # j_motor =0 to help initial guessing
        self.check_data(self.n_sf, 1, math.inf, True, False)  # 1<=n_sf<inf

        all_checks = [
            self.incl_ang.check_val,
            self.tq_resist.check_val,
            self.ang_v_max.check_val,
            self.acc_time.check_val,
            self.rotary_eff.check_val,
            self.j_arm.check_val,
            self.mass_arm.check_val,
            self.r_arm.check_val,
            self.j_counter.check_val,
            self.mass_counter.check_val,
            self.r_counter.check_val,
            self.reduct_ratio.check_val,
            self.j_reduct.check_val,
            self.ang_res.check_val,
            self.j_motor.check_val,
            self.n_sf.check_val,
        ]


        if "X" in all_checks:
            self.warning.text = "[i][b]INVALID INPUT[/b][/i]"
            return
        else:
            self.warning.text = ""

        self.j_load.value = load_inertia(self.j_arm.value, self.mass_arm.value, self.r_arm.value, self.j_counter.value, self.mass_counter.value, self.r_counter.value, self.reduct_ratio.value, self.j_reduct.value)

        self.req_rpm.value = required_rpm(self.ang_v_max.value, self.reduct_ratio.value)

        self.acc_tq.value = acceleration_torque(self.req_rpm.value, self.acc_time.value, self.j_load.value, self.j_motor.value)

        self.load_tq.value = load_toruqe(self.incl_ang.value, self.mass_arm.value, self.r_arm.value, self.mass_counter.value, self.r_counter.value, self.tq_resist.value, self.rotary_eff.value, self.reduct_ratio.value)

        self.req_tq.value = required_torque(self.acc_tq.value, self.load_tq.value, self.n_sf.value)

        self.req_ang_res.value = required_angular_resolution(self.ang_res.value, self.reduct_ratio.value)

        self.j_motor_display.value = self.j_motor.value

        self.n_sf_display.value = self.n_sf.value


        return

    def reset_input(self, instance):

        all_data = [
            self.incl_ang,
            self.tq_resist,
            self.ang_v_max,
            self.acc_time,
            self.rotary_eff,
            self.j_arm,
            self.mass_arm,
            self.r_arm,
            self.j_counter,
            self.mass_counter,
            self.r_counter,
            self.reduct_ratio,
            self.j_reduct,
            self.ang_res,
            self.j_motor,
            self.n_sf,

            self.j_load,
            self.req_rpm,
            self.acc_tq,
            self.load_tq,
            self.req_tq,
            self.req_ang_res,
            self.j_motor_display,
            self.n_sf_display
        ]



        for x in all_data:
            x.value=""
            x.check_val=""

        self.warning.text = ""

        return



def get_screen_layout():
    root_layout = BoxLayout(orientation='vertical')
    scroll_view = ScrollView(size_hint=(1, 1))
    table = Table()
    scroll_view.add_widget(table)

    button_layout1 = BoxLayout(size_hint_y=None, height=ROW_HEIGHT*1.3, padding=[10, 10])
    back_button = Button(text="Back", size_hint_x=None, width=screen_width*0.3 ,font_size=FONT_SIZE, height=ROW_HEIGHT)

    def go_back(instance):
        App.get_running_app().root.current = "menu"

    back_button.bind(on_press=go_back)
    button_layout1.add_widget(back_button)

    button_layout2 = BoxLayout(size_hint_y=None, height=ROW_HEIGHT * 2, padding=[10, 10])
    reset_button = Button(text="Reset", size_hint_x=1, font_size=FONT_SIZE, height=ROW_HEIGHT)
    reset_button.bind(on_press=table.reset_input)
    calculate_button = Button(text="Calculate/Update", size_hint_x=1, font_size=FONT_SIZE, height=ROW_HEIGHT)
    calculate_button.bind(on_press=table.calculate_update)
    button_layout2.add_widget(reset_button)
    button_layout2.add_widget(calculate_button)

    root_layout.add_widget(button_layout1)
    root_layout.add_widget(scroll_view)
    root_layout.add_widget(button_layout2)
    return root_layout





#         .o.          ooooooooo.      ooooooooo.
#        .888.         `888   `Y88.    `888   `Y88.
#       .8"888.         888   .d88'     888   .d88'
#      .8' `888.        888ooo88P'      888ooo88P'
#     .88ooo8888.       888             888
#    .8'     `888.      888             888
#   o88o     o8888o    o888o           o888o

class TableApp(App):
    def build(self):
        root_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView(size_hint=(1, 1))
        table = Table()
        scroll_view.add_widget(table)

        button_layout = BoxLayout(size_hint_y=None, height=ROW_HEIGHT*2, padding=[10, 10])
        reset_button = Button(text="Reset", size_hint_x=1,font_size=FONT_SIZE, height=ROW_HEIGHT)
        reset_button.bind(on_press=table.reset_input)
        calculate_button = Button(text="Calculate/Update", size_hint_x=1,font_size=FONT_SIZE, height=ROW_HEIGHT)
        calculate_button.bind(on_press=table.calculate_update)
        button_layout.add_widget(reset_button)
        button_layout.add_widget(calculate_button)

        root_layout.add_widget(scroll_view)
        root_layout.add_widget(button_layout)

        return root_layout



if __name__ == "__main__":
    TableApp().run()



