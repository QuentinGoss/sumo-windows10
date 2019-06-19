# reduce2grid.py
# Author: Quentin Goss
# Reduces a SUMO map to a simpler grid
import xml.etree.ElementTree as ET
import sys
import os
from bresenham import bresenham # Line tracking Algorithm

def main():
    options = get_options()
    if options.version: version_banner(); sys.exit()
    options = convert_speed(options)
    options = concat_name_cell_dim(options)
    global GRID; GRID = init_grid(options)
    navigate_edg_xml(options)
    os.system('MKDIR temp')
    write_nod_xml(options)
    write_edg_xml(options)
    os.system("netconvert --node-files=./temp/%s.nod.xml --edge-files=./temp/%s.edg.xml --output-file=./temp/%s.net.xml --verbose" % (options.name,options.name,options.name))
    write_sumocfg_rou_settings(options)
    move_files(options)
    print('Complete!')
    return

# Parse arguments from Command Line
def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--version', dest='version', action="store_true", default=False, help="Shows version information.")
    parser.add_option('-e','--edg.xml', dest='edg_xml', type='string', default=None, help='*.edg.xml file.')
    parser.add_option('-n','--nod.xml', dest='nod_xml', type='string',default=None, help='*.nod.xml file.')
    parser.add_option('-x','--center.xy', dest='center_xy', type='string', default=None, help='Center coords of grid. #.##,#.##')
    parser.add_option('-d', '--cell.dimension', dest='cell_dim', type='int', default=100, help='Cell dimensions Height/Width')
    parser.add_option('-H','--window.height', dest='window_height', type='int', default=None, help='Window height.')
    parser.add_option('-W','--window.width', dest='window_width', type='int', default=None, help='Window width')
    parser.add_option('--node_type', dest='node_type', type='string', default='priority', help='Node type.')
    parser.add_option('-l','--lanes', dest='lanes', type='int', default=1, help='# Lanes')
    parser.add_option('-s','--speed', dest='speed', type='float', default=25.0, help='Speed (m/s)')
    parser.add_option('--mph', dest='mph', action='store_true', default=False, help="Speed value is in mph instead of m/s")
    parser.add_option('-p','--name', dest='name', type='string', default=None, help='Name of output files.')
    parser.add_option('-o','--output.dir', dest='output_dir', type='string', default='map', help='The destination of the script output.')
    
    #
    (options,args) = parser.parse_args()
    validate_options(options)
    return options

# Validate Options
def validate_options(options):
    if options.edg_xml == None:
        print('No *.edg.xml file specified.')
        sys.exit()
    elif options.nod_xml == None:
        print('No *.nod.xml file specified.')
        sys.exit()
    elif options.center_xy == None:
        print('No center.xy coordinate specified.')
        sys.exit()
    elif not (options.center_xy.count('.') == 2) or not (options.center_xy.count(',') == 1):
        print('Invalid center.xy coordinates.')
        print('You entered: %s' % (options.center_xy))
        print('Right click -> Copy Cursor Position\nSomething like 568.47,399.78 is the Result')
        sys.exit()
    elif options.window_height == None:
        print('Must specify window height with --window.height')
        sys.exit()
    elif options.window_width == None:
        print('Must specifiy window width with --window.width')
        sys.exit()
    elif options.name == None:
        print('Must specify a name with -p or --name. (i.e --name=myname)')
        sys.exit()
    return

# Version Banner
def version_banner():
    print("~~ Reduce Map to Grid Tool ~~")
    print("  Version Alpha")
    print("  Author: Quentin Goss")
    print("  Simplifies a map by generalizing it into an grid with 8 directions.")
    print("  In this version, Lane, Speed, Priority, and Type information is lost.")
    return

# Converts to mph is flag is set
# @param options = command line arguments
# @return updated options
def convert_speed(options):
    if options.mph:
        options.speed = options.speed * 0.44704
    return options
    
# Navigate edg_xml
# @param options = command line arguments
def navigate_edg_xml(options):
    # XML file loading
    tree = ET.parse(options.edg_xml)
    root = tree.getroot()
    
    # Determine how much work will be done
    n_allowed = find_n_allowed(root); n = 0
        
    # Iterate through all edge tags.
    for edge in root.findall('edge'):
        # Check if passenger vehicles are allowed on the edge
        if not (check_if_passable(edge,"passenger")):
            continue
        
        # Does the edge have a shape?
        # Yes - Determine if the edge leaves the cell using the shape
        if xml_has_atrribute(edge,'shape'):
            child_edges = breakdown_shape(edge.attrib['shape'])
            # For each child edge...
            for x0y0x1y1 in child_edges:
                # Add connections in the grid
                p_from = Point(x0y0x1y1[0],x0y0x1y1[1]) # x0y0
                p_to = Point(x0y0x1y1[2],x0y0x1y1[3])   # x1y1
                add_connection(p_from,p_to)
                continue
            
        # No - This shape is a line between two nodes
        # Lookup the nodes and use the node coordinates
        else:
            if xml_has_atrribute(edge,'from') and xml_has_atrribute(edge,'to'):
                # Add connection to the grid
                x0,y0 = lookup_node_xy(options,edge.attrib['from'])
                x1,y1 = lookup_node_xy(options,edge.attrib['to'])
                p_from = Point(x0,y0); p_to = Point(x1,y1);
                add_connection(p_from,p_to)
                
        # Update
        n += 1
        print('Progress %6.2f%%' % (float(n)/float(n_allowed)*100),end='\r')
        continue
    print()
    return

# Performs one iteration of the *.edg.xml to determine the number of
# passable nodes to be checked
# @param ElementTree-xml-object root = contains xml tags
# @return int = Number of passable nodes that will be used in the
#   smplification process
def find_n_allowed(root):
    # statistics tracking
    n_allowed = 0
    n_disallowed = 0
    
    # Iterate through all edge tags.
    for edge in root.findall('edge'):
        # Check if passenger vehicles are allowed on the edge
        if (check_if_passable(edge,"passenger")):
            n_allowed += 1
        else:
            n_disallowed += 1
            continue
    print("Allowed %d Disallowed %d" % (n_allowed,n_disallowed))
    return n_allowed

# Checks if an edge is passable by a vehicle type.
# @param ElementTree-xml-object edge = edge xml tag
# @param string veh_type = Vehicle Type
# @return True if passable, False otherwise
def check_if_passable(edge,veh_type):
    # Check inside the allow attribute
    try:
        if veh_type in edge.attrib['allow']:
            return True
        else:
            return False
    except:
        pass
    
    # Check inside the disallow attribute
    try:
        if not veh_type in edge.attrib['disallow']:
            return True
        else:
            return False
    except:
        pass
        
    # If it isn't allowed or dissallowed then we assume it
    # to be allowed
    return True

# Checks if a given xml object has an attribute
# @param ElementTree-xml-object xml = xml tag
# @param string attrib =  attribute to check the existence of
# @return True if exists, False otherwise
def xml_has_atrribute(xml,attrib):
    try:
        len(xml.attrib[attrib])
        return True
    except:
        pass
    return False

# Looks up a node_id in the *.nod.xml file.
# @param options = Command Line Arguments
# @param string = Node ID
# @return (x,y) = x y coordinates of the Node
def lookup_node_xy(options,node_id):
    # XML File Loading
    tree = ET.parse(options.nod_xml)
    root = tree.getroot()
    
    # Nagivate through the file to find the node
    # ** SLOW OPERATION - Can be improved **
    for node in root.findall('node'):
        #print(xml_has_atrribute(node,'id'),node.attrib['id'])
        if xml_has_atrribute(node,'id') and node.attrib['id'] == node_id:
            return (float(node.attrib['x']),float(node.attrib['y']))
    raise('Node ID %s not found' % (node_id))

# Returns a list of individual child-edges given the shape of a large edge
# @param string shape = coordinates of the node shape in string format.
# @return list of (x0,y0,x1,y1) of from->to pairs
def breakdown_shape(shape):
    xypairs = shape.split(' ')
    n = 0; child_edges = []
    while not (n + 1 == len(xypairs)):
        x0,y0 = xystring2float(xypairs[n])
        x1,y1 = xystring2float(xypairs[n+1])
        child_edges.append((x0,y0,x1,y1))
        n += 1 #lcv
        continue
    return child_edges
    
# Translates an xy string to (x,y) coordinates
#
# Right click -> Copy Cursor Position
# Something like 568.47,399.78 is the Result
#
# @param string s_xy = coordinates in string format
# @return (x,y) =  x,y coordinates as a tuple of floats
def xystring2float(s_xy):
    ls_xy = s_xy.split(',')
    return (float(ls_xy[0]),float(ls_xy[1]))

# Grid Classes
class Point(object):
    def __init__(self,x,y):
        self.x = x # float(x coordinate)
        self.y = y # float(y coordinate)

class Cell_Index(object):
    def __init__(self,col,row):
        self.col = col # int(col)
        self.row = row # int(row)

class Connection(object):
    def __init__(self,ifrom,ito):
        self.ifrom = ifrom  # Cell_Index of from Cell
        self.ito = ito      # Cell_Index of to Cell
        self.weight = 1     # Weight
        
    # Checks if a connection already exists
    def compare(self,ifrom,ito):
        if (ifrom.col == self.ifrom.col) and (ito.col == self.ito.col) and (ifrom.row == self.ifrom.row) and (ito.row == self.ito.row):
            return True
        return False

class Cell(object):
    def __init__(self,index,center):
        self.index = index   # Cell_Index(col,row)
        self.center = center # Point(x,y)
        self.connections = [] # Conections between this to another edge

# Initializes the grid and creates the cell objects
# Uses the center point and the grid height/width
# +------------------+
# |                  |
# |         +        | window.height
# |     center.xy    |
# +------------------+
#     window.width
#
# +--+--+--+
# |  |  |  | cell.dimension
# +--+--+--+
# |  |  |  |
# +--+--+--+
#
# Top Left Corner
# +-------> x+
# |  
# | y-
# V
#
# @param options = command line arguments
# @return grid = Empty grid with 
def init_grid(options):
    print('Initializing grid...',end='')
    class grid:
        center = None       # Center Point()
        top_left = None     # Top Left Corner Point()
        bottom_right = None # Bottom Right Corner Point()
        cells = None        # Cells [col][row]
        ncols = None        # Number of columns
        nrow = None         # Number of rows
        cell_dim = options.cell_dim     # Cell Dimension
        height = options.window_height  # Height of Grid
        width = options.window_width    # Width of Grid
        anomalies = 0       # Statistics
        
    # Center Point
    x,y = xystring2float(options.center_xy)
    grid.center = Point(x,y)
    
    # Top Left Corner
    grid.top_left = Point(x - options.window_width / 2, y + options.window_height / 2)
    
    # Bottom Right Corner
    grid.bottom_right = Point(x + options.window_width / 2, y - options.window_height / 2)
    
    # Initialize Control Variables for the loop ahead
    icol = 0; irow = 0; col = [];
    half_cell_dim = options.cell_dim / 2
    init_x = grid.top_left.x + half_cell_dim
    x = init_x; y = grid.top_left.y - half_cell_dim 
    
    # Create Cells Until Cells occupy the entire window
    while y >= grid.bottom_right.y:
        # Clean out the row list
        row = []
        
        # Fill out the rows
        while x <= grid.bottom_right.x:
            cell = Cell(Cell_Index(icol,irow),Point(x,y))
            row.append(cell); x += options.cell_dim; irow += 1
            continue
        
        # Row is filled out, append the row and reset x
        col.append(row); x = init_x; irow = 0
        
        # Update y
        y -= options.cell_dim; icol += 1
        continue
    
    # Clean up 
    grid.cells = col; grid.ncols = len(col); grid.nrows = len(row)
    del col, row
    print('COMPLETE!')
    return grid

# Adds a connection between two points in the grid
# @param Point p_from = beginning of edge
# @param Point p_to = end of edge
def add_connection(p_from,p_to):
    # Do the points exist in the grid?
    if not (is_point_in_grid(p_from) and is_point_in_grid(p_to)):
        return # Point doesn't exist. It doesn't matter
        
    # Determine the index of the cell
    ifrom = point2icell(p_from)
    ito = point2icell(p_to)
    
    # Does the point go to itself?
    if (p_from.x == p_to.x) and (p_from.y == p_to.y):
        return # No need to draw a line to itself.
    
    # Is this connection anomalmous?
    if check4anomaly(ifrom,ito):
        GRID.anomalies += 1
        # Subdivide the connection
        child_connections = breakdown_anomaly(ifrom,ito)
        # Add each connection individually
        for conn in child_connections:
            ifrom = conn[0]; ito = conn[1]
            validate_and_add_connection(ifrom,ito)
            continue
    
    # Not anomalous. Validate
    else:
        validate_and_add_connection(ifrom,ito)
    
    return

# Validates and adds a connection if possible,
#  given ifrom and ito
# @param Cell_Index ifrom = Cell index of start
# @param Cell_Index ito = Cell index of end
def validate_and_add_connection(ifrom,ito):
    # Grab Cell
    cell = GRID.cells[ifrom.col][ifrom.row]
    
    # First connection in this cell
    if len(cell.connections) == 0:
        cell.connections.append(Connection(ifrom,ito))
        
    # See if a connection exists
    else:
        found = False
        for conn in cell.connections:
            if conn.compare(ifrom,ito):
                conn.weight += 1; found = True
                break
            continue
        if not found:
            cell.connections.append(Connection(ifrom,ito))
            
    # Update Cell
    GRID.cells[ifrom.col][ifrom.row] = cell
    return

# Checks if a given point exists within the grid
# @param Point xy = any point
# @return True if the point exists, False otherwise
def is_point_in_grid(xy):
    return ((xy.x >= GRID.top_left.x) and (xy.x <= GRID.bottom_right.x) and (xy.y <= GRID.top_left.y) and (xy.y >= GRID.bottom_right.y))

# Translares a Point to a Cell_Index
# @param Point xy = any point
# @return Cell_Index
def point2icell(xy):
    xy = pos_in_grid(xy)
    col = int(xy.y / GRID.cell_dim)
    row = int(xy.x / GRID.cell_dim)
    row = GRID.nrows - 1 - row
    return Cell_Index(col,row)

# Gets the position of a point in relation to the grid window
# @param Point xy = any point
# @return Point = position in the grid window
def pos_in_grid(xy):
    return Point(GRID.bottom_right.x - xy.x,GRID.top_left.y - xy.y)

# Checks for connections that are anomolous
#  Each edge should only travel 1 cell away at a time
# o o o         o
#  \|/  OKAY!  /
# o-o-o       o
#  /|\        |\
# o o o       o \  <-- NOT OKAY!!
#                o
# @return True if this anomoly is detected.
def check4anomaly(ifrom,ito):
    if (abs(ifrom.col - ito.col) > 1) or (abs(ifrom.row - ito.row) > 1):
        return True
    return False

# Breaks up anomalous roads into incremental roads
#  using the Bresenham Line Algorithm
# @param Cell_Index ifrom = starting index
# @param Cell_Index ito = ending index
# @return tuple of one-increment Cell_Index pairs
def breakdown_anomaly(ifrom,ito):
    middle_edges = list(bresenham(ifrom.col,ifrom.row,ito.col,ito.row))
    
    # Loop Control Variables
    n = 0; child_connections = []
    while not (n + 1 == len(middle_edges)):
        ifrom = Cell_Index(middle_edges[n][0],middle_edges[n][1])
        ito = Cell_Index(middle_edges[n+1][0],middle_edges[n+1][1])
        child_connections.append((ifrom,ito))
        n += 1 # LCV
        continue
        
    return child_connections

# Write the nod.xml file
# @param options = Command line arguments
def write_nod_xml(options):
    # Statistics tracking
    n = 1; total = GRID.ncols * GRID.nrows
    
    # Write to file
    with open('./temp/%s.nod.xml' % (options.name),'w') as xml:
        xml.write('<nodes>\n')
        for col in GRID.cells:
            for cell in col:
                xml.write('\t<node id="cell%d_%d" x="%f" y="%f" type="%s"/>\n' % (cell.index.col,cell.index.row,cell.center.x,cell.center.y,options.node_type))
                
                # Update
                print('Writing grid.nod.xml %6.2f%%' % (float(n)/float(total)*100),end='\r')
                n += 1
                continue
            continue
        xml.write('</nodes>')
        print()
    return

# Write the edg.xml file
# @param options = Command line arguments
def write_edg_xml(options):
    # Statistics tracking
    n = 1; total = GRID.ncols * GRID.nrows; n_conn = 0
    
    # Write to File
    with open('./temp/%s.edg.xml' % (options.name),'w') as xml:
        xml.write('<edges>\n')
        for col in GRID.cells:
            for cell in col:
                for conn in cell.connections:
                    xml.write('\t<edge id="road%d" from="cell%d_%d" to="cell%d_%d" priority="%d" numLanes="%d" speed="%f"/>\n' %  (n_conn, conn.ifrom.col, conn.ifrom.row, conn.ito.col, conn.ito.row, 1, options.lanes, options.speed)) 
                    n_conn += 1
                    continue
                    
                # Update
                print('Writing grid.nod.xml %6.2f%%' % (float(n)/float(total)*100),end='\r')
                n += 1
                continue
            continue
        xml.write('</edges>')
    return

# Write Sumoconfig and Route Files
# @param options = command line arguments
def write_sumocfg_rou_settings(options):
    print('Writing additional files...', end='')
    
    # Sumoconfig
    sumocfg = '<configuration>\n\t<input>\n\t\t<net-file value="%s.net.xml" />\n\t\t<route-files value="%s.rou.xml" />\n\t</input>\n\t<time>\n\t\t<begin value="0" />\n\t\t<end value="3000000" />\n\t</time>\n' % (options.name,options.name)
    
    sumocfg += '\t<settings>\n\t\t<grid-dimension rows="%d" cols="%d" />\n\t</settings>\n' % (int(options.window_height/options.cell_dim),int(options.window_width/options.cell_dim))
    
    sumocfg += '</configuration>'
    
    # Routefile
    routefile = """<routes>\n</routes>"""
    
    # Settings FIles
    x,y = xystring2float(options.center_xy)
    settings = '<viewsettings>\n\t<delay value="50"/>\n\t<scheme name="real world"/>\n\t<viewport zoom="100" x="%f" y="%f"/>\n</viewsettings>' % (x,y)
    with open('temp/%s.sumocfg' % (options.name),'w') as f:
        f.write(sumocfg)
    with open('temp/%s.rou.xml' % (options.name),'w') as f:
        f.write(routefile)
    with open('temp/%s.settings.xml' % (options.name),'w') as f:
        f.write(settings)
    print('COMPLETE!')
    return

# Concatenates the name and cell_dimension
# @param options = command line arguments
# @return options.name = name.cell_dim
def concat_name_cell_dim(options):
    options.name = '%s.%d' % (options.name,options.cell_dim)
    return options

# Move files to output directory
# @param options = command line arguments
def move_files(options):
    print('Moving files...',end='')
    os.system('mkdir "%s"' % (options.output_dir))
    os.system('move .\\temp\\*.* %s' % (options.output_dir))
    os.system('rmdir temp')
    print('COMPLETE!')
    return

main()
