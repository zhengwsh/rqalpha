from queue import Queue
from datetime import timedelta, datetime

from rqalpha.interface import AbstractEventSource
from rqalpha.events import Events


class VNPYEventSource(AbstractEventSource):
    def __init__(self):
        self._tick_que = Queue()

    def put_tick(self, tick):
        self._tick_que.put(tick)

    def events(self, start_date, end_date, frequency):
        while datetime.now() < start_date:
            continue

        while True:
            if not self._tick_que.empty():
                tick = self._tick_que.get()
                calendar_dt = tick['datetime']
                if calendar_dt > end_date:
                    break
                # TODO 验证逻辑是否正确
                dt_before_night_trading = calendar_dt.replace(hour=20, minute=30, second=0, microsecond=0)
                if calendar_dt > dt_before_night_trading:
                    trading_dt = calendar_dt + timedelta(days=1)
                else:
                    trading_dt = calendar_dt
                yield calendar_dt, trading_dt, Events.BAR
