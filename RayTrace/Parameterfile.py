#     BigBertha
#   Same as NASABOOM1EMParameterFile
import numpy as np
INPUTFILE = "input/inputNASABOOM1.txt"
RecInput = "Env/Receivers/PointReceivers.txt"
ipname = 'Env/SimpleEMBuilding/SingleBuilding.obj'
Fs = 24000.0
xinitial = 145.0
yinitial = 35.0
zinitial = 0.0
radius = .15
soundspeed = 348.537
ps = 1.0
Temp = 302.182778
time = .01
hr = 20.0
theta = 1.6863372
phi = 3.44458181
boomspacing = 0.6   # .6
# boomspacing= 0.035
# boomspacing= 0.1
# boomspacing= 1
xmin = -1
ymin = 30.0
zmin = 0.0
xmax = -1
ymax = 100.0
zmax = 25.0
IMAX = 75
h = 10.0
absorbplanes = 1
# allocate(tempalphabuilding(absorbplanes,8))
# Find way to rephrase
# outputfile = 'PythonTest1.txt'
outputfile = "PythonTestSimple" + str(boomspacing) + "_withdecl.txt"       # debugging
graphName = "TestGraph"                                     # No not use full file extension here
# Will's
# outputfile = "PythonTestEnv" + str(boomspacing) + ".txt"       # debugging
# Turn Radiosity on or off.  This will include diffuse reflections
radiosity = 1
# Turn on complex absorption
complexabsorption = 0

tempalphabuilding = np.zeros([absorbplanes, 8])
if complexabsorption == 1:
    tempalphabuilding[0] = [0.55, 0.55, 0.25, 0.18, 0.12, 0.07, 0.04, 0.04]
else:
    tempalphabuilding = np.zeros([absorbplanes, 8])

# Enter an array for absorption of alpha ground octave bands between
# 63 and 8000
tempalphaground = [0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03]
# Enter an array for absorption of Alpha Building octave bands between
# 63 and 8000
tempalphabuilding[0, :] = [0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.03]
# what percentage of the energy is reflected diffusely between 0,1
percentdiffuse = 0.0

# Broken all down to:
# complexabsorption = 1
# if complexabsorption == 1:
#     tempalphaground=np.array([[0.55,0.55,0.25,0.18,0.12,0.07,0.04,0.04],
#     [0.01,0.01,0.01,0.02,0.02,0.02,0.03,0.03],[0.01,0.01,0.01,0.02,0.02,0.02,0.03,0.03]])
# print(tempalphaground)

# if __name__ == "__main__":      #being lazy. You can run from here now
#    import RayTrace
# pass
