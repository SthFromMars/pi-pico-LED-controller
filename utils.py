from config import *
from machine import Pin, PWM
from utime import sleep

def initialize_pins():
    pins = {
        "red": Pin(RED_PIN, Pin.OUT),
        "green": Pin(GREEN_PIN, Pin.OUT),
        "blue": Pin(BLUE_PIN, Pin.OUT)
    }
    return pins

def initialize_pwm(pins):
    pwms = {}
    for pin in pins.keys():
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

def convert_hex_to_single_color(hex_color, id):
    bit8 = int(hex_color[id*2+1 : id*2+3], 16)
    return bit8

def convert_hex_to_rgb(hex_color):
    color = {
        "red": convert_hex_to_single_color(hex_color, 0),
        "green": convert_hex_to_single_color(hex_color, 1),
        "blue": convert_hex_to_single_color(hex_color, 2)
    }
    return color

def convert_8bit_to_16bit(bit8):
    bit16 = {}
    for color in bit8:
        bit16[color] = (bit8[color]**2) * 257/255
    return bit16

def set_color(state, pwms):
    rgb = convert_hex_to_rgb(state["color"])
    if state["use_color_correction"]:
        for color in rgb.keys():
            rgb[color] = rgb[color] * COLOR_CORRECTION[color]
        max_value = max(rgb.values())
        if max_value < 255:
            ratio = 255 / max_value
            for color in rgb.keys():
                rgb[color] = round(rgb[color] * ratio)
    rgb = convert_8bit_to_16bit(rgb)
    for color in rgb.keys():
        duty = round(rgb[color] * state["brightness"] / 100)
        pwms[color].duty_u16(duty)

def change_power(state, pins, pwms):
    pwms_return = None
    if state["turned_on"]:
        pwms_return = initialize_pwm(pins)
        set_color(state, pwms_return)
    else:
        deinitialize(pins, pwms)
    return pwms_return