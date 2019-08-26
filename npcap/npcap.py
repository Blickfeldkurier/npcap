#! /usr/bin/env python3
import pprint
import argparse
import time
import ipaddress
import socket
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
            self.browser.append(ServiceBrowser(self.zeroconf, item, self))

    def __del__(self):
        self.zeroconf.close()

    def remove_service(self, zeroconf, type, name):
        pass

    def debugPrintMsg(self, name, info):
        print("Name: " + name)
        pprint.pprint(info)
        print("-----\n")
    
    def add_defaultValues(self, typestr, info):
        tmpDict = {}
        properties = info.properties
        server = info.server
        address = str(ipaddress.ip_address(info.address)) 
        if not address in self.packets:
            self.packets[address] = []
        tmpDict['type'] = typestr
        tmpDict['hostname'] = server
        tmpDict['port'] = str(info.port)
        if b'rp' in properties:
            tmpDict['rp'] = str(properties[b'rp'].decode())
        if b'ty' in properties:
            tmpDict['ty'] = str(properties[b'ty'].decode())
        if b'pdl' in properties:
            tmpDict['pdl'] = str(properties[b'pdl'].decode())
        if b'adminurl' in properties.keys():
            tmpDict['adminurl'] = properties[b'adminurl']
        self.packets[address].append(tmpDict)

    def add_ipp(self, name, info):
        self.add_defaultValues('_ipp._tcp.local.', info)
        
    def add_ipps(self, name, info):
        self.add_defaultValues('_ipps._tcp.local.', info)
    
    def add_printer(self, name, info):
        if info:
            self.add_defaultValues('_printer._tcp.local.', info)
    
    def add_pdl(self, name, info):
            self.add_defaultValues('_pdl-datastream._tcp.local.', info)
    
    def add_printcaps(self, name, info):
        self.add_defaultValues('_print_caps._tcp.local.', info)
    
    def printHosts(self, norev):
        for item in self.packets.keys():
            if norev == True:
                print(item)
            else:
                try:
                    host = socket.gethostbyaddr(item)
                    print(str(host[0]) + "/" + item)
                except socket.error:
                    print(item)

    def printSingleHost(self, ip, norev):
        if not ip in self.packets:
            return 
        if norev == True:
            print(ip)
        else:
            try:
               host = socket.gethostbyaddr(ip)
               print(str(host[0]) + "/" + ip)
            except socket.error:
                    print(ip)
            for typeitem in self.packets[ip]:
                for key, value in typeitem.items():
                    if key == "type":
                        print("\t" + value + ":")
                    else:
                        print("\t\t" + key + ": " + str(value))

    def printAll(self, norev):
        for ip, items in self.packets.items():
            if norev == True:
                print(ip)
            else:
                try:
                    host = socket.gethostbyaddr(ip)
                    print(str(host[0]) + "/" + ip)
                except socket.error:
                    print(ip)
            for typeitem in items:
                for key, value in typeitem.items():
                    if key == "type":
                        print("\t" + value + ":")
                    else:
                        print("\t\t" + key + ": " + str(value))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if type == "_ipp._tcp.local.":
            self.add_ipp(name, info)
        elif type == "_ipps._tcp.local.":
            self.add_ipps(name, info)
        elif type == "_printer._tcp.local.":
            self.add_printer(name, info)
        elif type == "_pdl-datastream._tcp.local.":
            self.add_pdl(name, info)
        elif type == "_print-caps._tcp.local.":
            self.add_printcaps(name, info)
        else:
            return

def main():
    parser = argparse.ArgumentParser(description='Get Network Printer Capabilities')
    parser.add_argument("-t", "--timeout", type=int, default=10,help="Timout for waiting on Zeroconf packages (Default:23)")
    parser.add_argument("-z", "--nozeroconf", default=False, action='store_true', help="Skip Zeroconf")
    parser.add_argument("-s", "--nosnmp", default=False, action='store_true', help="Skip SNMP")
    parser.add_argument("-l", "--list", default=False, action='store_true', help="List Zeroconf Hosts and Exit")
    parser.add_argument("-d", "--discover", default=False, action='store_true', help="Print capabilities of All Zeroconf hosts and Exit")
    parser.add_argument("-r", "--nolookup", default=False, action='store_true', help="No reverse lookup")
    parser.add_argument('addresses', nargs='*', help='List of Ip addresses to look up')
    args = parser.parse_args()

    listener = None
    if args.nozeroconf == False:
        listener = PrinterListener()
        wait = True
        lastTime = time.time()
        print("Waiting for Zeroconf Answers")
        while wait:
            deltaT = time.time() - lastTime
            if(deltaT % 1 == 0):
                print(str(deltaT) + "/" + str(args.timeout))
            if deltaT >= args.timeout:
                wait = False
    print("[Done]\n")
    print("Reslults: ")
    if args.list == True:
        if listener:
            listener.printHosts(args.nolookup)
        exit()

    if args.discover == True:
        if listener:
            listener.printAll(args.nolookup)
        exit()
    
    if args.addresses:
        for item in args.addresses:
            if listener:
                host = socket.gethostbyname(item)
                listener.printSingleHost(host, args.nolookup)
    else:
        if listener:
            listener.printAll(args.nolookup)
        else:
            print("No address given and no-zeroconf flag set. Can't do a thing")

if __name__ == "__main__":
    main()
