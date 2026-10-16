from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
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



def ball_screw_inertia (bs_dia, bs_len, bs_dens):  #for calculation mode
    bs_dia, bs_len, bs_dens = float_input(bs_dia, bs_len, bs_dens)
    if None in (bs_dia, bs_len, bs_dens): return ""
    if any(x <= 0 for x in (bs_dia, bs_len, bs_dens)): return ""
    bs_dia_m = bs_dia / 1000  # m
    bs_len_m = bs_len / 1000  # m
    bs_mass = 0.25 * math.pi * bs_dia_m ** 2 * bs_len_m * bs_dens  # kg
    j_bs = 0.125 * bs_mass * bs_dia_m ** 2 * 1e6  # 10^-6 kg·m²
    return "{:.4g}".format(float(j_bs))


def load_inertia(bs_lead, mass, j_bs, reduct_ratio, j_reduct):
    bs_lead, mass, j_bs, reduct_ratio, j_reduct = float_input(bs_lead, mass, j_bs, reduct_ratio, j_reduct)
    if None in (bs_lead, mass, j_bs, reduct_ratio, j_reduct): return ""
    if any(x <= 0 for x in (bs_lead, mass, j_bs, reduct_ratio)): return ""
    if j_reduct < 0: return ""
    bs_lead_m = bs_lead / 1000  # m/rev
    j_mass = mass * (bs_lead_m / (2 * math.pi))**2 *1e6  # 10^-6 kg·m²
    j_load = (j_mass + j_bs) / (reduct_ratio**2) + j_reduct  # 10^-6 kg·m²
    return "{:.4g}".format(float(j_load))


def required_rpm(v_max, bs_lead, reduct_ratio):
    v_max, bs_lead, reduct_ratio = float_input(v_max, bs_lead, reduct_ratio)
    if None in (v_max, bs_lead, reduct_ratio): return ""
    if any(x <= 0 for x in (v_max, bs_lead,reduct_ratio)): return ""
    req_rpm = reduct_ratio* (v_max / bs_lead) * 60    # v_max: mm/s  bs_lead: mm/rev
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


def uniform_motion_torque(incl_ang, mass, frict_coef, f_ex, bs_lead, bs_eff, reduct_ratio):
    incl_ang, mass, frict_coef, f_ex, bs_lead, bs_eff, reduct_ratio = float_input(incl_ang, mass, frict_coef, f_ex, bs_lead, bs_eff, reduct_ratio)
    if None in (incl_ang, mass, frict_coef, f_ex, bs_lead, bs_eff, reduct_ratio): return ""
    if any(x <= 0 for x in (mass, frict_coef, bs_lead, bs_eff, reduct_ratio)): return ""
    if f_ex < 0: return ""
    if incl_ang > 90 or incl_ang < 0: return ""
    if frict_coef >= 1:return ""
    if bs_eff >= 1: return ""
    alpha = math.radians(incl_ang)       # rad
    f_mass = mass * 9.8 * (math.sin(alpha) + math.cos(alpha) * frict_coef)  # N, resistance from weight and friction
    fa_uni_asc = f_mass + f_ex           # N, axial load when uniform speed ascending
    bs_lead_m = bs_lead/1000             # mm/rev
    uni_asc_tq = fa_uni_asc * bs_lead_m / (2*math.pi * bs_eff) / reduct_ratio   # N*m uniform ascending
    return "{:.4g}".format(float(uni_asc_tq))


def ball_screw_preload(incl_ang, mass, frict_coef, f_ex, v_max, acc_time):  #for F/3 mode
    incl_ang, mass, frict_coef, f_ex, v_max, acc_time = float_input(incl_ang, mass, frict_coef, f_ex, v_max, acc_time)
    if None in (incl_ang, mass, frict_coef, f_ex, v_max, acc_time): return ""
    if any(x <= 0 for x in (mass, frict_coef, v_max, acc_time)): return ""
    if f_ex < 0: return ""
    if incl_ang > 90 or incl_ang < 0: return ""
    if frict_coef >= 1: return ""
    alpha = math.radians(incl_ang)       # rad
    f_mass = mass * 9.8 * (math.sin(alpha) + math.cos(alpha) * frict_coef)  # N, resistance from weight and friction
    v_max_m = v_max /1000   #m/s
    fa_acc_asc = f_mass + f_ex + mass*(v_max_m/acc_time)  #N max axial load, acc during ascending
    bs_preload = fa_acc_asc / 2.83  # N
    # "preload=max axial load F/3 method"  use 2.8 or 2.83 or 2^1.5
    return "{:.4g}".format(float(bs_preload))


def ballscrew_preload_torque(bs_lead, bs_dia, bs_preload, reduct_ratio):
    bs_lead, bs_dia, bs_preload, reduct_ratio = float_input(bs_lead, bs_dia, bs_preload, reduct_ratio)
    if None in (bs_lead, bs_dia, bs_preload, reduct_ratio): return ""
    if any(x <= 0 for x in (bs_lead, bs_dia, reduct_ratio)): return ""
    if bs_preload < 0: return ""
    bs_lead_m = bs_lead/1000  # m/rev
    assume_pitch_dia = bs_lead / 6 + bs_dia  #mm   this is a rough assumption base mutiple THK model
    tan_beta = bs_lead / (math.pi * assume_pitch_dia)    # need to use ball center to center distance AKA pitch diameter
    ref_tq = 0.05 * tan_beta**-0.5  *  bs_preload * bs_lead_m / (2*math.pi)  # N*m
    bs_preload_tq = ref_tq *1.5 / reduct_ratio   # N
    # becuase we do not know the torque fluctuation factor, assume a high value here
    return "{:.4g}".format(float(bs_preload_tq))


def load_torque(uni_asc_tq, bs_preload_tq):
    uni_asc_tq, bs_preload_tq = float_input(uni_asc_tq, bs_preload_tq)
    if None in (uni_asc_tq, bs_preload_tq): return ""
    if uni_asc_tq <= 0: return ""
    if bs_preload_tq < 0: return ""
    load_tq = uni_asc_tq + bs_preload_tq    #N*m
    return "{:.4g}".format(float(load_tq))



def load_torque_110(uni_asc_tq):                # preload as additonal 10% load torque
    uni_asc_tq, = float_input(uni_asc_tq,)
    if None in (uni_asc_tq,): return ""
    if uni_asc_tq <= 0: return ""
    load_tq = uni_asc_tq * 1.1    #N*m
    return "{:.4g}".format(float(load_tq))



def required_torque(acc_tq, load_tq, n_sf):
    acc_tq, load_tq, n_sf = float_input(acc_tq, load_tq, n_sf)
    if None in (acc_tq, load_tq, n_sf): return ""
    if any(x <= 0 for x in (acc_tq, load_tq, n_sf)): return ""
    if n_sf <1: return ""
    req_tq = (acc_tq + load_tq) * n_sf    # N*m
    return "{:.4g}".format(float(req_tq))


def required_angular_resolution (linear_res, bs_lead, reduct_ratio):
    linear_res, bs_lead, reduct_ratio = float_input(linear_res, bs_lead, reduct_ratio)
    if None in (linear_res, bs_lead, reduct_ratio): return ""
    if any(x <= 0 for x in (linear_res, bs_lead, reduct_ratio)): return ""
    linear_res_mm = linear_res / 1000    # mm
    req_ang_res = 360 * (linear_res_mm / bs_lead) * reduct_ratio # deg/step
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
            size_hint_y=None, height=ROW_HEIGHT*1, halign='left', valign='middle', text_size=(LABEL_WIDTH, None)
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
        self.add_dataitem("mass", "Total Moving Mass (kg)", "Table mass + work mass", False)
        self.add_dataitem("frict_coef", "Linear Guide Friction Coefficient", "", False)
        self.add_dataitem("f_ex", "External Force (N)", "", False)
        self.add_dataitem("v_max", "Max Speed (mm/s)", "", False)
        self.add_dataitem("acc_time", "Acceleration Time (s)", "Time to reach max speed", False)




        # Ball Screw
        self.add_widget(Label(text="[i][u][b]BALL SCREW[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                              size_hint_y=None, font_size=FONT_SIZE*1.2,text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT, halign='left', valign='middle'))

        self.add_dataitem("bs_eff", "Ball Screw Efficiency", "Ball screw about 0.9",False)
        self.add_dataitem("bs_lead", "Ball Screw Lead (mm/rev)", "Displacement per rev",False)
        self.add_dataitem("bs_dia", "Ball Screw Diameter (mm)", "", False)

        self.add_dataitem("j_bs_choice", "Ball Screw Inertia Option", "Choose an input option", True)
        self.add_toggleitem(["Manual Input", "Calculate"], "j_bs_choice_toggle")
        self.add_dataitem("bs_len", "Ball Screw Length (mm)", "",False)
        self.add_dataitem("bs_dens", "Ball Screw Density (kg/m^3)", "Steel 7900 kg/m^3", False)
        self.add_dataitem("j_bs", "Ball Screw Inertia\n(10^-6 kg*m^2)", "Manual input", False)

        self.bs_len.background, self.bs_dens.background, self.j_bs.background = (0.8, 0.8, 0.8, 1), (0.8, 0.8, 0.8, 1), (0.8, 0.8, 0.8, 1)
        self.j_bs_choice_toggle_1.bind(on_press=self.j_bs_pressed)
        self.j_bs_choice_toggle_2.bind(on_press=self.j_bs_pressed)

        self.add_dataitem("bs_preload_choice", "Ball Screw Preload Option", "Choose an input option", True)
        self.add_toggleitem(["Manual Input", "F/3 Method", "+10% Load Torque"], "bs_preload_choice_toggle")
        self.add_dataitem("bs_preload", "Ball Screw Preload (N)", "Manual input",False)

        self.bs_preload.background = (0.8, 0.8, 0.8, 1)
        self.bs_preload_choice_toggle_1.bind(on_press=self.bs_preload_pressed)
        self.bs_preload_choice_toggle_2.bind(on_press=self.bs_preload_pressed)
        self.bs_preload_choice_toggle_3.bind(on_press=self.bs_preload_pressed)


        # Transmission
        self.add_widget(Label(text="[i][u][b]TRANSMISSION[/b][/u][/i]", markup=True, color=(0, 0, 0, 1), size_hint_x=None, width=LABEL_WIDTH,
                              size_hint_y=None, font_size=FONT_SIZE*1.2,text_size=(LABEL_WIDTH, None), height=ROW_HEIGHT, halign='left', valign='middle'))

        self.add_dataitem("reduct_ratio", "Reduction Ratio (Motor to Shaft)", "Put 1 for direct coupling", False)
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




    def j_bs_pressed(self, instance):
        self.j_bs_pressed_format()


    def bs_preload_pressed(self, instance):
        self.bs_preload_pressed_format()


    def j_bs_pressed_format(self):
        if self.j_bs_choice_toggle_1.state == "down":
            self.j_bs_choice.value = "Manual Input"
            #self.bs_len.readonly, self.bs_dens.readonly, self.j_bs.readonly  = True, True, False
            self.bs_len.color, self.bs_dens.color, self.j_bs.color = (0.5, 0.5, 0.5, 1), (0.5, 0.5, 0.5, 1), (0, 0, 0, 1)
            self.bs_len.background, self.bs_dens.background, self.j_bs.background = (0.8, 0.8, 0.8, 1), (0.8, 0.8, 0.8, 1), (1, 1, 1, 1)

        elif self.j_bs_choice_toggle_2.state == "down":
            self.j_bs_choice.value = "Calculate"
            #self.bs_len.readonly, self.bs_dens.readonly, self.j_bs.readonly = False, False, True
            self.bs_len.color, self.bs_dens.color, self.j_bs.color = (0, 0, 0, 1), (0, 0, 0, 1), (0.5, 0.5, 0.5, 1)
            self.bs_len.background, self.bs_dens.background, self.j_bs.background = (1, 1, 1, 1), (1, 1, 1, 1), (0.8, 0.8, 0.8, 1)

        else:
            self.j_bs_choice.value = ""
            #self.bs_len.readonly, self.bs_dens.readonly, self.j_bs.readonly  = True, True, True
            self.bs_len.color, self.bs_dens.color, self.j_bs.color = (0.5, 0.5, 0.5, 1), (0.5, 0.5, 0.5, 1), (0.5, 0.5, 0.5, 1)
            self.bs_len.background, self.bs_dens.background, self.j_bs.background = (0.8, 0.8, 0.8, 1), (0.8, 0.8, 0.8, 1), (0.8, 0.8, 0.8, 1)


    def bs_preload_pressed_format(self):
        if self.bs_preload_choice_toggle_1.state == "down":
            self.bs_preload_choice.value = "Manual Input"
            #self.bs_preload.readonly = False
            self.bs_preload.color = (0, 0, 0, 1)
            self.bs_preload.background = (1, 1, 1, 1)

        elif self.bs_preload_choice_toggle_2.state == "down":
            self.bs_preload_choice.value = "F/3 Method"
            #self.bs_preload.readonly = True
            self.bs_preload.color = (0.5, 0.5, 0.5, 1)
            self.bs_preload.background = (0.8, 0.8, 0.8, 1)

        elif self.bs_preload_choice_toggle_3.state == "down":
            self.bs_preload_choice.value = "+10% Load Torque"
            #self.bs_preload.readonly = True
            self.bs_preload.color = (0.5, 0.5, 0.5, 1)
            self.bs_preload.background = (0.8, 0.8, 0.8, 1)

        else:
            self.bs_preload_choice.value = ""
            self.bs_preload.background = (0.8, 0.8, 0.8, 1)


    def add_toggleitem(self, option_text, group_name):
        box = BoxLayout(orientation='horizontal', size_hint_x=None, width=TOGGLE_WIDTH)
        for i, name in enumerate(option_text):
            btn = ToggleButton(
                text=name, group=group_name,
                size_hint_x=None, width=TOGGLE_WIDTH / len(option_text), size_hint_y=None, height=ROW_HEIGHT, font_size=LINEDIT_FONT_SIZE, state='normal')
            box.add_widget(btn)
            setattr(self, f"{group_name}_{i + 1}", btn)
        self.add_widget(box)


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
            self.incl_ang.value, self.mass.value, self.frict_coef.value, self.f_ex.value, self.v_max.value, self.acc_time.value, self.bs_eff.value, self.bs_lead.value,
            self.j_bs_choice.value, self.bs_dia.value, self.bs_len.value, self.bs_dens.value, self.j_bs.value, self.bs_preload_choice.value,
            self.bs_preload.value, self.reduct_ratio.value, self.j_reduct.value, self.linear_res.value, self.j_motor.value, self.n_sf.value)

        print(input_text)

        self.check_data(self.incl_ang, 0, 90, True, True)        # 0<=incl_ang<=90
        self.check_data(self.mass, 0, math.inf, False,False)           # 0<mass<inf
        self.check_data(self.frict_coef, 0, 1, False, False)     # 0<frict_coef<1
        self.check_data(self.f_ex, 0, math.inf, True,False)            # 0<=f_ex<inf
        self.check_data(self.v_max, 0, math.inf, False, False)         # 0<v_max<inf
        self.check_data(self.acc_time, 0, math.inf, False, False)      # 0<acc_time<inf
        self.check_data(self.bs_eff, 0, 1, False, False)         # 0<bs_eff<1
        self.check_data(self.bs_lead, 0, math.inf, False, False)       # 0<bs_lead<inf
        self.check_data(self.bs_dia, 0, math.inf, False, False)        # 0<bs_dia<inf

        if self.j_bs_choice.value == "Manual Input" or self.j_bs_choice.value == "Calculate":
            self.j_bs_choice.check_val = ""
        else:
            self.j_bs_choice.check_val = "X"

        if self.j_bs_choice.value == "Manual Input":
            self.bs_len.check_val = ""
            self.bs_dens.check_val = ""
            self.check_data(self.j_bs, 0, math.inf, False, False)     # 0<j_bs<inf
        elif self.j_bs_choice.value == "Calculate":
            self.check_data(self.bs_len, 0, math.inf, False, False)   # 0<bs_len<inf
            self.check_data(self.bs_dens, 0, math.inf, False, False)  # 0<bs_dens<inf
            self.j_bs.check_val = ""

        if self.bs_preload_choice.value == "Manual Input" or self.bs_preload_choice.value == "F/3 Method" or self.bs_preload_choice.value == "+10% Load Torque":
            self.bs_preload_choice.check_val = ""
        else:
            self.bs_preload_choice.check_val = "X"

        if self.bs_preload_choice.value == "Manual Input":
            self.check_data(self.bs_preload, 0, math.inf, True, False)  # 0<=bs_preload<inf
        else:
            self.bs_preload.check_val = ""

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
            self.bs_eff.check_val,
            self.bs_lead.check_val,
            self.j_bs_choice.check_val,
            self.bs_dia.check_val,
            self.bs_len.check_val,
            self.bs_dens.check_val,
            self.j_bs.check_val,
            self.bs_preload_choice.check_val,
            self.bs_preload.check_val,
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


        if self.j_bs_choice.value == "Calculate":
            self.j_bs.value = ball_screw_inertia(self.bs_dia.value, self.bs_len.value, self.bs_dens.value)
        elif self.j_bs_choice.value == "Manual Input":
            self.bs_len.value = ""
            self.bs_dens.value = ""

        self.j_load.value = load_inertia(self.bs_lead.value, self.mass.value, self.j_bs.value, self.reduct_ratio.value, self.j_reduct.value)

        self.req_rpm.value = required_rpm(self.v_max.value, self.bs_lead.value, self.reduct_ratio.value)

        self.acc_tq.value = acceleration_torque(self.req_rpm.value, self.acc_time.value, self.j_load.value, self.j_motor.value)

        self.uni_asc_tq = ""
        self.uni_asc_tq = uniform_motion_torque(self.incl_ang.value, self.mass.value, self.frict_coef.value, self.f_ex.value, self.bs_lead.value, self.bs_eff.value, self.reduct_ratio.value)

        if self.bs_preload_choice.value == "F/3 Method":
            self.bs_preload.value = ball_screw_preload(self.incl_ang.value, self.mass.value, self.frict_coef.value, self.f_ex.value, self.v_max.value, self.acc_time.value)
        elif self.bs_preload_choice.value == "+10% Load Torque":
            self.bs_preload.value = ""

        self.bs_preload_tq = ""
        self.bs_preload_tq = ballscrew_preload_torque(self.bs_lead.value, self.bs_dia.value, self.bs_preload.value, self.reduct_ratio.value)

        if self.bs_preload_choice.value == "+10% Load Torque": self.load_tq.value = load_torque_110(self.uni_asc_tq)
        else: self.load_tq.value = load_torque(self.uni_asc_tq, self.bs_preload_tq)

        self.req_tq.value = required_torque(self.acc_tq.value, self.load_tq.value, self.n_sf.value)

        self.req_ang_res.value = required_angular_resolution(self.linear_res.value, self.bs_lead.value, self.reduct_ratio.value)

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
            self.bs_eff,
            self.bs_lead,
            self.j_bs_choice,
            self.bs_dia,
            self.bs_len,
            self.bs_dens,
            self.j_bs,
            self.j_bs_choice,
            self.bs_preload_choice,
            self.bs_preload,
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

        self.j_bs_choice_toggle_1.state = "normal"
        self.j_bs_choice_toggle_2.state = "normal"

        self.bs_preload_choice_toggle_1.state = "normal"
        self.bs_preload_choice_toggle_2.state = "normal"
        self.bs_preload_choice_toggle_3.state = "normal"

        self.j_bs_pressed_format()
        self.bs_preload_pressed_format()



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



