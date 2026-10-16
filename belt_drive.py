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



def load_inertia(dp_1, dp_2, dp_idle, j_p1, j_p2, j_idle, qty_idle, mass, reduct_ratio, j_reduct):
    dp_1, dp_2, dp_idle, j_p1, j_p2, j_idle, qty_idle, mass, reduct_ratio, j_reduct = float_input(dp_1, dp_2, dp_idle, j_p1, j_p2, j_idle, qty_idle, mass, reduct_ratio, j_reduct)
    if None in (dp_1, dp_2, dp_idle, j_p1, j_p2, j_idle, qty_idle, mass, reduct_ratio, j_reduct): return ""
    if any(x <= 0 for x in (dp_1, dp_2, j_p1, j_p2, mass, reduct_ratio)): return ""
    if any(x < 0 for x in (dp_idle, j_idle, qty_idle, j_reduct)): return ""

    if dp_idle==0 or qty_idle==0 or j_idle==0:
        j_total_driving = j_p1 + j_p2/(dp_2/dp_1)**2 + mass*dp_1**2 /4  # 10^-6 kg·m²
    else:
        j_total_driving = j_p1 + j_p2 /(dp_2/dp_1)**2 + j_idle /(dp_idle/dp_1)**2 *qty_idle + mass*dp_1**2 /4   # 10^-6 kg·m²
    j_load = j_total_driving / reduct_ratio**2 + j_reduct    # 10^-6 kg·m²

    return "{:.4g}".format(float(j_load))


def required_rpm(v_max, dp_1, reduct_ratio):
    v_max, dp_1, reduct_ratio = float_input(v_max, dp_1, reduct_ratio)
    if None in (v_max, dp_1, reduct_ratio): return ""
    if any(x <= 0 for x in (v_max, dp_1, reduct_ratio)): return ""
    req_rpm = v_max / (math.pi * dp_1) * 60 * reduct_ratio      # v_max: mm/s  dp_1: mm
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


def load_toruqe(incl_ang, mass, frict_coef, f_ex, dp_1, belt_drive_eff, reduct_ratio):
    incl_ang, mass, frict_coef, f_ex, dp_1, belt_drive_eff, reduct_ratio = float_input(incl_ang, mass, frict_coef, f_ex, dp_1, belt_drive_eff, reduct_ratio)
    if None in (incl_ang, mass, frict_coef, f_ex, dp_1, belt_drive_eff, reduct_ratio): return ""
    if any(x <= 0 for x in (mass, frict_coef, dp_1, belt_drive_eff, reduct_ratio)): return ""
    if f_ex < 0: return ""
    if incl_ang > 90 or incl_ang < 0: return ""
    if frict_coef >= 1:return ""
    if belt_drive_eff >= 1: return ""

    alpha = math.radians(incl_ang)       # rad
    f_mass = mass * 9.8 * (math.sin(alpha) + math.cos(alpha) * frict_coef)  # N, resistance from weight and friction
    fa_uni_asc = f_mass + f_ex           # N, axial load when uniform speed ascending
    dp_1_m = dp_1/1000             # m
    load_tq = fa_uni_asc * dp_1_m/2  / belt_drive_eff / reduct_ratio    # N*m uniform ascending

    return "{:.4g}".format(float(load_tq))



def required_torque(acc_tq, load_tq, n_sf):
    acc_tq, load_tq, n_sf = float_input(acc_tq, load_tq, n_sf)
    if None in (acc_tq, load_tq, n_sf): return ""
    if any(x <= 0 for x in (acc_tq, load_tq, n_sf)): return ""
    if n_sf <1: return ""
    req_tq = (acc_tq + load_tq) * n_sf    # N*m
    return "{:.4g}".format(float(req_tq))


def required_angular_resolution (linear_res, dp_1, reduct_ratio):
    linear_res, dp_1, reduct_ratio = float_input(linear_res, dp_1, reduct_ratio)
    if None in (linear_res, dp_1, reduct_ratio): return ""
    if any(x <= 0 for x in (linear_res, dp_1, reduct_ratio)): return ""
    linear_res_mm = linear_res / 1000    # mm      from micron tomm
    req_ang_res = 360 * linear_res_mm/(math.pi*dp_1) * reduct_ratio # deg/step
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
        self.add_dataitem("mass", "Total Moving Mass (kg)", "Belt mass + work mass", False)
        self.add_dataitem("frict_coef", "Linear Guide Friction Coefficient", "", False)
        self.add_dataitem("f_ex", "External Force (N)", "", False)
        self.add_dataitem("v_max", "Max Speed (mm/s)", "", False)
        self.add_dataitem("acc_time", "Acceleration Time (s)", "Time to reach max speed", False)




        # Pulley
        self.add_widget(
            Label(text="[i][u][b]PULLEY[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None,
                  width=LABEL_WIDTH,
                  size_hint_y=None, font_size=FONT_SIZE * 1.2, text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT,
                  halign='left', valign='middle'))
        self.add_dataitem("belt_drive_eff", "Belt Drive Efficiency", "", False)
        self.add_dataitem("dp_1", "Driving Pulley Pitch Diameter (mm)", "", False)
        self.add_dataitem("j_p1", "Driving Pulley Inertia\n(10^-6 kg*m^2)", "", False)
        self.add_dataitem("dp_2", "Driven Pulley Pitch Diameter (mm)", "", False)
        self.add_dataitem("j_p2", "Driven Pulley Inertia\n(10^-6 kg*m^2)", "", False)
        self.add_dataitem("dp_idle", "Idler Pulley Pitch Diameter (mm)", "Put 0 if no idler", False)
        self.add_dataitem("j_idle", "Idler Pulley Inertia\n(10^-6 kg*m^2)", "Put 0 if no idler", False)
        self.add_dataitem("qty_idle", "Number of Idlers", "Put 0 if no idler", False)




        # Transmission
        self.add_widget(Label(text="[i][u][b]TRANSMISSION[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                              size_hint_y=None, font_size=FONT_SIZE*1.2,text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT, halign='left', valign='middle'))

        self.add_dataitem("reduct_ratio", "Reduction Ratio (Motor to Drving)", "Put 1 for direct coupling", False)
        self.add_dataitem("j_reduct", "Reduction Inertia\n(10^-6 kg*m^2)", "Put 0 for direct coupling", False)
        self.add_dataitem("linear_res", "Linear Resolution (μm)", "", False)
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
        if data == None: data_item.check_val = "X"
        elif (data > lower or (lower_equal and data == lower)) and \
                (data < upper or (upper_equal and data == upper)):
            data_item.check_val = ""
        else:
            data_item.check_val = "X"

    def calculate_update(self, instance):

        input_text = (
            self.incl_ang.value, self.mass.value, self.frict_coef.value, self.f_ex.value, self.v_max.value,self.acc_time.value,
            self.belt_drive_eff.value, self.dp_1.value, self.j_p1.value, self.dp_2.value, self.j_p2.value, self.dp_idle.value, self.j_idle.value, self.qty_idle.value,
            self.reduct_ratio.value, self.j_reduct.value, self.linear_res.value, self.j_motor.value, self.n_sf.value)

        print(input_text)

        self.check_data(self.incl_ang, 0, 90, True, True)        # 0<=incl_ang<=90
        self.check_data(self.mass, 0, math.inf, False,False)           # 0<mass<inf
        self.check_data(self.frict_coef, 0, 1, False, False)     # 0<frict_coef<1
        self.check_data(self.f_ex, 0, math.inf, True,False)            # 0<=f_ex<inf
        self.check_data(self.v_max, 0, math.inf, False, False)         # 0<v_max<inf
        self.check_data(self.acc_time, 0, math.inf, False, False)  # 0<acc_time<inf
        self.check_data(self.belt_drive_eff, 0, 1, False, False)         # 0<belt_drive_eff<1
        self.check_data(self.dp_1, 0, math.inf, False, False)       # 0<   <inf
        self.check_data(self.j_p1, 0, math.inf, False, False)        # 0<   <inf
        self.check_data(self.dp_2, 0, math.inf, False, False)       # 0<   <inf
        self.check_data(self.j_p2, 0, math.inf, False, False)        # 0<   <inf
        self.check_data(self.dp_idle, 0, math.inf, True, False)       # 0<=   <inf
        self.check_data(self.j_idle, 0, math.inf, True, False)        # 0<=   <inf
        self.check_data(self.qty_idle, 0, math.inf, True, False)        # 0<=   <inf


        self.check_data(self.reduct_ratio, 0, math.inf, False, False)  # 0<reduct_ratio<inf
        self.check_data(self.j_reduct, 0, math.inf, True, False)  # 0<j_reduct<inf
        self.check_data(self.linear_res, 0, math.inf, False, False)  # 0<linear_res<inf
        self.check_data( self.j_motor, 0, math.inf, True, False)  # 0<=j_motor<inf   # j_motor =0 to help initial guessing
        self.check_data(self.n_sf, 1, math.inf, True, False)  # 1<=n_sf<inf

        all_checks = [
            self.incl_ang.check_val,
            self.mass.check_val,
            self.frict_coef.check_val,
            self.f_ex.check_val,
            self.v_max.check_val,
            self.acc_time.check_val,
            self.belt_drive_eff.check_val,
            self.dp_1.check_val,
            self.j_p1.check_val,
            self.dp_2.check_val,
            self.j_p2.check_val,
            self.dp_idle.check_val,
            self.j_idle.check_val,
            self.qty_idle.check_val,
            self.reduct_ratio.check_val,
            self.j_reduct.check_val,
            self.linear_res.check_val,
            self.j_motor.check_val,
            self.n_sf.check_val,
        ]


        if "X" in all_checks:
            self.warning.text = "[i][b]INVALID INPUT[/b][/i]"
            return
        else:
            self.warning.text = ""

        self.j_load.value = load_inertia( self.dp_1.value, self.dp_2.value, self.dp_idle.value, self.j_p1.value, self.j_p2.value, self.j_idle.value, self.qty_idle.value, self.mass.value, self.reduct_ratio.value, self.j_reduct.value)

        self.req_rpm.value = required_rpm(self.v_max.value, self.dp_1.value, self.reduct_ratio.value)

        self.acc_tq.value = acceleration_torque(self.req_rpm.value, self.acc_time.value, self.j_load.value, self.j_motor.value)

        self.load_tq.value = load_toruqe( self.incl_ang.value, self.mass.value, self.frict_coef.value, self.f_ex.value, self.dp_1.value, self.belt_drive_eff.value, self.reduct_ratio.value)

        self.req_tq.value = required_torque(self.acc_tq.value, self.load_tq.value, self.n_sf.value)

        self.req_ang_res.value = required_angular_resolution(self.linear_res.value, self.dp_1.value, self.reduct_ratio.value)

        self.j_motor_display.value = self.j_motor.value

        self.n_sf_display.value = self.n_sf.value


        return


    def reset_input(self, instance):

        all_data = [
            self.incl_ang,
            self.mass,
            self.frict_coef,
            self.f_ex,
            self.v_max,
            self.acc_time,
            self.belt_drive_eff,
            self.dp_1,
            self.j_p1,
            self.dp_2,
            self.j_p2,
            self.dp_idle,
            self.j_idle,
            self.qty_idle,
            self.reduct_ratio,
            self.j_reduct,
            self.linear_res,
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



