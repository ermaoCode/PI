# -*- coding: utf-8 -*-
"""
A class represent fuzz model.

Including common fields, special fields(such as length field and checksum field)
Including a block layer.
Written by Jennings Mao <maojianling@ict.ac.cn>
"""
import  checksum
import struct

# offset : offset of this field
# length : length of this field
# primitive_type : primitive_type. including [static, byte, length, checksum]
# checksum_type : checksum algorithm, including [ipv4]
# length_block_offset : the target offset of checksum field
class ProtocolField:
    def __init__(self, offset, length, primitive_type, default_value, checksum_type=None, length_block_offset=0):
        self.offset = offset
        self.length = length
        self.primitive_type = primitive_type
        self.default_value = default_value
        self.checksum_type = checksum_type
        self.length_block_offset = length_block_offset

    def __cmp__(self, other):
        return cmp(self.offset, other.offset)


class FuzzModel:
    # origin_sequences: sequences without gap, be used for checksum
    def __init__(self, sequences_tuple):
        self.nums = len(sequences_tuple)
        self.sequences = []
        self.lens = [0] * self.nums
        i = 0
        for _, seq in sequences_tuple:
            self.sequences.append(seq)
            for v in seq:
                if v != 256:
                    self.lens[i] += 1
            i += 1

        # check whether length fixed
        self.is_fixed_length = True
        for i in range(self.nums - 1):
            if self.lens[i] != self.lens[i+1]:
                self.is_fixed_length = False
                break

        # mutation rate
        self.mtConsensus = []
        # most common value
        self.consensus = []
        self.protocol_fields = []

        self.protocol_len = len(self.sequences[0])
        self.occupied_field = [0]*self.protocol_len

        self.has_length_field = False
        self.length_block_offset = 0
        self.has_checksum_field = False

        self.parse_structure()

    def insert_fuzz_field(self, offset, length, primitive_type, default_value, checksum_type=None, length_block_offset=0):
        for i in range(offset, offset+length):
            if self.occupied_field[i] != 0:
                raise Exception("overlap fields!")
            else:
                self.occupied_field[i] = 1

        self.protocol_fields.append(ProtocolField(offset, length, primitive_type, default_value, checksum_type, length_block_offset))

    def parse_structure(self):
        seq_len = len(self.sequences[0])

        for j in range(0, seq_len):
            column = []
            for seq in self.sequences:
                column.append(seq[j])
            dt = self.mutation_rate(column)
            self.mtConsensus.append(dt)

        # calculate most common value (as the default value)
        for i in range(seq_len):
            histogram = {}
            for seq in self.sequences:
                if seq[i] in histogram.keys():
                    histogram[seq[i]] += 1
                else:
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

        # check length field
        length_field_index = -1
        offset = 0
        if not self.is_fixed_length:
            length_field_index, offset = self.find_linear_relationship()

        if length_field_index >= 0:
            self.has_length_field = True
            self.length_block_offset = offset

            if length_field_index>0 and self.mtConsensus[length_field_index-1] == 0 and \
                    self.sequences[0][length_field_index-1] == 0:
                # 2-byte length field
                length_field_index = length_field_index-1
                self.insert_fuzz_field(length_field_index, 2, "length", 0, length_block_offset=offset)
            else:
                self.insert_fuzz_field(length_field_index, 1, "length", 0, length_block_offset=offset)

        # find static field (mutate rate is 0)
        for i in range(self.protocol_len):
            if self.mtConsensus[i] == 0 and not self.occupied_field[i]:
                field_length = 1
                offset = i
                while i < self.protocol_len-1 and self.mtConsensus[i+1] == 0 and not self.occupied_field[i+1]:
                    field_length += 1
                    i += 1

                default_value = ""
                for j in range(field_length):
                    default_value += chr(self.sequences[0][offset+j])
                    # tmp = hex(self.consensus[offset+j])[2:]
                    # if len(tmp) == 1:
                    #     tmp = "0" + tmp
                    # default_value += "\x5cx"+tmp
                # default_value = struct.pack("<"+"B"*field_length, *self.sequences[0][offset:offset+field_length])

                self.insert_fuzz_field(offset, field_length, "static", default_value)

        # check checksum field
        # find 2-byte checksum field
        for i in range(self.protocol_len - 1):
            # checksum features: high mutation rates
            if self.mtConsensus[i] > 0.5 and self.mtConsensus[i+1] > 0.5 and not self.occupied_field[i] \
                    and not self.occupied_field[i+1]:
                # checksum_algorithms = ["ipv4", "crc32", "crc16"]
                if self.check_checksum_relationship("ipv4", i, 2):
                    self.has_checksum_field = True
                    self.insert_fuzz_field(i, 2, "checksum", 0, checksum_type="ipv4")
                # TODO: add other checksum identification

        # add remain fields
        for i in range(self.protocol_len):
            if not self.occupied_field[i]:
                field_length = 1
                offset = i
                while i < self.protocol_len-1 and not self.occupied_field[i+1]:
                    field_length += 1
                    i += 1

                default_value = ""
                for j in range(field_length):
                    if self.consensus[offset+j] == 256:
                        # gap
                        pass
                    elif self.consensus[offset+j] == 257:
                        # totally different
                        default_value += chr(0)
                    else:
                        default_value += chr(self.consensus[offset+j])
                        # # default_value += struct.pack("B", self.consensus[offset+j])
                        # tmp = hex(self.consensus[offset+j])[2:]
                        # if len(tmp) == 1:
                        #     tmp = "0" + tmp
                        # default_value += "\\x"+tmp

                self.insert_fuzz_field(offset, field_length, "byte", default_value)

        if not self.is_fixed_length:
            # if this is a not fixed length protocol,then we can add a random data
            max_length = 100
            default_value = 0
            self.protocol_fields.append(ProtocolField(self.protocol_len, max_length, "random", default_value))

        self.protocol_fields.sort()
        print "finish"

    # find 1-byte length field
    def find_linear_relationship(self):
        seq_len = len(self.sequences[0])
        seq_num = len(self.sequences)

        y = self.lens
        for i in range(seq_len):
            x = []
            for j in range(seq_num):
                x.append(self.sequences[j][i])
            if self.check_linear_relation(x, y):
                return i, y[0] - x[0]

        return -1, 0

    def check_checksum_relationship(self, checksum_type, checksum_offset, checksum_len):
        if checksum_type == "ipv4":
            # ipv4 checksum has nothing to do with position/offset
            return checksum.check_ipv4_checksum(self.sequences)

    @staticmethod
    # check if there exists a positive linear relationship such as y = x  + b
    def check_linear_relation(x, y):
        length = len(x)

        b = y[0] - x[0]

        for i in range(1, length):
            if b != y[i] - x[i]:
                return False

        return True



    @staticmethod
    def mutation_rate(data):

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