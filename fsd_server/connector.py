import json
import sqlite3
from select import select
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM


class FSDConnector:
    def __init__(self, local_deployment: bool):
        self.sock = socket(family=AF_INET, type=SOCK_STREAM)
        self.fsdb = sqlite3.connect("identifier.sqlite")
        self.fscrs = self.fsdb.cursor()
        self.local = local_deployment
        self.clients = {}

    def client_listener(self):
        print("Starting PFSD Connector...")
        self.sock.bind(("127.0.0.1", 1987))
        print("Started PFSD Connector")
        while True:
            print("Listening for client...")
            event = select([self.sock], [self.sock], [])
            if event is self.sock:
                client, _ = self.sock.accept()
                i = select([self.sock], [self.sock], [], 5)
                if i is not self.sock:
                    print("Waiting for data")
                    data = self.sock.recv(1024)
                    try:
                        print("Got the data, reading")
                        decode = data.decode("UTF-8")
                        js = json.loads(decode)
                        js["client"] = client
                        self.clients[js.get("CID")] = js
                        out = self.fscrs.execute("SELECT * FROM FSD_USERS WHERE cid = ?", (js.get("CID")))
                        print(out)
                        thread = Thread(target=self.data_listener, args=(client, js.get("CID")), name=js.get("CID"))
                        thread.start()
                    except UnicodeDecodeError:
                        print("Unable to read data, connection terminated")
                        err = {"message": "Unable to decode last message, please contact the dev of your pilot client"}
                        serr = json.dumps(err)
                        client.send(serr.encode("UTF-8"))
                        client.close()

    def data_listener(self, client, cid):
        while 1:
            try:
                in_event = select([client, ], [client, ], [])
                if in_event is client:
                    print("Detected inbound connection on a client connection, this is definitely not intended")
                    client.close()
                else:
                    template = {
                        "latitude": None,
                        "longitude": None,
                        "squawk": None,
                        "xpdrm": None,
                        "heading": None,
                        "pitch": None,
                        "aircraft": None,
                        "groundspeed": None,
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
                            for output in zip(template.values(), template_types.values()):
                                if not isinstance(output[0], output[1]):
                                    passed = 0
                            if passed:
                                dump = json.dumps(template)
                                self.sock.sendall(dump.encode("UTF-8"))
            except Exception as err:
                print(f"Data listener for {cid} raised an exception\n{err}")
