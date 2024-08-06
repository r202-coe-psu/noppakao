import datetime
import javascript as js

from browser import ajax, document, html, window, timer, aio


bangkok_timezone = datetime.timezone(datetime.timedelta(hours=7), name="Asia/Bangkok")


class MainMonitor:
    def __init__(self):
        self.acquisition_interval = 60

    async def monitor(self):
        await self.setup()

        while self.running:
            print(f"monitor: wake up {datetime.datetime.now()}")
            await aio.sleep(self.acquisition_interval)

    async def setup(self):
        pass

    def start(self):
        print("start")
        aio.run(self.monitor())
