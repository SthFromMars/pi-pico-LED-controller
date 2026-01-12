from config import *
from machine import Pin, PWM
from utime import sleep

def initialize_pins():
    pins = {
        "base": Pin("LED", Pin.OUT),
        "red": Pin(RED_PIN, Pin.OUT),
        "green": Pin(GREEN_PIN, Pin.OUT),
        "blue": Pin(BLUE_PIN, Pin.OUT)
    }
    pins["base"].on()
    return pins

def initialize_pwm(pins):
    pwms = {}
    for pin in pins.keys():
        if pin == "base":
            continue
        pwm = PWM(pins[pin])
        pwm.freq(1000)
        pwm.duty_u16(0)
        pwms[pin] = pwm
    return pwms

def deinitialize(pins, pwms):
    for pwm in pwms.values():
        pwm.duty_u16(0)
    sleep(0.1)
    for pwm in pwms.values():
        pwm.deinit()
    sleep(0.1)
    for pin in pins.values():
        pin.off()
    sleep(0.1)

def convert_hex_to_single_color(hex_color, id, brightness):
    bit8 = int(hex_color[id*2+1 : id*2+3], 16)
    bit8 = round(bit8 * brightness / 100 )
    bit16 = bit8 * 257
    return bit16

def convert_hex_to_rgb(hex_color, brightness):
    color = {
        "red": convert_hex_to_single_color(hex_color, 0, brightness),
        "green": convert_hex_to_single_color(hex_color, 1, brightness),
        "blue": convert_hex_to_single_color(hex_color, 2, brightness)
    }
    return color

def set_color(state, pwms):
    rgb = convert_hex_to_rgb(state["color"], state["brightness"])
    for color in rgb.keys():
        duty = rgb[color]
        if state["use_color_correction"]:
            duty = round(duty * COLOR_CORRECTION[color])
        pwms[color].duty_u16(duty)

def change_power(state, pins, pwms):
    pwms_return = None
    if state["turned_on"]:
        pwms_return = initialize_pwm(pins)
        set_color(state, pwms_return)
    else:
        deinitialize(pins, pwms)
    return pwms_return