
# from PI import *
import PI.input as input
import PI.distance as distance
import PI.phylogeny as phylogeny
import PI.multialign as multialign
import PI.output as output
import PI.fuzz as fuzz
import PI.sumofpair as sp
import sys
import datetime
import argparse
import os
import json
import pcapy

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph", help="generate a phylogeny tree graph", action="store_true")
    parser.add_argument("--spscore", help="get sp socre of sequence", action="store_true")
    parser.add_argument("--html", help="whether output the HTML format (<br> instead of \\n)", action="store_true")
    parser.add_argument("--htmltemplate", help="The path of HTML template file")
    parser.add_argument("-w", "--weight", help="the weight for dividing clusters", type=float)
    parser.add_argument("-o", "--output_dir", help="the output dir name")
    parser.add_argument("input_file", help="input net trace file")
    args = parser.parse_args()

    weight = 1.0
    graph = False
    output_dir = "./output/test/"
    html_format = False
    html_templte_path = "./output/Template.html"

    if args.graph:
        graph = True
    if args.html:
        html_format = True

    if args.weight:
        weight = args.weight
        if weight < 0.0 or weight > 1.0:
            print "FATAL: Weight must be between 0 and 1"
            sys.exit(-1)
    if args.output_dir:
        output_dir = args.output_dir

    if args.htmltemplate:
        html_templte_path = args.htmltemplate

    input_file = args.input_file

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
    data = {}

    output_path = output_dir
    if os.path.exists(output_path):
        ls = os.listdir(output_path)
        for i in ls:
            c_path = os.path.join(output_path, i)
            if not os.path.isdir(c_path):
                os.remove(c_path)
    else:
        os.mkdir(output_path)
    i = 1
    for seqs in alist:
        cluster_name = "cluster_" + str(i)
        print "Generating "+cluster_name
        if not html_format:
            output.Ansi(seqs).go()
        else:
            output.Html(seqs).go()

        print "Sum of pairs: " + str(sp.get_sp_score(seqs))

        f = fuzz.Fuzz(seqs, protocol=sequences.protocol, ip_p=sequences.ip_p, port=sequences.port)

        target_json = output_path + "/" + cluster_name + ".json"
        data[cluster_name] = f.go()

        print target_json
        print data[cluster_name]
        with open(target_json, "w") as f:
            json.dump(data[cluster_name], f)
            # a = json.dumps(data[cluster_name], ensure_ascii=False).encode("utf-8")
            # f.write(a)

        i += 1
        print ""

    print "Write json file completed!"

    s = json.dumps(data)
    s = '<script type="text/javascript"> data=' + s + '</script>'

    if args.htmltemplate:
        with open(args.htmltemplate, "r") as f:
            s += f.read()
        with open(output_path+"/clusters.html", "w") as f:
            f.write(s)

        if html_format:
            print "<br><br>"
            print s


if __name__ == "__main__":
    now = datetime.datetime.now()
    main()
    end = datetime.datetime.now()
    print ("Running " + str(end-now))
