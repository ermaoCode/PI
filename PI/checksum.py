# for checking checksum field
def ones_complement_sum_carry_16(a, b):
    """Compute ones complement sum and carry at 16 bits.

    :type a: int
    :type b: int

    :return: Sum of a and b, ones complement, carry at 16 bits.
    """
    pre_sum = a + b
    return (pre_sum & 0xffff) + (pre_sum >> 16)


def _collate_bytes(msb, lsb):
    """
    Helper function for our helper functions.
    Collates msb and lsb into one 16-bit value.

    :type msb: str
    :param msb: Single byte (most significant).

    :type lsb: str
    :param lsb: Single byte (least significant).

    :return: msb and lsb all together in one 16 bit value.
    """
    return (ord(msb) << 8) + ord(lsb)


def ipv4_checksum(msg):
    """
    Return IPv4 checksum of msg.
    :param msg: Message to compute checksum over.
    :type msg: bytes

    :return: IPv4 checksum of msg.
    :rtype: int
    """
    # Pad with 0 byte if needed
    if len(msg) % 2 == 1:
        msg += b"\x00"

    msg_words = map(_collate_bytes, msg[0::2], msg[1::2])
    total = reduce(ones_complement_sum_carry_16, msg_words, 0)
    return ~total & 0xffff


# sequences : [[int]]
def check_ipv4_checksum(sequences):
    for seq in sequences:
        msg = list(seq)
        while 256 in msg:
            msg.remove(256)

        if len(msg)%2 == 1:
            msg.append(0)

        msg_words = map(lambda x, y: (x << 8) + y, msg[0::2], msg[1::2])
        total = reduce(ones_complement_sum_carry_16, msg_words, 0)
        res = ~total & 0xffff
        if res != 0:
            return False

    return True

