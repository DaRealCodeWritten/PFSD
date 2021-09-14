import json
import sqlite3
from select import select
from socket import socket, AF_INET, SOCK_STREAM


class FSDConnector:
    def __init__(self, local_deployment: bool):
        self.sock = socket(family=AF_INET, type=SOCK_STREAM)
        self.fsdb = sqlite3.connect("identifier.sqlite")
        self.local = local_deployment
        self.clients = {}

    def data_listener(self):
        while 1:
            in_event, out_event = select([self.sock, ], [self.sock, ], [])
            if in_event is self.sock:
                # Inbound client connection
                i, o = select([self.sock], [self.sock], [])
                client, _ = self.sock.accept()
                if i is not self.sock:
                    data = self.sock.recv(1024)
                    try:
                        decode = data.decode("UTF-8")
                    except UnicodeDecodeError:
                        err = {"message": "Unable to decode last message, please contact the dev of your pilot client"}
                        serr = json.dumps(err)
                        client.send(serr.encode("UTF-8"))
                        client.close()

            else:
                template = {
                    "latitude": None,
                    "longitude": None,
                    "squawk": None,
                    "xpdrm": None,
                    "heading": None,
                    "pitch": None
                    "aircraft": None,
                    "groundspeed": None,
                    "CID": None
                }
                template_types = {
                    "latitude": str,
                    "longitude": str,
                    "squawk": int,
                    "xpdrm": str,
                    "heading": float,
                    "pitch": float,
                    "aircraft": str,
                    "groundspeed": float,
                    "CID": int
                }
                data = self.sock.recv(1024)
                if data:
                    sjs = data.decode()
                    dec = json.loads(sjs)
                    template.update(dec)
                    if any(key is None for key in template):
                        pass
                    else:
                        passed = 1
                        for output in zip(template, template_types):
                            if type(output[0]) != type(output[1]):
                                passed = 0
                        if passed:
                            dump = json.dumps(template)
                            self.sock.sendall(dump.encode("UTF-8"))

