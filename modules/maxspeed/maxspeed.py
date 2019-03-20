# edgestats.py
# Author: Quentin Goss
# Last Modified: 3/12/2019
# 
# Returns the max min and average speeds in a .net.xml file
import math

def main():
  options = get_options()
  print(options.net_xml + '\n')
  
  print("1 m/s = 2.23694 mph\n")
  
  speeds = []
  #class priority:
  #  current = None
  #  vals = []
  #  speeds = []
  #class _type:
  #  current = None
  #  vals = []
  #  speeds = []
  n = 0
  outliers = 0
  
  with open(options.net_xml,'r') as net_xml:
    for s_line in net_xml:
      
      #if 'priority="' in s_line:
      #  s_line = s_line[s_line.index('priority="')+len('priority="'):]
      #  priority.current = int(s_line[:s_line.index('"')])
      #  if 'type="' in s_line:
      #    s_line = s_line[s_line.index('type="')+len('type="'):]
      #    _type.current = s_line[:s_line.index('"')]
      
      ###
      # All speeds
      ###    
      if 'speed="' in s_line:
        s_line = s_line[s_line.index('speed="')+len('speed="'):]
        s = float(s_line[:s_line.index('"')])
        speeds.append(s)
        n += 1
      
    # end for
  # end with  
  speeds.sort()
  
  if not options.trim_perc < 0.0000000001:    
    trim_perc = options.trim_perc
    #trim_perc = 0.007
    trim_amt = int(float(len(speeds)) * trim_perc)
    speeds = speeds[trim_amt:-trim_amt]
  else:
    trim_perc = options.trim_perc
    trim_amt = 0
  
  class ms:
    _min = speeds[0]
    _max = speeds[-1]
    avg = math.fsum(speeds)/len(speeds)
  class mph:
    _min = ms._min * 2.23694
    _max = ms._max * 2.23694
    avg = ms.avg * 2.23694
  print("Min: %5.2f m/s %6.2f mph\nAvg: %5.2f m/s %6.2f mph\nMax: %5.2f m/s %6.2f mph\n" % (ms._min,mph._min,ms.avg,mph.avg,ms._max,mph._max))
  
  print("+-- Bottom 100 Speeds --+")
  print(speeds[:100])
  
  print("\n+-- Top 100 Speeds --+")
  print(speeds[-100:])
  
  print("\n# Lanes: %d" % (n))
  print("Trimmed: %.2f%% or %d items" % (trim_perc * 100, trim_amt*2))
# End def main()



# Get options from optparse
# @return options - Flag options
def get_options():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option('--net_xml', help='Path of the NET_XML file', action='store', type='string', dest='net_xml', default='None')
  parser.add_option('--trim_perc', help="% to me trimmeded.", action='store', type='float',dest='trim_perc',default=0.0)
  (options, args) = parser.parse_args()
  
  if options.net_xml == 'None':
    raise Exception('.net.xml not declared. Please point to the .net.xml using --net_xml NET_XML.')
  elif options.net_xml[0-len('.net.xml'):] != '.net.xml':
    raise Exception('Incorrect .net.xml file extension >> \'{}\'. Must end in .net.xml!' .format(options.net_xml))
  
  return options
# end def get_options()

main()
