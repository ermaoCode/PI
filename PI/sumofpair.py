"""
calculate the SP(sum of pair) score of aligned sequence.
"""

def cmp_char(c1, c2):
    if c1 == 256 and c2 == 256:
        return -2
    if c1 == 256 and c2 != 256:
        return -1
    if c1 != 256 and c2 == 256:
        return -1

    if c1 == c2:
        return 2
    else:
        return -1


def get_sp_score(sequence):
    seq_len = len(sequence[0][1])
    seq_num = len(sequence)
    SP_score = 0

    for col in range(seq_len):

        for i in range(seq_num):
            for j in range(seq_num):
                if i == j:
                    continue
                SP_score += cmp_char(sequence[i][1][col], sequence[j][1][col])

    return SP_score