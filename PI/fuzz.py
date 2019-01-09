
"""
Fuzz module
Generate fuzzing script

Written by Jennings Mao <maojianling@ict.ac.cn>
"""
import time


class Fuzz:

    def __init__(self, sequences, protocol="ip", port=0):
        self.mtConsensus = []
        self.sequences = sequences
        self.json_result = {}
        self.gen_json_template()
        self.protocol = protocol
        self.port = port

    def gen_json_template(self):
        self.json_result["test"] = {}
        now = int(time.time()*1000)

        self.json_result["test"]["timestamp"] = now
        self.json_result["test"]["testname"] = "AutoScript"+str(now)
        self.json_result["test"]["description"] = "Autogen fuzzing script"

        self.json_result["test"]["session"] = {}
        self.json_result["test"]["session"]["target"] = {}
        # To be fixed by user
        self.json_result["test"]["session"]["target"]["ip"] = ""
        self.json_result["test"]["session"]["target"]["port"] = self.port
        self.json_result["test"]["session"]["target"]["protocol"] = self.protocol

        self.json_result["test"]["status"] = []
        self.json_result["test"]["status"][0] = {}

        # Only one status in default
        self.json_result["test"]["status"][0]["status_name"] = "DefaultStatus"
        self.json_result["test"]["status"][0]["blocks"] = []

    def _go(self):

        

        l = len(self.sequences[0][1])

        for j in range(0, l):
            column = []
            for id, seq in self.sequences:
                column.append(seq[j])
            dt = self._mutation_rate(column)
            self.mtConsensus.append(dt)



    @staticmethod
    def _mutation_rate(data):

        histogram = {}

        for x in data:
            try:
                histogram[x] += 1
            except:
                histogram[x] = 1

        items = histogram.items()
        items.sort()

        if len(items) == 1:
            rate = 0.0
        else:
            rate = len(items) * 1.0 / len(data) * 1.0

        return rate




from curses.ascii import *

class Output:

    def __init__(self, sequences):

        self.sequences = sequences
        self.consensus = []
        self._go()

    def _go(self):
        pass

class Ansi(Output):

    def __init__(self, sequences):

        # Color defaults for composition
        self.gap = "\033[41;30m%s\033[0m"
        self.printable = "\033[42;30m%s\033[0m"
        self.space = "\033[43;30m%s\033[0m"
        self.binary = "\033[44;30m%s\033[0m"
        self.zero = "\033[45;30m%s\033[0m"
        self.bit = "\033[46;30m%s\033[0m"
        self.default = "\033[47;30m%s\033[0m"

        Output.__init__(self, sequences)

    def _go(self):

        seqLength = len(self.sequences[0][1])
        rounds = seqLength / 18
        remainder = seqLength % 18
        l = len(self.sequences[0][1])

        start = 0
        end = 18

        dtConsensus = []
        mtConsensus = []

        for i in range(rounds):
            for id, seq in self.sequences:
                print "%04d" % id,
                for byte in seq[start:end]:
                    if byte == 256:
                        print self.gap % "___",
                    elif isspace(byte):
                        print self.space % "   ",
                    elif isprint(byte):
                        print self.printable % "x%02x" % byte,
                    elif byte == 0:
                        print self.zero % "x00",
                    else:
                        print self.default % "x%02x" % byte,
                print ""

            # Calculate datatype consensus

            print "DT  ",
            for j in range(start, end):
                column = []
                for id, seq in self.sequences:
                    column.append(seq[j])
                dt = self._dtConsensus(column)
                print dt,
                dtConsensus.append(dt)
            print ""

            print "MT  ",
            for j in range(start, end):
                column = []
                for id, seq in self.sequences:
                    column.append(seq[j])
                rate = self._mutationRate(column)
                print "%03d" % (rate * 100),
                mtConsensus.append(rate)
            print "\n"

            start += 18
            end += 18

        if remainder:
            for id, seq in self.sequences:
                print "%04d" % id,
                for byte in seq[start:start + remainder]:
                    if byte == 256:
                        print self.gap % "___",
                    elif isspace(byte):
                        print self.space % "   ",
                    elif isprint(byte):
                        print self.printable % "x%02x" % byte,
                    elif byte == 0:
                        print self.zero % "x00",
                    else:
                        print self.default % "x%02x" % byte,
                print ""

            print "DT  ",
            for j in range(start, start + remainder):
                column = []
                for id, seq in self.sequences:
                    column.append(seq[j])
                dt = self._dtConsensus(column)
                print dt,
                dtConsensus.append(dt)
            print ""

            print "MT  ",
            for j in range(start, start + remainder):
                column = []
                for id, seq in self.sequences:
                    column.append(seq[j])
                rate = self._mutationRate(column)
                mtConsensus.append(rate)
                print "%03d" % (rate * 100),
            print ""

        # Calculate consensus sequence
        l = len(self.sequences[0][1])

        for i in range(l):
            histogram = {}
            for id, seq in self.sequences:
                try:
                    histogram[seq[i]] += 1
                except:
                    histogram[seq[i]] = 1

            items = histogram.items()
            items.sort()

            m = 1
            v = 257
            for j in items:
                if j[1] > m:
                    m = j[1]
                    v = j[0]

            self.consensus.append(v)

            real = []

            for i in range(len(self.consensus)):
                if self.consensus[i] == 256:
                    continue
                real.append((self.consensus[i], dtConsensus[i], mtConsensus[i]))

        #
        # Display consensus data
        #
        totalLen = len(real)
        rounds = totalLen / 18
        remainder = totalLen % 18

        start = 0
        end = 18

        print "\nUngapped Consensus:"

        for i in range(rounds):
            print "CONS",
            for byte,type,rate in real[start:end]:
                if byte == 256:
                    print self.gap % "___",
                elif byte == 257:
                    print self.default % "???",
                elif isspace(byte):
                    print self.space % "   ",
                elif isprint(byte):
                    print self.printable % "x%02x" % byte,
                elif byte == 0:
                    print self.zero % "x00",
                else:
                    print self.default % "x%02x" % byte,
            print ""

            print "DT  ",
            for byte,type,rate in real[start:end]:
                print type,
            print ""

            print "MT  ",
            for byte,type,rate in real[start:end]:
                print "%03d" % (rate * 100),
            print "\n"

            start += 18
            end += 18

        if remainder:
            print "CONS",
            for byte,type,rate in real[start:start + remainder]:
                if byte == 256:
                    print self.gap % "___",
                elif byte == 257:
                    print self.default % "???",
                elif isspace(byte):
                    print self.space % "   ",
                elif isprint(byte):
                    print self.printable % "x%02x" % byte,
                elif byte == 0:
                    print self.zero % "x00",
                else:
                    print self.default % "x%02x" % byte,
            print ""

            print "DT  ",
            for byte,type,rate in real[start:end]:
                print type,
            print ""

            print "MT  ",
            for byte,type,rate in real[start:end]:
                print "%03d" % (rate * 100),
            print ""

    def _dtConsensus(self, data):
        histogram = {}

        for byte in data:
            if byte == 256:
                try:
                    histogram["G"] += 1
                except:
                    histogram["G"] = 1
            elif isspace(byte):
                try:
                    histogram["S"] += 1
                except:
                    histogram["S"] = 1
            elif isprint(byte):
                try:
                    histogram["A"] += 1
                except:
                    histogram["A"] = 1
            elif byte == 0:
                try:
                    histogram["Z"] += 1
                except:
                    histogram["Z"] = 1
            else:
                try:
                    histogram["B"] += 1
                except:
                    histogram["B"] = 1

        items = histogram.items()
        items.sort()

        m = 1
        v = '?'
        for j in items:
            if j[1] > m:
                m = j[1]
                v = j[0]

        return v * 3

    def _mutationRate(self, data):

        histogram = {}

        for x in data:
            try:
                histogram[x] += 1
            except:
                histogram[x] = 1

        items = histogram.items()
        items.sort()

        if len(items) == 1:
            rate = 0.0
        else:
            rate = len(items) * 1.0 / len(data) * 1.0

        return rate
