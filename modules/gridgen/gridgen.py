# gridgen.py
# Author: Quentin Goss
# Grid generator tool for generating variable sized grids

def main():
    options = get_options()
    if options.version:
        version_banner()
        return
    options = convert_speed(options)
    nodes = generate_nodes(options)
    edges = generate_edges(options,nodes)
    print()
    return

# Parse arguments from Command Line
def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--version', dest='version', action="store_true", default=False, help="Shows version information.")
    parser.add_option('-c', '--columns', dest='col', type='int', default=10, help="N Columns of nodes.")
    parser.add_option('-r', '--rows', dest='row', type='int', default=10, help="N Rows of nodes.")
    parser.add_option('--node_type', dest='node_type', type='string', default='priority', help='Node type.')
    parser.add_option('--node_dist', dest='node_dist', type='int', default=100, help='Distance between nodes.')
    parser.add_option('-l','--lanes', dest='lanes', type='int', default=1, help='# Lanes')
    parser.add_option('-s','--speed', dest='speed', type='float', default=25.0, help='Speed (m/s)')
    parser.add_option('--mph', dest='mph', action='store_true', default=False, help="Speed value is in mph instead of m/s")
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
        def __init__(self,_id,x,y,_type,pos):
            self._id = _id    # ID
            self.x = x        # x coordinate
            self.y = y        # y coordinate
            self._type = _type# Type
            self.pos = pos    # Position in grid (N E S W or C for center)
            return
        def summary(self):
            print('%7s %6s %6s %7s, %2s' % (self._id,self.x,self.y,self._type,self.pos))
            return
    nodes = []
    n = 1
    total = options.col * options.row
    for col in range(options.col):
        for row in range(options.row):
            _id = "%d_%d" % (col,row)
            x = "%d" % (options.node_dist * row)
            y = "%d" % (options.node_dist * col)
            _type = options.node_type
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
            nodes.append(node(_id,x,y,_type,pos))
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
            self._id = _id
            self._from = _from
            self.to = to
            self.priority = priority
            self.lanes = lanes
            self.speed = speed
            return
        def summary(self):
            return
    n = 1
    total = (options.row * options.col * 8) - (2 * options.row) - (2 * options.col)
    return

main()
