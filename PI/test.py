import align

str1 = "abcdefgh"
str2 =  "cdeghabc"

(nseq1, nseq2, edits1, edits2, score, gaps) = align.NeedlemanWunsch(str1, str2, None, 0, 0)

print nseq1
print nseq2
