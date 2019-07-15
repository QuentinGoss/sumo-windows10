# speedhist.py
# Author: Quentin Goss
# A helper script for using the edges.stats.csv

# Load edge dictionaries from a CSV
# @param csv = filename where the csvs are stored
def load_edges(csv='edges.stats.csv'):
    edges = []; first = True
    with open(csv,'r') as f:
        for line in f:
            if first:
                first = False
                continue
            line = line.strip()
            data = line.split(',')
            edges.append(dict(ID=data[0],mean=float(data[1]),std=float(data[2]),p50=float(data[3]),p85=float(data[4])))
    return edges
test()
