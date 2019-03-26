
import numpy

# string seq1 : sequence 1
# string seq2 : sequence 2
# int    e    : Misplaced punishment
def NeedlemanWunsch(seq1, seq2,S, g, e):
    edits1 = []
    edits2 = []

    M = len(seq1) + 1
    N = len(seq2) + 1

    table = numpy.zeros([M, N], 'i')

    # Iterate through matrix and score similarities
    for i in range(1, M):
        for j in range(1, N):
            if seq1[i - 1] == seq2[j - 1]:
                table[i][j] = 1
            else:
                table[i][j] = 0

    # Sum the matrix
    i_max = 0
    j_max = 0
    t_max = 0

    for i in range(1, M):
        for j in range(1, N):
            v1 = table[i-1][j-1]
            v2 = table[i][j-1]
            v3 = table[i-1][j]

            if v1 > 255:
                v1 = v1 >> 8
            if v2 > 255:
                v2 = v2 >> 8
            if v3 > 255:
                v3 = v3 >> 8

            v1 = v1 + table[i][j] - position_punish(i,j)
            v2 = v2 - e
            v3 = v3 - e

            m = 0

            # direction: 1- left & up  2- left 4- up
            direction = 0

            if v1 > m:
                m = v1
                direction = 1

            if v2 > m:
                m = v2
                direction = 2

            if v3 > m:
                m = v3
                direction = 4
            #
            # if m == v1:
            #     direction = direction | (1 << 0)
            # elif m == v2:
            #     direction = direction | (1 << 1)
            # elif m == v3:
            #     direction = direction | (1 << 2)

            if m >= t_max:
                t_max = m
                i_max = i
                j_max = j

            m = m << 8
            m = m | direction

            table[i][j] = m

    # Do backtrace through matrix
    i = i_max
    j = j_max

    new_len = 0

    while i and j:
        data = table[i][j]
        ni = nj = 0

        if data & (1 << 2):
            ni = i - 1
            nj = j

        elif data & (1 << 1):
            ni = i
            nj = j - 1

        elif data & (1 << 0):
            ni = i - 1
            nj = j - 1

        new_len = new_len + 1

        i = ni
        j = nj

    new_seq1 = numpy.zeros((new_len), 'i')
    new_seq2 = numpy.zeros((new_len), 'i')

    s1 = s2 = new_len
    gaps = 0

    i = i_max
    j = j_max

    while i and j:
        data = table[i][j]
        ni = nj = 0

        if data & (1 << 2):
            ni = i - 1
            nj = j
            direction = (1 << 2)
            s1 = s1 - 1
            s2 = s2 - 1

            new_seq1[s1] = (seq1[i - 1])
            new_seq2[s2] = 256 # '_'
            edits2.append(s2)
            gaps = gaps + 1

        elif data & (1 << 1):
            ni = i
            nj = j - 1
            direction = (1 << 1)
            s1 = s1 - 1
            s2 = s2 - 1

            edits1.append(s1)
            new_seq1[s1] = 256 # '_'
            new_seq2[s2] = (seq2[j - 1])
            gaps = gaps + 1

        elif data & (1 << 0):
            ni = i - 1
            nj = j - 1
            direction = (1 << 0)
            s1 = s1 - 1
            s2 = s2 - 1
            new_seq1[s1] = (seq1[i - 1])
            new_seq2[s2] = (seq2[j - 1])


        # if direction == (1 << 0):
        #     s1 = s1 - 1
        #     s2 = s2 - 1
        #     new_seq1[s1] = (seq1[i - 1])
        #     new_seq2[s2] = (seq2[j - 1])

        # if direction == (1 << 1):
        #     s1 = s1 - 1
        #     s2 = s2 - 1
        #
        #     edits1.append(s1)
        #     new_seq1[s1] = 256 # '_'
        #     new_seq2[s2] = (seq2[j - 1])
        #     gaps = gaps + 1

        # if direction == (1 << 2):
        #     s1 = s1 - 1
        #     s2 = s2 - 1
        #
        #     new_seq1[s1] = (seq1[i - 1])
        #     new_seq2[s2] = 256 # '_'
        #     edits2.append(s2)
        #     gaps = gaps + 1

        i = ni
        j = nj

    return (new_seq1, new_seq2, edits1, edits2, t_max, gaps)

def SmithWaterman(seq1, seq2, S, g, e):

    # cdef int M, N, i, j, t_max, i_max, j_max, direction
    # cdef int v1, v2, v3, m, new_len, data, ni, nj

    # cdef int nrows, ncols
    # cdef x

    edits1 = []
    edits2 = []

    M = len(seq1) + 1
    N = len(seq2) + 1

    table = numpy.zeros([M, N], 'i')

    for i in range(M):
        table[i][0] = 0 - i

    for i in range(N):
        table[0][i] = 0 - i

    # matrix = <int *>table.data

    # Iterate through matrix and score similarities


    for i in range(1, M):
        for j in range(1, N):
            if seq1[i - 1] == seq2[j - 1]:
                table[i][j] = 2
            else:
                table[i][j] = -1

    # Sum the matrix
    i_max = 0
    j_max = 0
    t_max = 0

    for i in range(1, M):
        for j in range(1, N):

            direction = 0

            # v1 = matrix[(i - 1) * ncols + (j - 1)]
            # v2 = matrix[i * ncols + (j - 1)]
            # v3 = matrix[(i - 1) * ncols + j]
            v1 = table[i-1][j-1]
            v2 = table[i][j-1]
            v3 = table[i-1][j]

            if v1 > 255 or (v1 & 0xffffff00) == False:
                v1 = v1 >> 8
            if v2 > 255 or (v1 & 0xffffff00) == False:
                v2 = v2 >> 8
            if v3 > 255 or (v1 & 0xffffff00) == False:
                v3 = v3 >> 8

            v1 = v1 + table[i][j] - position_punish(i,j)
            v2 = v2 - 2
            v3 = v3 - 2

            if v1 > 0:
                m = v1
            else:
                m = 0

            if v2 > m:
                m = v2

            if v3 > m:
                m = v3

            if m == v1:
                direction = direction | (1 << 0)

            if m == v2:
                direction = direction | (1 << 1)

            if m == v3:
                direction = direction | (1 << 2)

            if m >= t_max:
                t_max = m
                i_max = i
                j_max = j

            m = m << 8
            m = m | direction

            table[i][j] = m

    # Do backtrace through matrix
    i = i_max
    j = j_max

    new_len = 0

    while table[i][j] > 0:
        data = table[i][j]

        if data & (1 << 2):
            ni = i - 1
            nj = j

        if data & (1 << 1):
            ni = i
            nj = j - 1

        if data & (1 << 0):
            ni = i - 1
            nj = j - 1

        new_len = new_len + 1

        i = ni
        j = nj

    new_seq1 = numpy.zeros((new_len), 'i')
    new_seq2 = numpy.zeros((new_len), 'i')

    s1 = s2 = new_len
    gaps = 0

    i = i_max
    j = j_max

    while table[i][j] > 0:
        data = table[i][j]

        if data & (1 << 2):
            ni = i - 1
            nj = j
            direction = (1 << 2)

        if data & (1 << 1):
            ni = i
            nj = j - 1
            direction = (1 << 1)

        if data & (1 << 0):
            ni = i - 1
            nj = j - 1
            direction = (1 << 0)

        if direction == (1 << 0):
            s1 = s1 - 1
            s2 = s2 - 1
            # new_seq1[s1] = ord(seq1[i - 1])
            # new_seq2[s2] = ord(seq2[j - 1])
            new_seq1[s1] = seq1[i - 1]
            new_seq2[s2] = seq2[j - 1]

        if direction == (1 << 1):
            s1 = s1 - 1
            s2 = s2 - 1

            edits1.append(s1)
            # new_seq1[s1] = 92 # '_'
            # new_seq2[s2] = ord(seq2[j - 1])
            new_seq1[s1] = 256 # '_'
            new_seq2[s2] = seq2[j - 1]
            gaps = gaps + 1

        if direction == (1 << 2):
            s1 = s1 - 1
            s2 = s2 - 1
            #
            # new_seq1[s1] = ord(seq1[i - 1])
            # new_seq2[s2] = 92 # '_'
            new_seq1[s1] = seq1[i - 1]
            new_seq2[s2] = 256 # '_'
            edits2.append(s2)
            gaps = gaps + 1

        i = ni
        j = nj

    return (new_seq1, new_seq2, edits1, edits2, t_max, gaps)


def position_punish(i, j):
    if i > j:
        return (i-j)/2
    return (j-i)/2