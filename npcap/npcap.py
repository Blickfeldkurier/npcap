#! /usr/bin/env python3
import pprint
from zeroconf import ServiceBrowser, Zeroconf

class PrinterListener:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.packets = {}
        zerotypes = [
            "_ipp._tcp.local.",
            "_ipps._tcp.local.",
            "_printer._tcp.local.",
            "_pdl-datastream._tcp.local.",
            "_print-caps._tcp.local."
        ]
        self.browser = []
        for item in zerotypes:
            self.browser.append(ServiceBrowser(self.zeroconf, item, self))

    def __del__(self):
        self.zeroconf.close()

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Name: " + name)
        pprint.pprint(info)
        print("-----\n")

def main():
    listener = PrinterListener()

if __name__ == "__main__":
    main()
