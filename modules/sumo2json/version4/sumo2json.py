# sumo2json.py
# Author: Quentin Goss
# Last Modified: 3/27/2019
# Converts select sumo .net.xml data into .json format.
#
# VERSION 2:
# - Added fields 'from' and 'to' which contain IDs of the edges
#   at the start and end of the edge.
#
# VERSION 3:
# - Now uses SUMO edge id instead of from_to
#
# VERSION 4:
# - Rewritten to fix cases of missing edges.

def main():
    options = get_options()
    print('Using .net.xml >> %s' % (options.net_xml))
    
    global EDGES
    EDGES = []
    global N_EDGES
    N_EDGES = 1
    
    # Fill in the edge data I can at the moment
    parse_edge1(options)
    
    # Fill in the vertex data that I can
    print()
    global VERTEX
    VERTEX = []
    global N_VERTEX
    N_VERTEX = 1
    global X
    X = []
    global Y
    Y = []
    parse_vertex1(options)
    
    # Find the boundaries and link vertices with edges
    print()
    global BOUNDS
    BOUNDS = [[min(X),min(Y)],[max(X),max(Y)]]
    print("Found Boundaries: %.2f < x < %.2f %.f < y < %.f" % (BOUNDS[0][0], BOUNDS[1][0], BOUNDS[0][1], BOUNDS[1][1]))
    
    # Correlate Vertices with Edges
    link_edges()
    print()
    
    # Normalize coordinates
    normalize_coords()
    
    # Write JSON files
    print()
    write_vertex(options)
    print()
    write_edge(options)
    
    print('\nComplete.')
    return
  
def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-x','--net_xml', help='Path of the NET_XML file', action='store', type='string', dest='net_xml', default='None')
    parser.add_option('-e','--edge_json', help='Name of the edge json file.', action='store', type='string', dest='edges_json', default='edges.json')
    parser.add_option('-v','--vertex_json', help='Name of the vertex json file.', action='store', type='string', dest='vertex_json', default='junctions.json')
    (options, args) = parser.parse_args()

    if options.net_xml == 'None':
        raise Exception('.net.xml not declared. Please point to the .net.xml using --net_xml NET_XML.')
    elif options.net_xml[0-len('.net.xml'):] != '.net.xml':
        raise Exception('Incorrect .net.xml file extension >> \'{}\'. Must end in .net.xml!' .format(options.net_xml))

    return options
    
# parses edges from the net.xml file
# @param options = cmd line arguments
def parse_edge1(options):
    xml = []
    global EDGES
    global N_EDGES
    class state:
        at_edge = False
    with open(options.net_xml,'r') as net_xml:
        for line in net_xml:
            # First pass of edge
            if '<edge ' in line:
                xml.append(line)
                state.at_edge = True
                print('Gathering initial edge data for edge #%d' % N_EDGES, end='\r')
                N_EDGES += 1
                continue
            elif '</edge>' in line:
                attr = get_attributes(xml)
                del xml[:]
                state.at_edge = False
                EDGES.append(parse_attr_edge_pass1(attr))
            elif state.at_edge:
                xml.append(line)
    return

# Revised get attributes method
# @param _xml to be parsed
# @return data = 
def get_attributes(_xml):
    data = []
    for xml in _xml:
        attr = [] # [key,val]
        if '<edge' in xml:
            xml = xml[xml.index('<edge ')+len('<edge '):]
        elif '<lane' in xml:
            xml = xml[xml.index('<lane ')+len('<lane '):]
        elif '<junction' in xml:
            xml = xml[xml.index('<junction ') + len('<junction '):]
        while '"' in xml:
            key = xml[:xml.index('=')]
            xml = xml[len(key)+2:]
            val = xml[:xml.index('"')]
            xml = xml[xml.index('"')+2:]
            attr.append([key,val])
        data.append(attr)
    return data

# Parse edge attributes. Does not fill in coordinate data yet.
# @param list list data = list of attributes
# @return partially filled edge object
def parse_attr_edge_pass1(data):
    from sumodgclasses import edge
    e = edge()
    for attr in data[0]:
        if 'id' in attr[0]: e.id_me = attr[1]
        elif 'from' in attr[0]: e.id_from = attr[1]
        elif 'to' in attr[0]: e.id_to = attr[1]
        elif 'priority' in attr[0]: e.priority = attr[1]
        elif 'type' in attr[0]: e._type = attr[1]
    e.lanes = str(len(data) - 1)
    for i in range(1,len(data)):
        for attr in data[i]:
            if ('speed' in attr[0]) and (float(attr[1]) > e.speed): e.speed = float(attr[1])
            if ('length' in attr[0]) and (float(attr[1]) > e.length): e.length = float(attr[1])
    return e

# Parse Vertex data
def parse_vertex1(options):
    global N_VERTEX
    global VERTEX
    with open(options.net_xml,'r') as net_xml:
        for line in net_xml:
            if '<junction ' in line:
                attr = get_attributes([line])[0]
                VERTEX.append(parse_attr_vertex_pass1(attr))
                print('Gathering inital vertex data for vertex #%d' % (N_VERTEX), end='\r')
                N_VERTEX += 1
                
    return

# Parse vertex attributes. Does not fill in Normalized coordinates yet.
# @param data = list of vertex attributes
# @return partially filled vertex object
def parse_attr_vertex_pass1(data):
    from sumodgclasses import vertex
    v = vertex()
    x = float()
    y = float()
    for attr in data:
        if 'id' in attr[0]: v.id = attr[1]
        elif ('x' in attr[0]) and (len(attr[0]) == 1): x = float(attr[1])
        elif ('y' in attr[0]) and (len(attr[0]) == 1): y = float(attr[1])
    v.coords_true = [x,y]
    global X
    global Y
    X.append(x)
    Y.append(y)
    return v

# Correlates Vertices with Edges
def link_edges():
    global VERTEX
    global EDGES
    global N_EDGES
    n = 1
    class coords:
        _from = None
        to = None
    for e in EDGES:
        coords._from = None
        coords.to = None
        for v in VERTEX:
            if v.id == e.id_from: 
                coords._from = v.coords_true
            elif v.id == e.id_to: coords.to = v.coords_true
            if not (coords._from == None) and not (coords.to == None): break
        e.coords_true = [coords._from,coords.to]
        print("Linking Vertices to Edges %6.2f%%" % (float(n)/float(N_EDGES) * 100), end='\r')
        n += 1
    return

# Normalize coordinates
def normalize_coords():
    global VERTEX
    global EDGES
    global N_EDGES
    global N_VERTEX
    global BOUNDS
    n = 1
    for v in VERTEX:
        v.coords_norm = [normalize(v.coords_true[0],BOUNDS[1][0],BOUNDS[0][0]),normalize(v.coords_true[1],BOUNDS[1][1],BOUNDS[0][1])]
        print("Normalizing Vertices %6.2f%%" % (float(n)/float(N_VERTEX) * 100),end='\r')
        n += 1
    print()
    n = 1
    for e in EDGES:
        #
        e.coords_norm = [[normalize(e.coords_true[0][0],BOUNDS[1][0],BOUNDS[0][0]),normalize(e.coords_true[0][1],BOUNDS[1][1],BOUNDS[0][1])],[normalize(e.coords_true[1][0],BOUNDS[1][0],BOUNDS[0][0]),normalize(e.coords_true[1][1],BOUNDS[1][1],BOUNDS[0][1])]]
        print("Normalizing Edges %6.2f%%" % (float(n)/float(N_EDGES) * 100),end='\r')
        n += 1
    return

# Normalize a coordinate
# @param float x = Value to normalize
# @param float _max = upper limit
# @param float _min = lower limit
# @return normalized value
def normalize(x,_max,_min):
    return (_max - x)/(_max - _min)

# Write the vertex json file
def write_vertex(options):
    global VERTEX
    global N_VERTEX
    with open(options.vertex_json,'w') as vj:
        vj.write('{\n')
        first = True
        n = 1
        for v in VERTEX:
            msg = ''
            if not first:
                msg += ','
            else:
                first = False
            msg += '\n\t"' + v.id + '": {\n'
            msg += '\t\t"true_center_coords": [' + str(v.coords_true[0]) + ',' + str(v.coords_true[1]) + '],\n'
            msg += '\t\t"normal_center_coords": [' + str(v.coords_norm[0]) + ',' + str(v.coords_norm[1]) + ']\n'
            msg += '\t}'
            vj.write(msg)
            print("Writing Vertices to file %6.2f%%" % (float(n)/float(N_VERTEX) * 100),end='\r')
            n += 1
        vj.write('\n}')
    return

# Write the edge json file
def write_edge(options):
    global EDGES
    global N_EDGES
    with open(options.edges_json,'w') as ej:
        ej.write('{\n')
        first = True
        n = 1
        for e in EDGES:
            msg = ''
            if not first:
                msg += ','
            else:
                first = False
            msg += '\n\t"' + e.id_me + '": {\n'
            msg += '\t\t"true_coords": [[' + str(e.coords_true[0][0]) + ',' + str(e.coords_true[0][1]) + '],[' + str(e.coords_true[1][0]) + ',' + str(e.coords_true[1][1]) + ']],\n'
            msg += '\t\t"normal_coords": [[' + str(e.coords_norm[0][0]) + ',' + str(e.coords_norm[0][1]) + '],[' + str(e.coords_norm[1][0]) + ',' + str(e.coords_norm[1][1]) + ']],\n'
            msg += '\t\t"from": "' + e.id_from + '",\n'
            msg += '\t\t"to": "' + e.id_to + '",\n'
            msg += '\t\t"priority": "' + e.priority + '",\n'
            msg += '\t\t"type": "' + e._type + '",\n'
            msg += '\t\t"lanes": ' + e.lanes + ',\n'
            msg += '\t\t"speed": ' + str(e.speed) + ',\n'
            msg += '\t\t"length": ' + str(e.length) + '\n'
            msg += '\t}'
            ej.write(msg)
            print("Writing Edges to file %6.2f%%" % (float(n)/float(N_EDGES) * 100),end='\r')
            n += 1
        ej.write('\n}')
    return
main();
