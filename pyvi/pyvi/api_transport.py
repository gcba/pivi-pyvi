# This file is part of the Pyvi software package. Released
# under the Creative Commons ATT-NC-ShareAlire license
# http://creativecommons.org/licenses/by-nc-sa/4.0/
# Copyright (C) 2014, 2015 LESS Industries S.A.
# Lucas Chiesa <lucas@lessinduestries.com>

from transport import Transport
import urllib
import urllib2


class ApiTransport(Transport):
    """
    This transports the messages over an UDP channel.
    We use it to send datagrams to the LESS cloud.
    """
    def __init__(self):
        Transport.__init__(self)
        self.sock = None
        self.srv_addr = None
        self.api_name = None
        self.token = None
        self.ids_sensor = {}

    def _open(self):
        self.api_name = self.settings['server']
        self.token = self.settings['token']
        self.datatype1 = self.settings['type_vrms']
        self.datatype2 = self.settings['type_irms']
        self.datatype3 = self.settings['type_power']
        self.ids_sensor = self.settings['gcba_id']

    def _encode(self, sensor, data1, data2, data3):
        query_args = urllib.urlencode({
            "id1": sensor,
            "datatype1": self.datatype1,
            "data1": str(data1),
            "id2": sensor,
            "datatype2": self.datatype2,
            "data2": str(data2),
            "id3": sensor,
            "datatype3": self.datatype3,
            "data3": str(data3)
        })
        return query_args

    def _post(self, args):
        request = urllib2.Request(self.api_name)
        request.add_data(args)
        request.add_header("token", self.token)
        result = urllib2.urlopen(request).read()
        return result

    def write(self, value):

        gcba_id = self.ids_sensor[value.id_].strip()

        if int(gcba_id) == 0:
            return "sensor not config in api_backend"
        try:
            encode_args = self._encode(gcba_id, value.Vrms, value.Irms, value.Power)
            result = self._post(encode_args)
        except:
            raise
            return False
        return result

    def close(self):
        pass

    def reopen(self):
        pass
