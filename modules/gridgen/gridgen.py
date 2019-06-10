# gridgen.py
# Author: Quentin Goss
# Grid generator tool for generating variable sized grids
import os

def main():
    options = get_options()
    if options.version:
        version_banner()
        return
    options = convert_speed(options)
    nodes = generate_nodes(options)
    print()
    edges = generate_edges(options,nodes)
    print()
    
    os.system('mkdir temp')
    
    write_nod_xml(nodes)
    print()
    write_edg_xml(edges)
    print()
    os.system("netconvert --node-files=./temp/grid.nod.xml --edge-files=./temp/grid.edg.xml --output-file=./temp/grid.net.xml")
    print('Moving files.')
    os.system('mkdir "%s"' % (options.output_dir))
    os.system('move .\\temp\\*.* %s' % (options.output_dir))
    os.system('rmdir temp')
    print("Complete!")
    return

# Parse arguments from Command Line
def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--version', dest='version', action="store_true", default=False, help="Shows version information.")
    parser.add_option('-c', '--columns', dest='col', type='int', default=10, help="N Columns of nodes.")
    parser.add_option('-r', '--rows', dest='row', type='int', default=10, help="N Rows of nodes.")
    parser.add_option('--node_type', dest='node_type', type='string', default='priority', help='Node type.')
    parser.add_option('--node_distance', dest='node_dist', type='int', default=100, help='Distance between nodes.')
    parser.add_option('-l','--lanes', dest='lanes', type='int', default=1, help='# Lanes')
    parser.add_option('-s','--speed', dest='speed', type='float', default=25.0, help='Speed (m/s)')
    parser.add_option('--mph', dest='mph', action='store_true', default=False, help="Speed value is in mph instead of m/s")
    parser.add_option('-o','--output_dir', dest='output_dir', type='string', default='./grid', help='The destination of the script output.')
    (options,args) = parser.parse_args()
    return options

# Version Banner
def version_banner():
    print("~~ Grid Generator ~~")
    print("  Version Alpha")
    print("  Author: Quentin Goss")
    print("  Generates an X by Y dimension grid with 8 degrees of movement.")
    return

# Converts to mph is flag is set
# @param options = command line arguments
# @return updated options
def convert_speed(options):
    if options.mph:
        options.speed = options.speed * 0.44704
    return options
 
# Generates the Nodes
# @param options = command line arguments
# @return List of Nodes
def generate_nodes(options):
    class node:
        def __init__(self,_id,x,y,_type,pos,col,row):
            self._id = _id    # ID cell{col}_{row}
            self.x = x        # x coordinate
            self.y = y        # y coordinate
            self._type = _type# Type
            self.pos = pos    # Position in grid (N E S W or C for center)
            self.row = row    # Position in row
            self.col = col    # Position in col
            return
        def summary(self):
            print('%7s %6s %6s %7s, %2s' % (self._id,self.x,self.y,self._type,self.pos))
            return
    nodes = [] # Holds Nodes
    # Counter for update
    n = 1; total = options.col * options.row
    for col in range(options.col):
        for row in range(options.row):
            _id = "cell%d_%d" % (col,row)
            x = "%d" % (options.node_dist * row)
            y = "%d" % (options.node_dist * col)
            _type = options.node_type
            
            # Assign Position in the grid
            # (Will be used to determine number of edges later.)
            pos = 'C'
            if col == 0 and row == 0:
                pos = 'SW'
            elif col == (options.col - 1) and row == 0:
                pos = 'NW'
            elif col == 0 and row ==(options.row - 1):
                pos = 'SE'
            elif col == (options.col - 1) and row == (options.row - 1):
                pos = 'NE'
            elif col == 0:
                pos = 'S'
            elif col == (options.col - 1):
                pos = 'N'
            elif row == 0:
                pos = 'W'
            elif row == (options.row - 1):
                pos = 'E'
            nodes.append(node(_id,x,y,_type,pos,col,row))

            # Update
            print('Generating Nodes %6.2f%%' % (float(n)/float(total) * 100),end='\r')
            n += 1
            continue
        continue
    return nodes
    
# Generate Edges
# @param options = command line arguments
# @param nodes = list of nodes
# @param edges = list of edges
def generate_edges(options,nodes):
    class edge:
        def __init__(self,_id, _from, to, priority, lanes, speed):
            self._id = _id          # ID of this edge
            self._from = _from      # ID of starting Node
            self.to = to            # ID of ending Node
            self.priority = str(priority)# Priority
            self.lanes = str(lanes) # Number of lanes
            self.speed = str(speed) # Speed of edge
            return
        def summary(self):
            print('%7s %7s %7s %1s %1s %7s' % (self._id, self._from, self.to, self.priority, self.lanes, self.speed))
            return
    # Counter for update
    n = 1; total = len(nodes)
    
    n_edges = 0 # Edge counter
    edges = []  # Holds edges
    for node in nodes:
        col, row = parse_col_row(node._id)
        
        # Down Left
        #if not ('S' in node.pos or 'W' in node.pos):
        if (col - 1) >= 0 and (row - 1) >= 0:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col -1, row - 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
        
        # Up Left
        #if not ('N' in node.pos or 'W' in node.pos):
        if (col - 1) >= 0 and (row + 1) < options.row:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col - 1, row + 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
        
        # Down Right
        #if not ('S' in node.pos or 'E' in node.pos):
        if (col + 1) < options.col and (row - 1) >= 0:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col + 1, row - 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
            
        # Up Right
        #if not ('N' in node.pos or 'E' in node.pos):
        if (col + 1) < options.col and (row + 1) < options.row:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col + 1, row + 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
            
        # Up
        #if not 'N' in node.pos:
        if (row + 1) < options.row:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col, row + 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
            
        # Right
        #if not 'E' in node.pos:
        if (col + 1) < options.col:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col + 1, row)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
            
        # Left
        #if not 'W' in node.pos:
        if (col - 1) >= 0:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col - 1, row)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1
            
        # Down
        #if not 'S' in node.pos:
        if (row - 1) >= 0:
            _id = 'edge%d' % (n_edges)
            to = 'cell%d_%d' % (col, row - 1)
            edges.append(edge(_id,node._id,to,1,options.lanes,options.speed))
            n_edges += 1

        # Update
        print('Generating Edges %6.2f%%' % (float(n)/float(total)*100),end='\r')
        n += 1
        continue
    return edges
    
# Parses the column and row from a node_id
# @param node_id = node ID
# @return [col,row] as integers
def parse_col_row(node_id):
    node_id = node_id[len('cell'):]
    ls_col_row = node_id.split('_')
    return [int(ls_col_row[0]),int(ls_col_row[1])]

# Writes the grid.nod.xml file
# @param nodes = list of nodes
def write_nod_xml(nodes):
    banner = "<!--\n"
    banner += "\tThis code was autogenerated using gridgen.py\n"""
    banner += "\tTotal Nodes = %d\n" % (len(nodes))
    banner += "-->\n"
    with open('./temp/grid.nod.xml','w') as xml:
        xml.write(banner)
        xml.write('<nodes>\n')
        
        # Update tracking
        n = 1; total = len(nodes)
        for node in nodes:
            xml.write('\t<node id="%s" x="%s" y="%s" type="%s"/>\n' % (node._id,node.x,node.y,node._type))
            
            # Update
            print('Writing grid.nod.xml %6.2f%%' % (float(n)/float(total)*100),end='\r')
            n += 1
            continue
            
        xml.write('</nodes>')
    return

# Writes the grid.edg.xml file
# @param edges = list of edges
def write_edg_xml(edges):
    banner = "<!--\n"
    banner += "\tThis code was autogenerated using gridgen.py\n"""
    banner += "\tTotal Edges = %d\n" % (len(edges))
    banner += "-->\n"
    with open('./temp/grid.edg.xml','w') as xml:
        xml.write(banner)
        xml.write('<edges>\n')
        
        # update tracking
        n = 1; total = len(edges)
        for edge in edges:
            xml.write('\t<edge id="%s" from="%s" to="%s" priority="%s" numLanes="%s" speed="%s"/>\n' % (edge._id, edge._from, edge.to, edge.priority, edge.lanes, edge.speed))
            
            # Update
            print('Writing grid.edg.xml %6.2f%%' % (float(n)/float(total)*100),end='\r')
            n += 1
            continue
        
        xml.write('</edges>')
    return

main()
