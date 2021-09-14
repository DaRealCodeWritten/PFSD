from threading import Thread
from fsd_server import datafeed
from fsd_server import connector
class FSD_Server:
    def __init__(self, region: str, local_deployment=False):
        self.region = region
        self.local = local_deployment
        self.connector = None
        self.datafeed = None
        #self.datathread = Thread(target=self.datafeed.launch, args=(self.local,))
        self.connectthread = Thread(target=self.connector.launch, args=(self.local,))

    async def launch(self):
        self.connectthread.start()
        #self.datafeed.start()