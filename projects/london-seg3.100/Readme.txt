THis is the london-seg3.100 project. It is a small dense section of Greatter London, United Kingdom centered around London. The map files are kept in "data" and the speed histograms for the edges are in "speedhist".\


>> About the speed histograms. <<

The speed histograms are stored in csv format in "speedhist\edges.stats.csv". A helper script is provided to load the speed histograms into a list of dictionaries. For use:

import load_edges from speedhist
edges = load_edges()
for e in edges:
    # Handle edges

>> About the grid <<

This map has been simplified into a grid of cells 100m x 100m in side. There are 75 columns and 75 rows. Some of the edges are combined. The .conn.csv file stores which edge ids were combined to each cell. This can be found at "data\london-seg3.100.conn.csv"



