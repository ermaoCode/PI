import align

str1 = [8,0, 247, 166, 75, 130, 0,   1];
str2 = [8,0, 167, 210, 75, 130, 0,  12];

(nseq1, nseq2, edits1, edits2, score, gaps) = align.NeedlemanWunsch(str1, str2, None, 0, 0)

print nseq1
print nseq2
