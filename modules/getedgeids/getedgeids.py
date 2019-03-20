def main():
  options = get_options()
  print(options.net_xml)
  
  edge_ids = []
  
  with open(options.net_xml,'r') as net_xml:
    for s_line in net_xml:
      if '<edge ' in s_line:
        s_line = s_line[s_line.index('id="')+len('id="'):]
        _id = s_line[:s_line.index('"')]
        edge_ids.append(_id)
    # end for
  # end with
  
  edge_ids.sort()
  
  with open(options.output,'w') as output:
    first = True
    for _id in edge_ids:
      if first:
        output.write(_id)
        first = False
      else:
        output.write('\n' + _id)
  # end with
  
# end def main()

# Get options from optparse
# @return options - Flag options
def get_options():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option('--net_xml', help='Path of the NET_XML file', action='store', type='string', dest='net_xml', default='None')
  parser.add_option('--output', help='Path of the output file', action='store', type='string', dest='output', default='./out.txt')
  (options, args) = parser.parse_args()
  
  if options.net_xml == 'None':
    raise Exception('.net.xml not declared. Please point to the .net.xml using --net_xml NET_XML.')
  elif options.net_xml[0-len('.net.xml'):] != '.net.xml':
    raise Exception('Incorrect .net.xml file extension >> \'{}\'. Must end in .net.xml!' .format(options.net_xml))
  
  return options
# end def get_options()

main()
