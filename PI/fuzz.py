
"""
Fuzz module
Generate fuzzing script

Written by Jennings Mao <maojianling@ict.ac.cn>
"""
import time
import fuzzModel
import json

class Fuzz:

    def __init__(self, sequences, protocol="ip", ip_p=0, port=0, output="test.json"):
        self.mtConsensus = []
        self.sequences = sequences
        self.json_result = {}
        self.protocol = protocol
        self.port = port
        # protocol value in ip header
        self.ip_p = ip_p
        self.output = output

        self.gen_json_template()
        self._go()

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
        self.json_result["test"]["session"]["target"]["ip_p"] = self.ip_p

        self.json_result["test"]["status"] = []
        self.json_result["test"]["status"].append({})

        # Only one status in default
        self.json_result["test"]["status"][0]["status_name"] = "DefaultStatus"
        self.json_result["test"]["status"][0]["blocks"] = []

    def _go(self):
        fm = fuzzModel.FuzzModel(self.sequences)
        if fm.has_length_field and fm.length_block_offset != 0:
            # 2 block
            b0 = {"block_name" : "b0", "block_item" : []}
            b1 = {"block_name" : "b1", "block_item" : []}
            for protocol_field in fm.protocol_fields:
                if protocol_field.offset < fm.length_block_offset:
                    b0["block_item"].append(self.gen_primitive_obj(protocol_field))
                else:
                    b1["block_item"].append(self.gen_primitive_obj(protocol_field))
            self.json_result["test"]["status"][0]["blocks"].append(b0)
            self.json_result["test"]["status"][0]["blocks"].append(b1)
        else:
            # 1 block
            b1 = {"block_name" : "b1", "block_item" : []}
            for protocol_field in fm.protocol_fields:
                b1["block_item"].append(self.gen_primitive_obj(protocol_field))
            self.json_result["test"]["status"][0]["blocks"].append(b1)

        with open(self.output, "w") as f:
            json.dump(self.json_result, f, ensure_ascii=False)
            print "Write json file completed!"

    @staticmethod
    def gen_primitive_obj(protocol_field):
        res = {}
        if protocol_field.primitive_type == "byte":
            res["primitive"] = [{
                "name" : "primitive-type",
                "type" : "static",
                "default_value" : "byte"
            }, {
                "name" : "primitive-value",
                "type" : "string",
                "default_value" : protocol_field.default_value
            }, {
                "name" : "fuzzable",
                "type" : "enum",
                "enum_list" : ["True", "False"],
                "default_value" : "True"
            }, {
                "name" : "width",
                "type" : "digit",
                "default_value" : protocol_field.length
            }, {
                "name" : "endian",
                "type" : "enum",
                "enum_list" : ["BIG_ENDIAN", "LITTLE_ENDIAN"],
                "default_value" : "BIG_ENDIAN"
            }, {
                "name" : "fuzzing-type",
                "type" : "enum",
                "enum_list" : ["exhaustive", "sampling"],
                "default_value" : "sampling"
            }]
        elif protocol_field.primitive_type == "static":
            res["primitive"] = [
                {
                    "name": "primitive-type",
                    "type": "static",
                    "default_value": "static"
                },
                {
                    "name": "primitive-value",
                    "type": "string",
                    "default_value": protocol_field.default_value
                },
                {
                    "name": "width",
                    "type": "static",
                    "default_value": protocol_field.length
                }
            ]
        elif protocol_field.primitive_type == "checksum":
            res["primitive"] = [
                {
                    "name": "primitive-type",
                    "type": "static",
                    "default_value": "checksum_field"
                },
                {
                    "name": "target-block",
                    "type": "static",
                    "default_value": "total"
                },
                {
                    "name": "checksum-algorithm",
                    "type": "static",
                    "default_value": protocol_field.checksum_type
                },
                {
                    "name": "width",
                    "type": "static",
                    "default_value": protocol_field.length
                }
            ]
        elif protocol_field.primitive_type == "length":
            res["primitive"] = [
                {
                    "name": "primitive-type",
                    "type": "static",
                    "default_value": "length_field"
                },
                {
                    "name": "target-block",
                    "type": "static",
                    "default_value": "b1"
                },
                {
                    "name": "width",
                    "type": "static",
                    "default_value": protocol_field.length
                }
            ]
        return res


