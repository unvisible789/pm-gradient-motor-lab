-- PM Gradient Motor Lab FEMM geometry builder
-- Radial-flux 2D approximation of the described disc/axial concept.
openfemm()
newdocument(0)
mi_probdef(0, "millimeters", "planar", 1e-8, 25.000000, 30)

rotor_group = 2
stator_group = 1
coil_group = 3

mi_getmaterial("Air")
mi_getmaterial("NdFeB 40 MGOe")
mi_getmaterial("1010 Steel")
mi_getmaterial("1010 Steel")
mi_getmaterial("Copper")

function add_line(x1, y1, x2, y2)
  mi_addnode(x1, y1)
  mi_addnode(x2, y2)
  mi_addsegment(x1, y1, x2, y2)
end

function add_arc_segment(x1, y1, x2, y2, angle, maxseg)
  mi_addnode(x1, y1)
  mi_addnode(x2, y2)
  mi_addarc(x1, y1, x2, y2, angle, maxseg)
end

-- Air boundary
mi_drawarc(260.000000, 0, -260.000000, 0, 180, 2)
mi_drawarc(-260.000000, 0, 260.000000, 0, 180, 2)
mi_addblocklabel(0, 0)
mi_selectlabel(0, 0)
mi_setblockprop("Air", 1, 0, "<None>", 0, 0, 0)
mi_clearselected()

-- Rotor core
mi_drawarc(110.000000, 0, -110.000000, 0, 180, 2)
mi_drawarc(-110.000000, 0, 110.000000, 0, 180, 2)
mi_addblocklabel(10, 0)
mi_selectlabel(10, 0)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0, rotor_group, 0)
mi_clearselected()
-- Rotor gradient magnet 01

add_arc_segment(144.205675, -15.156627, 144.205675, 15.156627, 12.000000, 1)
add_arc_segment(119.342627, 12.543416, 119.342627, -12.543416, 12.000000, 1)
add_line(144.205675, -15.156627, 119.342627, -12.543416)
add_line(119.342627, 12.543416, 144.205675, 15.156627)
mi_addblocklabel(132.500000, 0.000000)
mi_selectlabel(132.500000, 0.000000)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 0.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 02

add_arc_segment(139.028862, 41.182225, 127.428481, 69.188020, 12.000000, 1)
add_arc_segment(105.458054, 57.259051, 115.058368, 34.081841, 12.000000, 1)
add_line(139.028862, 41.182225, 115.058368, 34.081841)
add_line(105.458054, 57.259051, 127.428481, 69.188020)
mi_addblocklabel(122.414038, 50.705555)
mi_selectlabel(122.414038, 50.705555)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 202.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 03

add_arc_segment(112.686164, 91.251457, 91.251457, 112.686164, 12.000000, 1)
add_arc_segment(75.518447, 93.257515, 93.257515, 75.518447, 12.000000, 1)
add_line(112.686164, 91.251457, 93.257515, 75.518447)
add_line(75.518447, 93.257515, 91.251457, 112.686164)
mi_addblocklabel(93.691649, 93.691649)
mi_selectlabel(93.691649, 93.691649)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 45.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 04

add_arc_segment(69.188020, 127.428481, 41.182225, 139.028862, 12.000000, 1)
add_arc_segment(34.081841, 115.058368, 57.259051, 105.458054, 12.000000, 1)
add_line(69.188020, 127.428481, 57.259051, 105.458054)
add_line(34.081841, 115.058368, 41.182225, 139.028862)
mi_addblocklabel(50.705555, 122.414038)
mi_selectlabel(50.705555, 122.414038)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 247.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 05

add_arc_segment(15.156627, 144.205675, -15.156627, 144.205675, 12.000000, 1)
add_arc_segment(-12.543416, 119.342627, 12.543416, 119.342627, 12.000000, 1)
add_line(15.156627, 144.205675, 12.543416, 119.342627)
add_line(-12.543416, 119.342627, -15.156627, 144.205675)
mi_addblocklabel(0.000000, 132.500000)
mi_selectlabel(0.000000, 132.500000)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 90.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 06

add_arc_segment(-41.182225, 139.028862, -69.188020, 127.428481, 12.000000, 1)
add_arc_segment(-57.259051, 105.458054, -34.081841, 115.058368, 12.000000, 1)
add_line(-41.182225, 139.028862, -34.081841, 115.058368)
add_line(-57.259051, 105.458054, -69.188020, 127.428481)
mi_addblocklabel(-50.705555, 122.414038)
mi_selectlabel(-50.705555, 122.414038)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 292.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 07

add_arc_segment(-91.251457, 112.686164, -112.686164, 91.251457, 12.000000, 1)
add_arc_segment(-93.257515, 75.518447, -75.518447, 93.257515, 12.000000, 1)
add_line(-91.251457, 112.686164, -75.518447, 93.257515)
add_line(-93.257515, 75.518447, -112.686164, 91.251457)
mi_addblocklabel(-93.691649, 93.691649)
mi_selectlabel(-93.691649, 93.691649)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 135.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 08

add_arc_segment(-127.428481, 69.188020, -139.028862, 41.182225, 12.000000, 1)
add_arc_segment(-115.058368, 34.081841, -105.458054, 57.259051, 12.000000, 1)
add_line(-127.428481, 69.188020, -105.458054, 57.259051)
add_line(-115.058368, 34.081841, -139.028862, 41.182225)
mi_addblocklabel(-122.414038, 50.705555)
mi_selectlabel(-122.414038, 50.705555)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 337.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 09

add_arc_segment(-144.205675, 15.156627, -144.205675, -15.156627, 12.000000, 1)
add_arc_segment(-119.342627, -12.543416, -119.342627, 12.543416, 12.000000, 1)
add_line(-144.205675, 15.156627, -119.342627, 12.543416)
add_line(-119.342627, -12.543416, -144.205675, -15.156627)
mi_addblocklabel(-132.500000, 0.000000)
mi_selectlabel(-132.500000, 0.000000)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 180.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 10

add_arc_segment(-139.028862, -41.182225, -127.428481, -69.188020, 12.000000, 1)
add_arc_segment(-105.458054, -57.259051, -115.058368, -34.081841, 12.000000, 1)
add_line(-139.028862, -41.182225, -115.058368, -34.081841)
add_line(-105.458054, -57.259051, -127.428481, -69.188020)
mi_addblocklabel(-122.414038, -50.705555)
mi_selectlabel(-122.414038, -50.705555)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 382.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 11

add_arc_segment(-112.686164, -91.251457, -91.251457, -112.686164, 12.000000, 1)
add_arc_segment(-75.518447, -93.257515, -93.257515, -75.518447, 12.000000, 1)
add_line(-112.686164, -91.251457, -93.257515, -75.518447)
add_line(-75.518447, -93.257515, -91.251457, -112.686164)
mi_addblocklabel(-93.691649, -93.691649)
mi_selectlabel(-93.691649, -93.691649)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 225.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 12

add_arc_segment(-69.188020, -127.428481, -41.182225, -139.028862, 12.000000, 1)
add_arc_segment(-34.081841, -115.058368, -57.259051, -105.458054, 12.000000, 1)
add_line(-69.188020, -127.428481, -57.259051, -105.458054)
add_line(-34.081841, -115.058368, -41.182225, -139.028862)
mi_addblocklabel(-50.705555, -122.414038)
mi_selectlabel(-50.705555, -122.414038)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 427.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 13

add_arc_segment(-15.156627, -144.205675, 15.156627, -144.205675, 12.000000, 1)
add_arc_segment(12.543416, -119.342627, -12.543416, -119.342627, 12.000000, 1)
add_line(-15.156627, -144.205675, -12.543416, -119.342627)
add_line(12.543416, -119.342627, 15.156627, -144.205675)
mi_addblocklabel(-0.000000, -132.500000)
mi_selectlabel(-0.000000, -132.500000)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 270.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 14

add_arc_segment(41.182225, -139.028862, 69.188020, -127.428481, 12.000000, 1)
add_arc_segment(57.259051, -105.458054, 34.081841, -115.058368, 12.000000, 1)
add_line(41.182225, -139.028862, 34.081841, -115.058368)
add_line(57.259051, -105.458054, 69.188020, -127.428481)
mi_addblocklabel(50.705555, -122.414038)
mi_selectlabel(50.705555, -122.414038)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 472.500000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 15

add_arc_segment(91.251457, -112.686164, 112.686164, -91.251457, 12.000000, 1)
add_arc_segment(93.257515, -75.518447, 75.518447, -93.257515, 12.000000, 1)
add_line(91.251457, -112.686164, 75.518447, -93.257515)
add_line(93.257515, -75.518447, 112.686164, -91.251457)
mi_addblocklabel(93.691649, -93.691649)
mi_selectlabel(93.691649, -93.691649)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 315.000000, 2, 0)
mi_clearselected()

-- Rotor gradient magnet 16

add_arc_segment(127.428481, -69.188020, 139.028862, -41.182225, 12.000000, 1)
add_arc_segment(115.058368, -34.081841, 105.458054, -57.259051, 12.000000, 1)
add_line(127.428481, -69.188020, 105.458054, -57.259051)
add_line(115.058368, -34.081841, 139.028862, -41.182225)
mi_addblocklabel(122.414038, -50.705555)
mi_selectlabel(122.414038, -50.705555)
mi_setblockprop("NdFeB 40 MGOe", 1, 0, "<None>", 517.500000, 2, 0)
mi_clearselected()

-- EML stator unit 01

add_arc_segment(202.476110, -32.069065, 202.476110, 32.069065, 18.000000, 1)
add_arc_segment(156.054758, 24.716645, 156.054758, -24.716645, 18.000000, 1)
add_line(202.476110, -32.069065, 156.054758, -24.716645)
add_line(156.054758, 24.716645, 202.476110, 32.069065)
mi_addblocklabel(181.500000, 0.000000)
mi_selectlabel(181.500000, 0.000000)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(196.265264, -16.998414, 196.265264, 16.998414, 9.900000, 1)
add_arc_segment(165.380882, 14.323537, 165.380882, -14.323537, 9.900000, 1)
add_line(196.265264, -16.998414, 165.380882, -14.323537)
add_line(165.380882, 14.323537, 196.265264, 16.998414)
mi_addblocklabel(181.500000, 0.000000)
mi_selectlabel(181.500000, 0.000000)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 02

add_arc_segment(165.848484, 120.495977, 120.495977, 165.848484, 18.000000, 1)
add_arc_segment(92.870070, 127.824685, 127.824685, 92.870070, 18.000000, 1)
add_line(165.848484, 120.495977, 127.824685, 92.870070)
add_line(92.870070, 127.824685, 120.495977, 165.848484)
mi_addblocklabel(128.339881, 128.339881)
mi_selectlabel(128.339881, 128.339881)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(150.800193, 126.760805, 126.760805, 150.800193, 9.900000, 1)
add_arc_segment(106.813674, 127.070213, 127.070213, 106.813674, 9.900000, 1)
add_line(150.800193, 126.760805, 127.070213, 106.813674)
add_line(106.813674, 127.070213, 126.760805, 150.800193)
mi_addblocklabel(128.339881, 128.339881)
mi_selectlabel(128.339881, 128.339881)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 03

add_arc_segment(32.069065, 202.476110, -32.069065, 202.476110, 18.000000, 1)
add_arc_segment(-24.716645, 156.054758, 24.716645, 156.054758, 18.000000, 1)
add_line(32.069065, 202.476110, 24.716645, 156.054758)
add_line(-24.716645, 156.054758, -32.069065, 202.476110)
mi_addblocklabel(0.000000, 181.500000)
mi_selectlabel(0.000000, 181.500000)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(16.998414, 196.265264, -16.998414, 196.265264, 9.900000, 1)
add_arc_segment(-14.323537, 165.380882, 14.323537, 165.380882, 9.900000, 1)
add_line(16.998414, 196.265264, 14.323537, 165.380882)
add_line(-14.323537, 165.380882, -16.998414, 196.265264)
mi_addblocklabel(0.000000, 181.500000)
mi_selectlabel(0.000000, 181.500000)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 04

add_arc_segment(-120.495977, 165.848484, -165.848484, 120.495977, 18.000000, 1)
add_arc_segment(-127.824685, 92.870070, -92.870070, 127.824685, 18.000000, 1)
add_line(-120.495977, 165.848484, -92.870070, 127.824685)
add_line(-127.824685, 92.870070, -165.848484, 120.495977)
mi_addblocklabel(-128.339881, 128.339881)
mi_selectlabel(-128.339881, 128.339881)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(-126.760805, 150.800193, -150.800193, 126.760805, 9.900000, 1)
add_arc_segment(-127.070213, 106.813674, -106.813674, 127.070213, 9.900000, 1)
add_line(-126.760805, 150.800193, -106.813674, 127.070213)
add_line(-127.070213, 106.813674, -150.800193, 126.760805)
mi_addblocklabel(-128.339881, 128.339881)
mi_selectlabel(-128.339881, 128.339881)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 05

add_arc_segment(-202.476110, 32.069065, -202.476110, -32.069065, 18.000000, 1)
add_arc_segment(-156.054758, -24.716645, -156.054758, 24.716645, 18.000000, 1)
add_line(-202.476110, 32.069065, -156.054758, 24.716645)
add_line(-156.054758, -24.716645, -202.476110, -32.069065)
mi_addblocklabel(-181.500000, 0.000000)
mi_selectlabel(-181.500000, 0.000000)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(-196.265264, 16.998414, -196.265264, -16.998414, 9.900000, 1)
add_arc_segment(-165.380882, -14.323537, -165.380882, 14.323537, 9.900000, 1)
add_line(-196.265264, 16.998414, -165.380882, 14.323537)
add_line(-165.380882, -14.323537, -196.265264, -16.998414)
mi_addblocklabel(-181.500000, 0.000000)
mi_selectlabel(-181.500000, 0.000000)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 06

add_arc_segment(-165.848484, -120.495977, -120.495977, -165.848484, 18.000000, 1)
add_arc_segment(-92.870070, -127.824685, -127.824685, -92.870070, 18.000000, 1)
add_line(-165.848484, -120.495977, -127.824685, -92.870070)
add_line(-92.870070, -127.824685, -120.495977, -165.848484)
mi_addblocklabel(-128.339881, -128.339881)
mi_selectlabel(-128.339881, -128.339881)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(-150.800193, -126.760805, -126.760805, -150.800193, 9.900000, 1)
add_arc_segment(-106.813674, -127.070213, -127.070213, -106.813674, 9.900000, 1)
add_line(-150.800193, -126.760805, -127.070213, -106.813674)
add_line(-106.813674, -127.070213, -126.760805, -150.800193)
mi_addblocklabel(-128.339881, -128.339881)
mi_selectlabel(-128.339881, -128.339881)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 07

add_arc_segment(-32.069065, -202.476110, 32.069065, -202.476110, 18.000000, 1)
add_arc_segment(24.716645, -156.054758, -24.716645, -156.054758, 18.000000, 1)
add_line(-32.069065, -202.476110, -24.716645, -156.054758)
add_line(24.716645, -156.054758, 32.069065, -202.476110)
mi_addblocklabel(-0.000000, -181.500000)
mi_selectlabel(-0.000000, -181.500000)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(-16.998414, -196.265264, 16.998414, -196.265264, 9.900000, 1)
add_arc_segment(14.323537, -165.380882, -14.323537, -165.380882, 9.900000, 1)
add_line(-16.998414, -196.265264, -14.323537, -165.380882)
add_line(14.323537, -165.380882, 16.998414, -196.265264)
mi_addblocklabel(-0.000000, -181.500000)
mi_selectlabel(-0.000000, -181.500000)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()

-- EML stator unit 08

add_arc_segment(120.495977, -165.848484, 165.848484, -120.495977, 18.000000, 1)
add_arc_segment(127.824685, -92.870070, 92.870070, -127.824685, 18.000000, 1)
add_line(120.495977, -165.848484, 92.870070, -127.824685)
add_line(127.824685, -92.870070, 165.848484, -120.495977)
mi_addblocklabel(128.339881, -128.339881)
mi_selectlabel(128.339881, -128.339881)
mi_setblockprop("1010 Steel", 1, 0, "<None>", 0.000000, 1, 0)
mi_clearselected()


add_arc_segment(126.760805, -150.800193, 150.800193, -126.760805, 9.900000, 1)
add_arc_segment(127.070213, -106.813674, 106.813674, -127.070213, 9.900000, 1)
add_line(126.760805, -150.800193, 106.813674, -127.070213)
add_line(127.070213, -106.813674, 150.800193, -126.760805)
mi_addblocklabel(128.339881, -128.339881)
mi_selectlabel(128.339881, -128.339881)
mi_setblockprop("Copper", 1, 0, "<None>", 0.000000, 3, 1)
mi_clearselected()


mi_zoomnatural()
mi_saveas("geometry/pm_gradient_motor_base.fem")
closefemm()
