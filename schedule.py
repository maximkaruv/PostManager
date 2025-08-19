import time
from datetime import datetime, timedelta

class Schedule:
    def __init__(self, timetable: list[str], job: function, time_scale: int):
        self.job = job
        self.time_scale = time_scale
        self.schedule_minutes = [self.parse_time(t) for t in timetable]

    # переводим расписание в минуты с начала суток
    def parse_time(t: str) -> int:
        h, m = map(int, t.split(":"))
        return h * 60 + m

    # запуск расписания текущего дня
    def run_day(self, day: int):
        virtual_minutes = 0
        end_of_day = 24 * 60

        # старт реального времени
        start_real = datetime.now()
        next_tick = start_real

        while virtual_minutes < end_of_day:
            # входит ли текущая минута в расписание
            if virtual_minutes in self.schedule_minutes:
                self.job()
                h, m = divmod(virtual_minutes, 60)
                print(f"[Задача запущена] День {day} | время {h:02d}:{m:02d}")

            # шаг на 1 виртуальную минуту
            virtual_minutes += 1
            next_tick += timedelta(seconds=60 / self.time_scale)

            # ждём до момента "следующей виртуальной минуты"
            sleep_time = (next_tick - datetime.now()).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)

    # запуск общего цикла
    def run_forever(self):
        day = 1
        while True:
            print(f"\n=== Начало виртуального дня {day} ===")
            self.run_day(day)
            day += 1

