
from PI import *
import sys, getopt
import datetime
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph", help="generate a phylogeny tree graph", action="store_true")
    parser.add_argument("-w", "--weight", help="the weight for dividing clusters", type=float)
    parser.add_argument("-o", "--output_file", help="the output json file")
    parser.add_argument("input_file", help="input net trace file")
    args = parser.parse_args()

    weight = 1.0
    graph = False
    output_file = "./test.json"

    if args.graph:
        graph = True
    if args.weight:
        weight = args.weight
        if weight < 0.0 or weight > 1.0:
            print "FATAL: Weight must be between 0 and 1"
        sys.exit(-1)
    if args.output_file:
        output_file = args.output_file

    input_file = args.input_file
    if not input_file:
        usage()

    print "Generating Fuzzing Script..."

    #
    # Open file and get sequences
    #
    try:
        sequences = input.Pcap(input_file)
    except:
        print "FATAL: Error opening '%s'" % input_file
        sys.exit(-1)

    if len(sequences) == 0:
        print "FATAL: No sequences found in '%s'" % input_file
        sys.exit(-1)
    else:
        print "Found %d unique sequences in '%s'" % (len(sequences), input_file)

    #
    # Create distance matrix (LocalAlignment, PairwiseIdentity, Entropic)
    #
    print "Creating distance matrix ..",
    dmx = distance.LocalAlignment(sequences)
    print "complete"

    #
    # Pass distance matrix to phylogenetic creation function
    #
    print "Creating phylogenetic tree ..",
    phylo = phylogeny.UPGMA(sequences, dmx, minval=weight)
    print "complete"

    #
    # Output some pretty graphs of each cluster
    #
    if graph:
        cnum = 1
        for cluster in phylo:
            out = "graph-%d" % cnum
            print "Creating %s .." % out,
            cluster.graph(out)
            print "complete"
            cnum += 1

    print "\nDiscovered %d clusters using a weight of %.02f" % \
        (len(phylo), weight)

    #
    # Perform progressive multiple alignment against clusters
    #
    i = 1
    alist = []
    for cluster in phylo:
        print "Performing multiple alignment on cluster %d .." % i,
        aligned = multialign.NeedlemanWunsch(cluster)
        print "complete"
        alist.append(aligned)
        i += 1
    print ""

    #
    # Display each cluster of aligned sequences
    #
    i = 1
    for seqs in alist:
        print "Generating cluster %d" % i
        output.Ansi(seqs)
        fuzz.Fuzz(seqs, protocol=sequences.protocol, ip_p=sequences.ip_p, port=sequences.port, output=output_file)
        i += 1
        print ""

if __name__ == "__main__":
    now = datetime.datetime.now()
    main()
    end = datetime.datetime.now()
    print ("Running " + str(end-now))
