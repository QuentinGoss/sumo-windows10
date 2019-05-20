# dgpng.py
# Author: Quentin Goss
# Last Modified: 3/20/19
#
# Creates a png of a directed graph given edge and vertex data.
from PIL import Image, ImageDraw

def main():            
    options = get_options()
    vertex = decode_vertex(options.vertex)
    edge = decode_edge(options.edge)
    canvas = init_canvas(options,vertex)
    draw_dg(options,vertex,edge,canvas)
    

# Command Line Argument Parser
# @return OptionParser options = Parsed options
def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-v', '--vertex_file', type="string", dest='vertex', default=None, help='File containing vertex JSONS')
    parser.add_option('-e', '--edge_file', type='string', dest='edge', default=None, help='File containing edge JSONS.')
    parser.add_option('-o', '--output_file', type='string', dest='output', default='out.png', help='Path of the output image.')
    parser.add_option('-w', '--width', type='int', dest='width', default=640, help='Width of img in PX.')
    parser.add_option('-H', '--height', type='int', dest='height', default=480, help='height of img in PX.')
    #parser.add_option('-r', '--force_ratio', dest='force_ratio', default=False, action='store_true', help='Keep width:height ratio.')
    parser.add_option('-R', '--red', type='int', dest='red', default=255, help='Red color of background. range[0:255]')
    parser.add_option('-G', '--green', type='int', dest='green', default=255, help='Green color of background. range[0:255]')
    parser.add_option('-B', '--blue', type='int', dest='blue', default=255, help='Blue color of background. range[0:255]')
    parser.add_option('-A', '--alpha', type='int', dest='alpha', default=255, help='Alpha of background. range[0:255]')
    parser.add_option('-E', '--edge_thickness', type='int', dest='edge_thickness', default=1, help='Thickness of edge line.')
    parser.add_option('-V', '--vertex_radius', type='int', dest='vertex_radius', default=1, help='Radius of vertex circle.')
    parser.add_option('-p', '--pandding', type='int', dest='padding', default=5, help='Padding around drawing frame in PX')
    parser.add_option('--vertex_red', type='int', dest='vertex_red', default=0, help='Red color of Vertex. range[0:255]')
    parser.add_option('--vertex_green', type='int', dest='vertex_green', default=0, help='Green color of Vertex. range[0:255]')
    parser.add_option('--vertex_blue', type='int', dest='vertex_blue', default=0, help='Blue color of Vertex. range[0:255]')
    parser.add_option('--vertex_alpha', type='int', dest='vertex_alpha', default=255, help='Alpha of Vertex. range[0:255]')
    parser.add_option('--edge_red', type='int', dest='edge_red', default=0, help='Red color of Edge. range[0:255]')
    parser.add_option('--edge_green', type='int', dest='edge_green', default=0, help='Green color of Edge. range[0:255]')
    parser.add_option('--edge_blue', type='int', dest='edge_blue', default=0, help='Blue color of Edge. range[0:255]')
    parser.add_option('--edge_alpha', type='int', dest='edge_alpha', default=255, help='Alpha of Edge. range[0:255]')
    (options,args) = parser.parse_args()
    if options.vertex == None:
        raise Exception("No Vertex file selected.")
    if options.edge == None:
        raise Exception("No edge file selected.")
    return options


# Decodes a JSON object from file.
# @param string _file = filepath
# @return dictionary data = JSON data
def decode_json(_file):
    import json
    with open(_file,'r') as f:
        data = json.load(f)
    return data

# Decodes a vertex data file
# @param string _file = filepath
# @return vertex = vertex struct
def decode_vertex(_file):
    data = decode_json(_file)
    class vertex:
        ids = []
        class coords:
            true = []
            normal = []
    for key,val in data.items():
        vertex.ids.append(key)
        vertex.coords.true.append(val['true_center_coords'])
        vertex.coords.normal.append(val['normal_center_coords'])
    # Invert y
    for i in range(len(vertex.coords.normal)):
        vertex.coords.normal[i][1] = 1 - vertex.coords.normal[i][1]
    return vertex
    
# Decodes an edge data file
# @param string _file = filepath
# @return edge = edge struct
def decode_edge(_file):
    data = decode_json(_file)
    class edge:
        class ids:
            self = ''
            _from = []
            to = []
        class coords:
            true = []
            normal = []
    for key,val in data.items():
        edge.ids.self = key
        edge.ids._from.append(val['from'])
        edge.ids.to.append(val['to'])
        edge.coords.true.append(val['true_coords'])
        edge.coords.normal.append(val['normal_coords'])
    # invert y values
    for i in range(len(edge.coords.normal)):
        edge.coords.normal[i][0][1] = 1 - edge.coords.normal[i][0][1]
        edge.coords.normal[i][1][1] = 1 - edge.coords.normal[i][1][1]
    return edge
    
# Initializes canvas struct
# @param OptParse options = cmd line arguments
# @param vertex vertex = vertex struct
# @return canvas = canvas struct
def init_canvas(options,vertex):
    class canvas:
        ratio = 1
        height = options.height
        width = options.width
        class frame:
            height = None
            width = None
            class border:
                x = None
                y = None
    # x : y = (x_max - x_min) / (y_max - y_min)
    #x_len = max(vertex.coords.true[0]) - min(vertex.coords.true[0])
    #y_len = max(vertex.coords.true[1]) - min(vertex.coords.true[1])
    #print('%4.3f:%4.3f' % (x_len,y_len))
    #ratio = x_len / y_len
    #print('%4.3f:1' % (ratio))
    #if (ratio > 1):
    #    canvas.width = int(float(canvas.height) * ratio)
    #else:
    #    canvas.height =int(float(canvas.width) / ratio)
    #print('%4.3f:1' % (canvas.width/canvas.height))
    #input('hhh')
    #canvas.ratio = (max(vertex.coords.true[0]) - min(vertex.coords.true[0])) / (max(vertex.coords.true[1]) - min(vertex.coords.true[1]))
    canvas.frame.height = canvas.height - options.padding * 2
    canvas.frame.width = canvas.width - options.padding *2
    canvas.frame.border.x = [options.padding,options.padding + canvas.frame.width]
    canvas.frame.border.y = [options.padding,options.padding + canvas.frame.height]
    #canvas.height = canvas.frame.height + 2 * options.padding
    #canvas.width = canvas.frame.width + 2 * options.padding
    return canvas

# Draws the directed graph to an img
# @param OptParse options = cmd line arguments
# @param vertex vertex = vertex struct
# @param edge edge = edge struct
# @param canvas canvas = canvas struct
# @return Image img = PIL img object
def draw_dg(options,vertex,edge,canvas):
    img = Image.new('RGBA',(canvas.width,canvas.height),(options.red,options.green,options.blue,options.alpha))
    img = draw_vertices(img,vertex,canvas,options)
    img = draw_edges(img,edge,canvas,options)
    img.save(options.output)
    return img
    
# Draws vertexs onto img
# @param vertex vertex = vertex struct
# @param Image img = img to draw on
# @return Image img = modified image
# @param OptParse options = cmd line arguments
def draw_vertices(img,vertex,canvas,options):
    draw = ImageDraw.Draw(img)
    for xy in vertex.coords.normal:
        center = (int(xy[0]*canvas.frame.width + canvas.frame.border.x[0]),int(xy[1]*canvas.frame.height + canvas.frame.border.y[0]))
        r = options.vertex_radius
        draw.ellipse((center[0]-r,center[1]-r,center[0]+r,center[1]+r), outline=(options.vertex_red,options.vertex_green,options.vertex_blue,options.vertex_alpha))
    return img

# Draws edge onto img
# @param edge = edge struct
# @param Image img = img to draw on
# @return Image img = modified image
# @param OptParse options = cmd line arguments
def draw_edges(img,edge,canvas,options):
    draw = ImageDraw.Draw(img)
    for xy in edge.coords.normal:
        points = (int(xy[0][0]*canvas.frame.width + canvas.frame.border.x[0]),int(xy[0][1]*canvas.frame.height + canvas.frame.border.y[0]),int(xy[1][0]*canvas.frame.width + canvas.frame.border.x[0]),int(xy[1][1]*canvas.frame.height + canvas.frame.border.y[0]))
        draw.line(points,width=options.edge_thickness,fill=(options.edge_red,options.edge_green,options.edge_blue,options.edge_alpha))
    return img
main()
