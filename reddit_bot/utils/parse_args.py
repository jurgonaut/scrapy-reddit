import os

def parse_args(settings, aArg):
    if os.environ.get(aArg):
        return os.environ.get(aArg)
    elif settings.get(aArg):
        return settings.get(aArg)
    else:
        raise RuntimeError("Couldn't parse arg: {aArg}")