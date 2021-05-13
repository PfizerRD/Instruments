def formatter(func):
    def wrap(id):
        cmd = func(id)
        return f"{id}{cmd}{chr(13)}".encode('ascii')
    return wrap


@formatter
def start(id):
    return "H"


@formatter
def stop(id):
    return "I"
