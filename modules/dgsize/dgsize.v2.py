# dgsize version 2
# Author: Quentin Goss
# Last Modified: 02/09/2019
# Counts the amount of vertices in a directed graph
#
# Updated for k-means clustered jsons

def main():
    options = get_options()
    n_vertices = 0
    n_edges = 0
    if not options.file_vertex == None:
        n_vertices = count_vertices(options.file_vertex)
    if not options.file_edge == None:
        n_edges = count_edges(options.file_edge)
    print('v={' + str(n_vertices) + '}e={' + str(n_edges) + '}') 
# end def main

def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-v', '--vertex_file', type="string", dest='file_vertex', default=None, help='File containing vertex JSONS')
    parser.add_option('-e', '--edge_file', type='string', dest='file_edge', default=None, help='File containing edge JSONS.')
    #parser.add_option('-n', type='int', dest='n', default=None, help='The amount of : in a json object')
    
    #args = ['-v',"C:\\flpoly\\Fall 2018\\Scientific Computing and Programming\\Final_Project\\jsons\\3choices\\junctions.json",'-e',"C:\\flpoly\\Fall 2018\\Scientific Computing and Programming\\Final_Project\\jsons\\3choices\\edges.json"]
    #(options, args) = parser.parse_args(args)
    (options,args) = parser.parse_args()

    return options
# end def get_options

# Counts the amount of vertices in a given file
#
# @param file_vertex <- File which contains vertices
# @param n <- # : in an object
def count_vertices(file_vertex,n=4):
    with open(file_vertex,'r') as vf:
        n_vertices = 0
        for line in vf:
            n_vertices += line.count(':')
        n_vertices = int(n_vertices / n)
        return(n_vertices)
# end def count_vertices

# Counts the amount of edges in a given file
#
# @param file_edge <- File which contains edges
# @param n <- @ : in an object
def count_edges(file_edge,n=7):
    with open(file_edge,'r') as ef:
        n_edges = 0
        for line in ef:
            n_edges += line.count(':')
        n_edges = int(n_edges / n)
        return(n_edges)
# end def count_edges

main()
