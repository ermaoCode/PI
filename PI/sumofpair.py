"""
calculate the SP(sum of pair) score of aligned sequence.
"""

def cmp_char(c1, c2):
    if c1 == 256 and c2 == 256:
        return 0
    if c1 == 256 and c2 != 256:
        return -2
    if c1 != 256 and c2 == 256:
        return -2

    if c1 == c2:
        return 2
    else:
        return -1


def get_sp_score(sequence):
    seq_num = len(sequence)
    max_seq_len = 0
    for i in range(seq_num):
        if len(sequence[i][1]) > max_seq_len:
            max_seq_len = len(sequence[i][1])

    # seq_len = len(sequence[0][1])
    SP_score = 0

    last_pos = [max_seq_len-1] * seq_num

    for i in range(seq_num):

        while last_pos[i] > 0:
            if len(sequence[i][1]) <= last_pos[i] or sequence[i][1][ last_pos[i] ] == 256:
                last_pos[i] -= 1
            else:
                break

    for col in range(max_seq_len):

        for i in range(seq_num):
            for j in range(seq_num):
                if i == j:
                    continue

                # ignore the "tail gap"
                if col > last_pos[i] or col > last_pos[j]:
                    continue

                SP_score += cmp_char(sequence[i][1][col], sequence[j][1][col])

    return SP_score