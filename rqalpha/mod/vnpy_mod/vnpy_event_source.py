# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from rqalpha.utils.logger import system_log
from rqalpha.interface import AbstractEventSource
from rqalpha.events import Event, EVENT
from rqalpha.utils import RqAttrDict


class VNPYEventSource(AbstractEventSource):
    def __init__(self, env, vnpy_engine):
        self._env = env
        self._engine = vnpy_engine
        self._before_trading_processed = False

    def events(self, start_date, end_date, frequency):
        while datetime.now().date() < start_date:
            continue

        before_trading_flag = True

        while True:
            # TODO: 明确 before_trading 逻辑
            if before_trading_flag:
                before_trading_flag = False
                system_log.debug("VNPYEventSource: before trading event")
                yield Event(EVENT.BEFORE_TRADING, datetime.now(), datetime.now())
                continue

            tick = self._engine.get_tick()
            system_log.debug("VNPYEventSource: tick {}", tick.__dict__)

            calendar_dt = tick['datetime']
            # if calendar_dt > end_date:
            #     break

            if calendar_dt.hour > 20:
                trading_dt = calendar_dt + timedelta(days=1)
            else:
                trading_dt = calendar_dt

            yield Event(EVENT.TICK, calendar_dt, trading_dt, {"tick": RqAttrDict(tick)})
