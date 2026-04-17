from config import *
from phew import server, connect_to_wifi
import json
from utils import initialize_pins, initialize_pwm, deinitialize, change_power, set_color
from serialization import get_state, write_state
import re
from machine import Pin

def main():
    pins = initialize_pins()
    print(connect_to_wifi(SSID, PASSWORD))
    basePin =  Pin("LED", Pin.OUT)
    basePin.on()
    state = get_state()
    pwms = None
    if state["turned_on"]:
        pwms = initialize_pwm(pins)
        set_color(state, pwms)
    with open("index.html", "r") as f:
        html = f.read()
    
    colorRegex = re.compile("^#[A-Fa-f0-9][A-Fa-f0-9][A-Fa-f0-9][A-Fa-f0-9][A-Fa-f0-9][A-Fa-f0-9]$")

    @server.route("/")
    def index(request):
        return server.Response(
            html, 
            status=200, 
            headers={"Content-Type": "text/html"}
        )

    @server.route("/getstate", methods=["GET"])
    def get_state_route(request):
        return server.Response(
            json.dumps(state), 
            status=200, 
            headers={"Content-Type": "application/json"}
        )

    @server.route("/setcolor", methods=["POST"])
    def set_color_route(request):
        color = request.data.get("color", "#000000")
        if colorRegex.search(color) is None:
            return "Bad color code", 400
        state["color"] = color
        state["brightness"] = request.data.get("brightness", 100)
        state["use_color_correction"] = request.data.get("use_color_correction", True)
        nonlocal pwms
        if not state["turned_on"]:
            state["turned_on"] = True
            pwms = change_power(state, pins, pwms)
        else:
            set_color(state, pwms)
        write_state(state)

        return server.Response(
            json.dumps(state), 
            status=200, 
            headers={"Content-Type": "application/json"}
        )

    @server.route("/setpower", methods=["POST"])
    def set_power(request):
        turned_on = request.data.get("turned_on", False)

        if turned_on != state["turned_on"]:
            state["turned_on"] = turned_on
            write_state(state)
            nonlocal pwms
            pwms = change_power(state, pins, pwms)

        return server.Response(
            json.dumps(state), 
            status=200, 
            headers={"Content-Type": "application/json"}
        )

    @server.catchall()
    def catchall(request):
        return "Not found", 404

    try:
        server.run()
    except KeyboardInterrupt:
        if state["turned_on"]:
            deinitialize(pins, pwms)
        print("Finished.")
