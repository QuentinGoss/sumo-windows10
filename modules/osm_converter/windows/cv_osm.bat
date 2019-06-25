title OSM Converter

@ECHO off

::  Edit these
SET project=Wyandotte.MI
SET prj_dir=.\
SET begin=0
SET end=30000

::  Do not edit these
SET project=%project%
SET net_xml=%project%.net.xml
SET osm=%project%.osm
SET typ_xml=osm.typ.xml
SET poly_xml=%project%.poly.xml
SET rou_xml=%project%.rou.xml
SET sumocfg=%project%.sumocfg
SET geo_sumocfg=%project%_geo.sumocfg

::  Clean out old files
del %prj_dir%%net_xml% *.sumocfg
echo Old .net.xml file(s) removed. Creating a new one...

::  Netconvert
netconvert --osm-files %prj_dir%%osm% -o %prj_dir%%net_xml% ^
--roundabouts.guess --ramps.guess --output.street-names ^
--junctions.join --tls.guess-signals --tls.discard-simple --tls.join
echo netconvert Complete.

::  Polyconvert
polyconvert --net-file %prj_dir%%net_xml% --osm-files %prj_dir%%osm% --type-file %typ_xml% -o %prj_dir%%poly_xml%
echo polyconvert Complete.

::  Route File
echo ^<routes>\n^</routes^> > %prj_dir%%rou_xml%

::  Sumocfg File w/ Geometry
echo ^<configuration^> > %prj_dir%%geo_sumocfg%
echo     ^<input^> >> %prj_dir%%geo_sumocfg%
echo         ^<net-file value="%net_xml%" /^> >> %prj_dir%%geo_sumocfg%
echo         ^<route-files value="%rou_xml%" /^> >> %prj_dir%%geo_sumocfg%
echo         ^<additional-files value="%poly_xml%" /^> >> %prj_dir%%geo_sumocfg%
echo     ^</input^> >> %prj_dir%%geo_sumocfg%
echo     ^<time^> >> %prj_dir%%geo_sumocfg%
echo         ^<begin value="%begin%" /^> >> %prj_dir%%geo_sumocfg%
echo         ^<end value="%end%" /^> >> %prj_dir%%geo_sumocfg%
echo     ^</time^> >> %prj_dir%%geo_sumocfg%
echo ^</configuration^> >> %prj_dir%%geo_sumocfg%
echo Geometry config file created.

::  Sumocfg File
echo ^<configuration^> > %prj_dir%%geo_sumocfg%
echo     ^<input^> >> %prj_dir%%geo_sumocfg%
echo         ^<net-file value="%net_xml%" /^> >> %prj_dir%%geo_sumocfg%
echo         ^<route-files value="%rou_xml%" /^> >> %prj_dir%%geo_sumocfg%
echo     ^</input^> >> %prj_dir%%geo_sumocfg%
echo     ^<time^> >> %prj_dir%%geo_sumocfg%
echo         ^<begin value="%begin%" /^> >> %prj_dir%%geo_sumocfg%
echo         ^<end value="%end%" /^> >> %prj_dir%%geo_sumocfg%
echo     ^</time^> >> %prj_dir%%geo_sumocfg%
echo ^</configuration^> >> %prj_dir%%geo_sumocfg%
echo Config file created.

::  Clean Unknowns from the .poly.xml
python remove_unknown.py --poly_xml=%prj_dir%%poly_xml%
del temp.poly.xml
echo 'type=unknowns removed from .poly.xml'

pause
