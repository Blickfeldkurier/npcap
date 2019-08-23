#! /usr/bin/env python3
import pprint
import argparse
import time
from zeroconf import ServiceBrowser, Zeroconf

class PrinterListener:
    """
    Gather and Store all Zeroconf packages
    """
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
            print("Added: " + item)
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
    parser = argparse.ArgumentParser(description='Get Network Printer Capabilities')
    parser.add_argument("-t", "--timeout", type=int, default=23,help="Timout for waiting on Zeroconf packages (Default:23)")
    args = parser.parse_args()

    listener = PrinterListener()
    wait = True
    lastTime = time.time()
    while wait:
        deltaT = time.time() - lastTime
        print(str(deltaT))
        if deltaT >= args.timeout:
            wait = False

if __name__ == "__main__":
    main()
