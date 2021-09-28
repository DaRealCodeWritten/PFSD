from threading import Thread
from fsd_server import datafeed
from fsd_server import connector
class FSD_Server:
    def __init__(self, region: str, local_deployment=False):
        self.region = region
        self.local = local_deployment
        self.connector = connector.FSDConnector(local_deployment)
        self.datafeed = None
        #self.datathread = Thread(target=self.datafeed.launch, args=(self.local,))
        self.connectthread = Thread(target=self.connector.client_listener)

    def launch(self):
        self.connectthread.start()
        #self.datafeed.start()