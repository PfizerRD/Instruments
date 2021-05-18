def start():
    return {"command": "start"}


def stop():
    return {"command": "stop"}


def set_flowrate(value):
    return {"command": "set_flowrate", "parameters": {"args": (value)}}
