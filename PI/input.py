
"""
Input module

Handle different input file types and digitize sequences

Written by Marshall Beddoe <mbeddoe@baselineresearch.net>
Copyright (c) 2004 Baseline Research

Licensed under the LGPL
"""

import pcapy
from socket import *
from sets   import *

__all__ = ["Input", "Pcap", "ASCII" ]

class Input:

    """Implementation of base input class"""

    def __init__(self, filename):
        """Import specified filename"""

        self.set = Set()
        self.sequences = []
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def next(self):
        if self.index == len(self.sequences):
            raise StopIteration

        self.index += 1

        return self.sequences[self.index - 1]

    def __len__(self):
        return len(self.sequences)

    def __repr__(self):
        return "%s" % self.sequences

    def __getitem__(self, index):
        return self.sequences[index]

class Pcap(Input):

    """Handle the pcap file format"""

    def __init__(self, filename, offset=14):
        Input.__init__(self, filename)
        self.pktNumber = 0
        self.offset = offset

        self.port = 0
        self.protocol = ""
        self.ip_p = 0

        try:
            pd = pcapy.open_offline(filename)
        except:
            raise IOError

        pd.dispatch(-1, self.handler)

    def handler(self, hdr, pkt):
        if hdr.getlen() <= 0:
            return


        # Ethernet is a safe assumption
        offset = self.offset

        # Parse IP header
        iphdr = pkt[offset:]

        ip_hl = ord(iphdr[0]) & 0x0f                    # header length
        ip_len = (ord(iphdr[2]) << 8) | ord(iphdr[3])   # total length
        self.ip_p = ord(iphdr[9])                            # protocol type
        ip_srcip = inet_ntoa(iphdr[12:16])              # source ip address
        ip_dstip = inet_ntoa(iphdr[16:20])              # dest ip address

        offset += (ip_hl * 4)
        self.protocol = "ip"

        # Parse TCP if applicable
        if self.ip_p == 6:
            tcphdr = pkt[offset:]

            th_sport = (ord(tcphdr[0]) << 8) | ord(tcphdr[1])   # source port
            th_dport = (ord(tcphdr[2]) << 8) | ord(tcphdr[3])   # dest port
            th_off = ord(tcphdr[12]) >> 4                       # tcp offset


            self.protocol = "tcp"
            # default system port is 1~1024
            # if th_dport <= 1024 and th_dport not in self.port:
            #     self.port.append(th_dport)
            # if th_sport <= 1024 and th_sport not in self.port:
            #     self.port.append(th_sport)
            if th_dport <= 1024 :
                self.port = th_dport

            offset += (th_off * 4)

        # Parse UDP if applicable
        elif self.ip_p == 17:
            udphdr = pkt[offset:]

            uh_sport = (ord(udphdr[0]) << 8) | ord(udphdr[1])   # source port
            uh_dport = (ord(udphdr[2]) << 8) | ord(udphdr[3])   # dest port

            self.protocol = "udp"
            # default system port is 1~1024
            # if uh_dport <= 1024 and uh_dport not in self.port:
            #     self.port.append(uh_dport)
            # if uh_sport <= 1024 and uh_sport not in self.port:
            #     self.port.append(uh_sport)
            if uh_dport <= 1024 :
                self.port = uh_dport
            offset += 8

        # Parse out application layer
        seq_len = (ip_len - offset) + 14

        if seq_len <= 0:
            return

        seq = pkt[offset:]

        l = len(self.set)
        self.set.add(seq)

        if len(self.set) == l:
            return

        # Digitize sequence
        digitalSeq = []
        for c in seq:
            digitalSeq.append(ord(c))

        self.sequences.append((self.pktNumber, digitalSeq))
        # Increment packet counter
        self.pktNumber += 1


class ASCII(Input):

    """Handle newline delimited ASCII input files"""

    def __init__(self, filename):
        Input.__init__(self, filename)

        try:
            fd = open(filename, "r")
        except:
            raise IOError

        lineno = 0

        while 1:
            lineno += 1
            line = fd.readline()

            if not line:
                break

            l = len(self.set)
            self.set.add(line)

            if len(self.set) == l:
                continue

            # Digitize sequence
            digitalSeq = []
            for c in line:
                digitalSeq.append(ord(c))

            self.sequences.append((lineno, digitalSeq))
