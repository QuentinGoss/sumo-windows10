:: Black Trace, Grey Map, White Nodes
python dgpng.py ^
--edg.xml=.\london-seg4\100\london-seg4.100.edg.xml ^
--nod.xml=.\london-seg4\100\london-seg4.100.nod.xml ^
--png=baseline.png ^
--background-color=(255,255,255,255) ^
--node-color=(255,255,255,255) ^
--edge-color=(0,0,0,100) ^
--internal-node-color=(0,0,0,0) ^
--edge-thickness=10 ^
--padding=10 ^
--color.ssv=baseline.ssv 
pause
exit
:: Black Trace, No Map, White Nodes
python dgpng.py ^
--edg.xml=.\london-seg4\100\london-seg4.100.edg.xml ^
--nod.xml=.\london-seg4\100\london-seg4.100.nod.xml ^
--png=baseline2.png ^
--background-color=(255,255,255,255) ^
--node-color=(0,0,0,0) ^
--edge-color=(0,0,0,0) ^
--internal-node-color=(0,0,0,0) ^
--edge-thickness=4 ^
--padding=10 ^
--color.ssv=baseline.ssv ^
--bw
exit
--save=flpoly.dg
--background-color=(14,14,14,255)
--save=C:\demand-supply-model\ignore\misc\greater-london\greater-london.dg
