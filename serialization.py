import json

def get_state():
    try:
        with open("state.json", "r") as f:
            return json.loads(f.read())
    except OSError:
        state = {
            "turned_on": False,
            "color": "#000000",
            "brightness": 0,
            "use_color_correction": True
        }
        write_state(state)
        return state
    
def write_state(state):
    with open("state.json", "w") as f:
        f.write(json.dumps(state))