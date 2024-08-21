class Base(object):
    def __init__(self, api, host, protocol, port=3000):
        self.api = api
        self.host = host
        self.protocol = protocol
        self.port = port
