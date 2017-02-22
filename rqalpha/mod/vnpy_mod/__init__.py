from rqalpha.interface import AbstractMod


class VNPYMod(AbstractMod):
    def __init__(self):
        pass

    def start_up(self, env, mod_config):
        from .vnpy_broker import VNPYBroker
        from .vnpy_event_source import VNPYEventSource

        if env.config.mod.vnpy.vnpy_data_source:
            from .vnpy_data_source import VNPYDataSource

    def tear_down(self, code, exception=None):
        pass


def load_mod():
    return VNPYMod()