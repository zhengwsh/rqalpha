# -*- coding: utf-8 -*-
from rqalpha.interface import AbstractMod

from .vnpy_engine import RQVNPYEngine
from .vnpy_event_source import VNPYEventSource
from .vnpy_broker import VNPYBroker


class VNPYMod(AbstractMod):
    def __init__(self):
        self._env = None
        self._engine = None

    def start_up(self, env, mod_config):
        self._env = env
        self._engine = RQVNPYEngine(env, mod_config)
        self._env.set_broker(VNPYBroker(env, self._engine))
        self._env.set_event_source(VNPYEventSource(env, self._engine))
        # TODO: CTP登录因该放到 before_trading 中好一点
        self._engine.connect()

    def tear_down(self, code, exception=None):
        self._engine.exit()
