# json2sqlite.py
# Author: Quentin Goss
# Last Modified: 4/2/19
#
# Creates an SQL lite database from an edge and vertex json file
#

def main():
    options = get_options()
    db = connect2db(options)
    create_vertex_table(db,options)
    create_edge_table(db,options)
    db.conn.close()
    return

def get_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-v', '--vertex_file', type="string", dest='vertex', default=None, help='File containing vertex JSONS')
    parser.add_option('-e', '--edge_file', type='string', dest='edge', default=None, help='File containing edge JSONS.')
    parser.add_option('-d', '--dbname', type='string', dest='dbname', default='map.db', help='Path to the database file.')
    #parser.add_option('-H', '--histogram_file', type='string', dest='histogram', default=None, help='File containing Histogram data.')
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

# Connects to database
# @param options = cmd arguments
# @param db = database connection and cursor
def connect2db(options):
    import sqlite3
    class db:
        conn = sqlite3.connect(options.dbname)
        c = None
    db.c = db.conn.cursor()
    return db
    
# Creates the table where the vertices go
# @param db = database
# @param options = cmd line arguments
def create_vertex_table(db,options):
    vdata = decode_json(options.vertex)
    db.c.execute("CREATE TABLE vertex (id TEXT, true_x REAL, true_y REAL, norm_x REAL, norm_y REAL)")
    for key,val in vdata.items():
        vertex = (key,val['true_center_coords'][0],val['true_center_coords'][1],val['normal_center_coords'][0],val['normal_center_coords'][1])
        db.c.execute("INSERT INTO vertex VALUES (?,?,?,?,?)",vertex)
    db.conn.commit()
    #db.c.execute("SELECT * FROM vertex")
    #print(db.c.fetchmany(10))
    return

# Creates the table where the edges go
# @param db = database
# @param options = cmd line arguments
def create_edge_table(db,options):
    edata = decode_json(options.edge)
    db.c.execute("CREATE TABLE edge (id TEXT, id_from TEXT, id_to TEXT, priority INTEGER, type TEXT, lanes INTEGER, speed REAL, length REAL, true_x0 REAL, true_y0 REAL, true_x1 REAL, true_y1 REAL, norm_x0 REAL, norm_y0 REAL, norm_x1 REAL, norm_y1 REAL)")
    for key,val in edata.items():
        edge = (key,val['from'],val['to'],int(val['priority']),val['type'],val['lanes'],val['speed'],val['length'],val['true_coords'][0][0],val['true_coords'][0][1],val['true_coords'][1][0],val['true_coords'][1][1],val['normal_coords'][0][0],val['normal_coords'][0][1],val['normal_coords'][1][0],val['normal_coords'][1][1])
        db.c.execute("INSERT INTO edge VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",edge)
    db.conn.commit()
    #db.c.execute("SELECT * FROM edge")
    #print(db.c.fetchmany(3))
    return

# Decodes a CSV file
# @param _csv = Path to csv file
def decode_csv(_csv):
    data = []
    with open(_csv,'r') as csv:
        for line in csv:
            row = []
            if '\n' in line: line = line[:line.rindex('\n')]
            items = line.split(',')
            for item in items:
                if item.isnumeric():
                    if '.' in item: row.append(float(item))
                    else: row.append(int(item))
                else: row.append(item)
            data.append(row)
    return data

main()
