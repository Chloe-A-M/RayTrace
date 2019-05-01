# RayTrace
# version 1.0.5

# Kimberly Lefkowitz created this program to propagate sonic booms around
# large structures, and to graduate. It is a ray tracing model that 
# will include specular and diffuse reflections. It will print out the
# sound field at ear height, at relevant microphone locations, and at 
# the building walls. It will read in the fft of a sonic boom signature.

# Dr. Riegel, William Costa, and George Seaton porting program from Fortran to python

# linking other python files with initialized variables and functions
import Parameterfile as PF
import BuildingGeometry as BG
import numpy as np
import Functions as fun
import ReceiverPointSource as RPS
#import math as m

import time

# What it does    
"""
      Initializes arrays 
      Initializes receivers
      Reads in geometry file (Boxes)
      Has Rays interact with receivers    
      Reconstructs data with respect to time 
      Print out results 
      Run fast          *New 4/14
"""
      
# What it does not do
"""
      Interacts with geometry
      Have a way of reading in complex geometries 
      Anything resembling radiosity
      Run Well          *New 4/14
"""

def TIMERECONSTRUCT(sizefft,magnitude,direction):
    '''
    This Function computes the timesignal from a given fft.  It writes the
    time signal to an array
    Timearray is now defined in here. Do not call it.
    Args:
    Returns:
    '''
    #outputarray[:,0] = frecuencias  [:,0]
    #outputarray[:,1] = receiverpoint[0]
    #outputarray[:,2] = receiverpoint[1]
    #outputarray[:,3] = receiverpoint[2]
    #outputarray[:,4] = ampinitial   [:] / 2.0
    #outputarray[:,5] = phaseinitial [:]
    #temparray[D,:,3]=inputarray[W,0]    #initial pressures
    #temparray[D,:,4]=0.0                #magnitude
    #temparray[D,:,5]=0.0                #direction
    #timetemparray[D,:,0]=temparray[D,0,0]
    #timetemparray[D,:,1]=temparray[D,0,1]
    #timetemparray[D,:,2]=temparray[D,0,2]
    #        timetemparray[D,W,3]=timearray[W]   #Not actually used until outside function
    #        timetemparray[D,W,4]=0.0    #timesignal
    XJ=complex(0,1)
    print('timeconstruct has been called')

    print('timetemparray has been initialized')
    # Create the complex array to feed into the inverse fft function
    # Author: Will, Create complex array and compute inverse fft first attempt Python
    #for D in range(0,arraysize) :

    # timetemparray has been broken into timesignal, as it is the only thing calculated inside this function

    #print('mag: ',magnitude.shape)
    if magnitude[0] == 0.0:
        # If first magnitude is zero then all timesignal is zero
        timesignal = 0.0

    else:
        # If not then calculate the timesignal 
        tempfft = abs(magnitude[:]) * np.exp(XJ*direction)
        tempfft = np.append(0,tempfft)
        print(tempfft.size)
        print('Created temparray')
        # use nummpy to compute inverse fft
        # use ifft numpy function with tempfft and sizefft as input
        # use timesignal as output
        timesignal=np.fft.ifft(tempfft,sizefft)
        print('Created time signature')
        #for W in range(sizeffttwo) :
            #if W == 0:
                #tempfft[W]=complex([0])
            #else:
                #tempfft[W]=complex(abs(temparray[D,W-1,4])*m.exp(XJ*temparray[D,W-1,5]))
                #tempfft = abs(magnitude[:]) * np.exp(XJ*direction)

    #return timetemparray
    return timesignal

def initial_signal(signalLength,fftOutput):
    """
    Making the array for the initial signals.
    Input sizefft and outputsignal
    """
    signalLength2 = int(signalLength//2)    # Making sizeffttwo in this function and setting it as an int again jsut to be sure
    outputFrequency = np.zeros((signalLength2,3))    #Making output array    equivalent to inputarray in old code
    throwarray = np.arange(1,signalLength2 + 1)     #Helps get rid of for-loops in old version

    outputFrequency[:,0] = throwarray * PF.Fs / signalLength #Tried simplifying the math a bit from original
    outputFrequency[:,1] = abs(fftOutput[:signalLength2]/signalLength) #Only go up to sizeffttwo 
    outputFrequency[:,2] = np.arctan2( np.imag(fftOutput[:signalLength2]/signalLength) , np.real(fftOutput[:signalLength2]/signalLength)) 

    return outputFrequency

def update(airabsorb,frequencia,phase,dx,amp,alpha,diffusion):
      """
      Update ray/ripple data
      Only input first row for frequency
      """
      PI = np.pi
      twopi = PI*2
      twopidx = twopi * dx

      lamb = PF.soundspeed/frequencia
      phaseTemp = phase[:] - (twopidx/lamb)
      ampTemp = amp[:] * (1.0-alpha) * (1.0-diffusion) * np.exp(airabsorb*dx)

      phase = phaseTemp[:] % twopi
      phase = np.where( (phase > PI),      phase-twopi,      phase)

      #self.phase = phase
      #self.amplitude = ampTemp
      return phase, ampTemp

# port and import receiver file
receiverhit=0
groundhit=0

# Initialize counters 
PI=3.1415965358979323846
XJ=(0.0,1.0)
radius2 = PF.radius**2
twopi= 2.0*PI
S=1
K=0
raysum=0

# Initiailize receiver variables
lastreceiver = np.empty(3)
lastreceiver2 = np.empty(3)
OC = np.empty(3)

# Read in input file
with open(PF.INPUTFILE) as IPFile:
      inputsignal=np.loadtxt(IPFile)
K=len(inputsignal)
HUGE=1000000.0
F=np.empty([1,3])

# Allocate the correct size to the signal and fft arrays

outputsignal=np.empty(int(K/2+1))
inputarray=np.empty((int(K/2),3))
inputarraynew=np.empty((int(K/2),3))
print(inputarraynew.shape)
#take the fft of the input signal with fftw

sizefft=K
sizeffttwo=sizefft//2
outputsignal=np.fft.fft(inputsignal,sizefft)
timearray=np.empty(sizefft)
timearraynew=np.empty(sizefft)
ampinitial=np.empty(sizeffttwo)
ampinitialnew=np.empty(sizeffttwo)
phaseinitial=np.empty(sizeffttwo)
phaseinitialnew=np.empty(sizeffttwo)

#       Create initial signal 
airabsorb = np.empty(sizeffttwo)
airabsorbnew = np.empty(sizeffttwo)
t = time.time()
Kbig=np.arange(0,sizefft,1)
#Knew=np.arange(1,sizeffttwo+1,1)

#inputarray[:,0]=Knew*PF.Fs/2*1/(sizeffttwo)
#inputarray[:,1]=abs(outputsignal[:sizeffttwo]/sizefft)
#inputarray[:,2]=np.arctan2(np.imag(outputsignal[:sizeffttwo]/sizefft),np.real(outputsignal[:sizeffttwo]/sizefft))
airabsorb=fun.ABSORPTION(PF.ps,inputarraynew[:,0],PF.hr,PF.Temp)
print('Absoption time no loop: %.8f ' %(time.time()-t))
frecuencias = initial_signal(sizefft,outputsignal)      # Equivalent to inputarray in original
inputarray =      frecuencias                   #hotfix for tight now
t=time.time()
#for K in range(sizeffttwo):
#    inputarray[K,0]=(K+1)*PF.Fs/2*1/(sizeffttwo)      #Frequenvies
#    inputarray[K,1]=abs(outputsignal[K]/sizefft)
#    inputarray[K,2]=np.arctan2(np.imag(outputsignal[K]/sizefft),np.real(outputsignal[K]/sizefft))
#    airabsorb[K]=fun.ABSORPTION(PF.ps,inputarray[K,0],PF.hr,PF.Temp)
#for K in range(sizefft):
#    timearray[K]=(K)*1/PF.Fs
#print('timearray: %.8f ' %(time.time()-t))
timearray=(Kbig)*1/PF.Fs

#close output signal and input #somehow

#       Set initial values
#Vinitial=np.around([PF.xinitial,PF.yinitial,PF.zinitial],8)
Vinitial =  np.array([PF.xinitial,PF.yinitial,PF.zinitial])
xiinitial  =np.cos(PF.phi)*np.sin(PF.theta)
ninitial   =np.sin(PF.phi)*np.sin(PF.theta)
zetainitial=np.cos(PF.theta)
length =    np.sqrt(xiinitial*xiinitial+ninitial*ninitial+zetainitial*zetainitial)
Finitial=np.array([xiinitial,ninitial,zetainitial])
                  #Show everything 
tmp=(Finitial[0]*Vinitial[0]+Finitial[1]*Vinitial[1]+Finitial[2]*Vinitial[2])
PLANEABC=np.array([Finitial[0],Finitial[1],Finitial[2],tmp])

#       Create initial boom array

yspace=PF.boomspacing*abs(np.cos(PF.phi))
zspace=PF.boomspacing*abs(np.sin(PF.theta))
if (PF.xmin == PF.xmax):
   RAYMAX=int((PF.ymax-PF.ymin)/yspace)*int((PF.zmax-PF.zmin)/zspace)
elif(PF.ymin == PF.ymax):
   RAYMAX=int((PF.xmax-PF.xmin)/xspace)*int((PF.zmax-PF.zmin)/zspace)
elif(PF.zmin == PF.zmax):
   RAYMAX=int((PF.ymax-PF.ymin)/yspace)*int((PF.xmax-PF.xmin)/xspace)
boomarray = np.zeros((RAYMAX,2))
print(RAYMAX , ' is the RAYMAX')
boomarray,sizex,sizey,sizez=fun.InitialGrid(PF.boomspacing,PLANEABC[0],PLANEABC[1],PLANEABC[2],PLANEABC[3],PF.theta,PF.phi,PF.xmin,PF.ymin,PF.zmin,PF.xmax,PF.ymax,PF.zmax,RAYMAX)

#     Create a receiver array, include a receiver file. 

alphanothing = np.zeros(sizeffttwo)

# Making specific receiver points using receive rmodule
RPS.Receiver.initialize(PF.RecInput)
ears = RPS.Receiver.rList           #easier to write
for R in ears:          #hotfix
      R.magnitude = np.zeros(sizefft)
RPS.arraysize= RPS.Receiver.arraysize
receiverpoint = [0.,0.,0.]
receiverarray = RPS.Receiver.Array  # backwards compatibility    Delete later
hitsum = 0

#############################################################
#      deallocate(receiverarray1)
#      if (planenum.ge.2) deallocate(receiverarray2)
#      if (planenum.ge.3) deallocate(receiverarray3)
#      if (planenum.ge.4) deallocate(receiverarray4)
#      if (planenum.ge.5) deallocate(receiverarray5)
#      if (planenum.ge.6) deallocate(receiverarray6)
#      if (planenum.ge.7) deallocate(receiverarray7)
#############################################################
#Find function to deallocate 

receiverarray1=None
if RPS.planenum >=2 :
    RPS.receiverarray2=None
if RPS.planenum >=3 :
    RPS.receiverarray3=None
if RPS.planenum >=4 :
    RPS.receiverarray4=None
if RPS.planenum >=5 :
    RPS.receiverarray5=None
if RPS.planenum >=6 :
    RPS.receiverarray6=None
if RPS.planenum >=7 :
    RPS.receiverarray7=None

#       Initialize normalization factor 
normalization=(PI*radius2)/(PF.boomspacing**2) 
temparray=np.empty((    RPS.Receiver.arraysize,sizeffttwo,6))
temparraynew=np.empty(( RPS.Receiver.arraysize,sizeffttwo,6))
timetemparray=np.zeros((RPS.Receiver.arraysize,sizefft,5))

t=time.time()

for D in range(0,RPS.Receiver.arraysize):
      for W in range(0,sizeffttwo):
            temparray[D,W,0]=receiverarray[D,0]
            temparray[D,W,1]=receiverarray[D,1]
            temparray[D,W,2]=receiverarray[D,2]
            temparray[D,W,3]=inputarray[W,0]    #initial pressures
            temparray[D,W,4]=0.0                #magnitude
            temparray[D,W,5]=0.0                #direction

#for D in range(0,RPS.Receiver.arraysize):
#      temparray[D,:,0:3]=RPS.Receiver.Array[D,0:3]
#      temparray[D,:,3]=inputarray[:,0]    #initial pressures
#      temparray[D,:,4]=0.0                #magnitude
#      temparray[D,:,5]=0.0                #direction


#for R in ears:
##      print(temparray[R,:,:])
##      print(R.position)
#      #temparray[R,:,0:3]=R.position
#      temparray[R,:,3]=inputarray[:,0]    #initial pressures
#      temparray[R,:,4]=0.0                #magnitude
#      temparray[R,:,5]=0.0                #direction

#for R in ears:
#      R.magnitude= np.zeros(sizefft)
#      R.frecuencias = frecuencias[:,0]
outputarray1=np.zeros((sizeffttwo,6))

#       Define ground plane
groundheight=0.000000000
GROUNDABC=np.array([0.000000000,0.000000000,1.00000000])
GROUNDD=-groundheight
groundD= -groundheight
nground=np.array([0.0,0.0,1.0])
alphaground=np.zeros(sizeffttwo)

#     Allocate absorption coefficients for each surface for each frequency

for D in range(1,sizeffttwo):       #This loop has a minimal impact on performance
    if inputarray[D,1] >= 0.0 or inputarray[D,1] < 88.0 :
        alphaground[D]=PF.tempalphaground[1]
    elif inputarray[D,1] >= 88.0 or inputarray[D,1] < 177.0 :
        alphaground[D]=PF.tempalphaground[2]
    elif inputarray[D,1] >= 177.0 or inputarray[D,1] < 355.0 :
        alphaground[D]=PF.tempalphaground[3]
    elif inputarray[D,1] >= 355.0 or inputarray[D,1] < 710.0 :
        alphaground[D]=PF.tempalphaground[4]
    elif inputarray[D,1] >= 710.0 or inputarray[D,1] < 1420.0 :
        alphaground[D]=PF.tempalphaground[5]
    elif inputarray[D,1] >= 1420.0 or inputarray[D,1] < 2840.0 :
        alphaground[D]=PF.tempalphaground[6]
    elif inputarray[D,1] >= 2840.0 or inputarray[D,1] < 5680.0 :
        alphaground[D]=PF.tempalphaground[7]
    elif inputarray[D,1] >= 5680.0 or inputarray[D,1] < inputarray[sizeffttwo,1]:
        alphaground[D]=PF.tempalphaground[8]


alphabuilding = np.zeros((PF.absorbplanes,sizeffttwo))

for W in range(1,PF.absorbplanes):        #These also look minimal
    for D in range(1,PF.absorbplanes):
        if  inputarray[D,1] >= 0.0 or inputarray[D,1] < 88.0:
            alphabuilding[W,D]=PF.tempalphabuilding[W,1]
        elif inputarray[D,1] >= 88.0 or inputarray[D,1] < 177.0:
            alphabuilding[W,D] = PF.tempalphabuilding [W,2]
        elif inputarray[D,1] >= 177.0 or inputarray[D,1] < 355.0 :
            alphabuilding[W,D] = tempalphabuilding[W,3]
        elif inputarray[D,1] >= 355.0 or inputarray[D,1] < 710.0 :
            alphabuilding[W,D] = tempalphabuilding[W,4]
        elif inputarray[D,1] >= 710.0 or inputarray[D,1] < 1420.0 :
            alphabuilding[W,D] = tempalphabuilding[W,5]
        elif inputarray[D,1] >= 1420.0 or inputarray[D,1] < 2840.0 :
            alphabuilding[W,D] = tempalphabuilding[W,6]
        elif inputarray[D,1] >= 2840.0 or inputarray[D,1] < 5680.0 :
            alphabuilding[W,D] = tempalphabuilding[W,7]
        elif inputarray[D,1] >= 5680.0 or inputarray[D,1] < inputarray[sizeffttwo,1] :
            alphabuilding[W,D] = tempalphabuilding[W,8]

#        Mesh the patches for the environment.  Include patching file. 
#if PF.radiosity == 1 :
##      import SingleBuildingGeometry
#      diffusion=percentdiffuse
#      diffusionground=0.0
#else:
#      diffusion=0.0
#      diffusionground=0.0

diffusionground = 0.0
if PF.radiosity:  # If it exists as a non-zero number
      import SingleBuildingGeometry
      diffusion = PF.radiosity
else:
      diffusion = 0.0

count=0

#     Loop through the intial ray locations
########################################################################################################################
########################################################################################################################
########################################################################################################################

print('began rays')
#ray = 606
#for ray in range(RAYMAX):
for ray in range(605,607):
      hitcount=0
      #ray = 606
      tmpsum=0.0
      doublehit=0
      ampinitial=inputarray[:,0]/normalization
      phaseinitial=inputarray[:,1]
      #Vinitial=np.array([boomarray[ray,0],boomarray[ray,1],boomarray[ray-1,2]])     #Where code diverges
      if (PF.h < (2*PF.radius)): 
            print('h is less than 2r')
            break
      F=Finitial
      #veci=Vinitial
      veci = boomarray[ray,:]
      # Making small steps along the ray path.  For each step we should return, 
      # location, phase and amplitude
      #for I in range(PF.IMAX):
      for I in range(15):
            dxreceiver=HUGE
            #print(veci)
            # Find the closest sphere and store that as the distance
            #for Q in range(0,RPS.arraysize):
            for R in ears:
                  #tempreceiver=fun.SPHERECHECK(receiverarray[Q],radius2,F,veci)
                  tempreceiver = R.SphereCheck(radius2,F,veci)
                  if (receiverhit >= 1):  #if you hit a receiver last time, don't hit it again
                        if np.all(R.position ==lastreceiver):
                        #if(   lastreceiver[0]==receiverarray[Q,0] and      lastreceiver[1]==receiverarray[Q,1] and  lastreceiver[2]==receiverarray[Q,2]):
                              tempreceiver=HUGE
                        #if(  F[0]==checkdirection[0] and  F[1] == checkdirection[1] and F[2] == checkdirection[2]):
                        #print(F)
                        #print(checkdirection)
                        #print(F == checkdirection)
                        #print(np.all(F == checkdirection))
                        if np.all(F == checkdirection):
                              #OC[0]=receiverarray[Q,0]-veci[0]
                              #OC[1]=receiverarray[Q,1]-veci[1]
                              #OC[2]=receiverarray[Q,2]-veci[2]
                              OC = R.position - veci
                              #OCLength=OC[0]*OC[0]+OC[1]*OC[1]+OC[2]*OC[2]
                              OCLength = np.dot(OC,OC)
                              #print('OCLength Orig',OCLength)
                              if(OCLength < radius2):
                                    tempreceiver=HUGE
                  if(receiverhit >= 2):
                        #if(lastreceiver2[0]== receiverarray[Q,0] and lastreceiver2[1]==receiverarray[Q,1] and lastreceiver2[2]==receiverarray[Q,2]):
                        if np.all(R.position == lastreceiver):
                              tempreceiver=HUGE
                  if (tempreceiver < dxreceiver):   
                        dxreceiver=tempreceiver
                        receiverpoint= R.position
                        #receiverpoint[0]=receiverarray[Q,0]
                        #receiverpoint[1]=receiverarray[Q,1]
                        #receiverpoint[2]=receiverarray[Q,2]
                  elif (tempreceiver== dxreceiver and tempreceiver != HUGE):
                        receivercheck=tempreceiver
                        #print('okay, does this one happen?')           
                        #print('receivercheck',receivercheck)
                        if np.all(R.position==receiverpoint):
                        #if(receiverarray[Q,0]==receiverpoint[0] and receiverarray[Q,1]==receiverpoint[1] and receiverarray[Q,2]==receiverpoint[2]):
                              doublehit=0
                        else:
                              receiverpoin2 = R.position
                              #receiverpoint2[0]=receiverarray[Q,0]
                              #receiverpoint2[1]=receiverarray[Q,1]
                              #receiverpoint2[2]=receiverarray[Q,2]
                              doublehit=1
            #      tempreceiver=fun.SPHERECHECK(receiverarray[Q],radius2,F,veci)
            #      if (receiverhit >= 1):  #if you hit a receiver last time, don't hit it again
            #            if(   lastreceiver[0]==receiverarray[Q,0] and      lastreceiver[1]==receiverarray[Q,1] and  lastreceiver[2]==receiverarray[Q,2]):
            #                  tempreceiver=HUGE
            #            if(  F[0]==checkdirection[0] and  F[1] == checkdirection[1] and F[2] == checkdirection[2]):
            #                  OC[0]=receiverarray[Q,0]-veci[0]
            #                  OC[1]=receiverarray[Q,1]-veci[1]
            #                  OC[2]=receiverarray[Q,2]-veci[2] 
            #                  OCLength=OC[0]*OC[0]+OC[1]*OC[1]+OC[2]*OC[2]
            #                  #print('OCLength Orig',OCLength)
            #                  if(OCLength < radius2):
            #                        tempreceiver=HUGE
            #      if(receiverhit >= 2):
            #            #print('recHit > 2 happens')        #This does not happen, good
            #            if(lastreceiver2[0]== receiverarray[Q,0] and lastreceiver2[1]==receiverarray[Q,1] and lastreceiver2[2]==receiverarray[Q,2]):
            #                  tempreceiver=HUGE
            #      if (tempreceiver < dxreceiver):
            #            #print('Well duh, this clearly happens ') #It's not supposed to   
            #            dxreceiver=tempreceiver
            #            receiverpoint[0]=receiverarray[Q,0]
            #            receiverpoint[1]=receiverarray[Q,1]
            #            receiverpoint[2]=receiverarray[Q,2]
            #      elif (tempreceiver== dxreceiver and tempreceiver != HUGE):
            #            receivercheck=tempreceiver
            #            #print('okay, does this one happen?')           
            #            #print('receivercheck',receivercheck)
            #            if(receiverarray[Q,0]==receiverpoint[0] and receiverarray[Q,1]==receiverpoint[1] and receiverarray[Q,2]==receiverpoint[2]):
            #                  doublehit=0
            #            else:
            #                  receiverpoint2[0]=receiverarray[Q,0]
            #                  receiverpoint2[1]=receiverarray[Q,1]
            #                  receiverpoint2[2]=receiverarray[Q,2]
            #                  doublehit=1
            #testing no Loop
            
            tempreceivernew=fun.SPHERECHECKNEW(receiverarray,radius2,F,veci)
            if (receiverhit >= 1):  #if you hit a receiver last time, don't hit it again
                  #if(any((receiverarray[:]==lastreceiver).all(1))):
                  if(np.all(receiverarray[:]==lastreceiver)):
                        tempreceiver=HUGE
                  #if((F[:]==checkdirection).all()):
                  if np.all(F[:]==checkdirection):
                        OCnew=receiverarray-veci
                        OCLengthnew=np.sum(OCnew*OCnew, axis=1)
                        print(OCLengthnew)
                        if(any(OCLengthnew) < radius2):
                              tempreceiver=HUGE
            if(receiverhit >= 2):
                        #print('recHit > 2 happens')        #This does not happen, good
                  #if(any((receiverarray[:]==lastreceiver).all(1))):
                  if(any((receiverarray[:]==lastreceiver).all(1))):
                        tempreceiver=HUGE
            if (any(tempreceivernew < dxreceiver)):
                  #print('This happens Now')
                        #print('Well duh, this clearly happens ') #It's not supposed to   
                  dxreceiver= min(tempreceivernew)
                  #print('dxreceiver',dxreceiver)
                  #### everything up to here looks good#### need to figure out how to get the index for the min now. 
                  receiverpoint[0]=receiverarray[Q,0]
                  receiverpoint[1]=receiverarray[Q,1]
                  receiverpoint[2]=receiverarray[Q,2]
            elif (tempreceiver== dxreceiver and tempreceiver != HUGE):
                  receivercheck=tempreceiver
                        #print('okay, does this one happen?')           
                        #print('receivercheck',receivercheck)
                  if(receiverarray[Q,0]==receiverpoint[0] and receiverarray[Q,1]==receiverpoint[1] and receiverarray[Q,2]==receiverpoint[2]):
                        doublehit=0
                  else:
                        receiverpoint2[0]=receiverarray[Q,0]
                        receiverpoint2[1]=receiverarray[Q,1]
                        receiverpoint2[2]=receiverarray[Q,2]
                        doublehit=1
            #     Check Intersection with ground plane
            GROUNDN=GROUNDABC
            GROUNDVD=GROUNDN[0]*F[0]+GROUNDN[1]*F[1]+GROUNDN[2]*F[2]
            if (groundhit==1):
                  dxground=HUGE
            elif (GROUNDVD!=0.0):
                  GROUNDVO=((GROUNDN[0]*veci[0]+GROUNDN[1]*veci[1]+GROUNDN[2]*veci[2])+GROUNDD)
                  dxground1=(-1.000)*GROUNDVO*(1.000)/GROUNDVD
                  dxground=dxground1
                  Vecip1=veci+dxground*np.array(F)
                  tmp=(GROUNDABC[0]*Vecip1[0]+GROUNDABC[1]*Vecip1[1]+GROUNDABC[2]*Vecip1[2]+GROUNDD)                  
                  if (dxground < 0.0):
                        dxground=HUGE
            else:
                  dxground=HUGE
            #     Check intersection with building
            dxbuilding=HUGE
            hit=0
            planehit=0
            #     Check intersection with Boxes
            t = time.time()
            for Q in range(0,BG.Boxnumber):
                  dxnear, dxfar, hit, planehit=fun.BOX(BG.Boxarraynear[Q], BG.Boxarrayfar[Q],veci,F)
                  #print('old',dxnear, dxfar, hit, planehit)
            #print('Box time loop: %.8f ' %(time.time()-t))
                  if (dxnear < dxbuilding):
                        dxbuilding=dxnear
                        Vecip1=veci+np.multiply(dxbuilding,F)
                        whichbox=Q
                        nbox=fun.PLANE(Vecip1, BG.Boxarraynear[whichbox],BG.Boxarrayfar[whichbox], planehit)
                        #print(Vecip1, BG.Boxarraynear[b],BG.Boxarrayfar[b], planehit[b])
            #t = time.time()
            #dxnearnew, dxfarnew, hitnew, planehitnew=fun.BOXnew(BG.Boxarraynear, BG.Boxarrayfar,veci,F)
            ##b=np.argmin(dxnearnew)
            #print('Box time no loop: %.8f ' %(time.time()-t))
           # print('new',np.amin(dxnearnew), dxfarnew, hitnew, planehitnew,b,np.amin(dxnearnew))
            #if (dxnearnew[b] < dxbuilding):
            #      dxbuilding=dxnearnew[b]
            #      Vecip1=veci+np.multiply(dxbuilding,F)
            #      print(Vecip1, BG.Boxarraynear[b],BG.Boxarrayfar[b], planehit[b])
            #      nboxnew=fun.PLANE(Vecip1, BG.Boxarraynear[b],BG.Boxarrayfar[b], planehit[b])
            #      print(nboxnew)
            #print('Box time no loop: %.8f ' %(time.time()-t))
             #     Check intersection with Triangles
            if(BG.TriangleNumber > 0):
                  for Q in range(0, BG.TriangleNumber):
                        dxnear, behind = fun.Polygon(veci,F,Q,3,TriangleNumber,PointNumbers,Trianglearray,BuildingPoints,normal,FaceNormalNo,FaceNormals)
                        if (dxnear < dxbuilding):
                              dxbuilding=dxnear
                              nbox=normal
                              whichbox=Q
            #    Check intersection with Squares
            if(BG.SquareNumber>0):
                  for Q in range(0,BG.SquareNumber):
                        dxnear, behind=Polygon(veci,F,Q,4,SquareNumber,PointNumbers,SquareArray,BuildingPoints,normal,FaceNormalNo,FaceNormals)
                        if (dxnear < dxbuilding):
                              dxbuilding=dxnear
                              nbox=normal
                              #print('nbox from squares', nbox)
                              whichbox=Q
            buildinghit=0
            receiverhit=0
            groundhit=0
            #     Check to see if ray hits within step size
            if (dxreceiver < PF.h or dxground < PF.h or dxbuilding < PF.h):
                  dx=min(dxreceiver,dxground,dxbuilding)
                  tmpsum=tmpsum+dx
                  #     if the ray hits a receiver, store in an array.  If the ray hits twice
                  #     Create two arrays to store in.
                  if (dx==dxreceiver):
                        print('hit receiver at step ',I)
                        #sum=sum+1                          # this is a built in name. we also don't seem to be using this for anything else
                        #print(veci,dx,F)
                        Vecip1=veci+np.multiply(dx,F)
                        veci=Vecip1
                        print(veci)
                        receiverhit=1
                        checkdirection=F
                        if(doublehit==1):
                              receiverhit=2
                        hitcount=hitcount+1
                        #print('hit receiver',sum,tmpsum,receiverpoint)
                        for W in range(0,sizeffttwo):
                              #print('airabsorb: ',airabsorb[W])
                              m=airabsorb[W]
                              lamb=PF.soundspeed/inputarray[W,1]
                              phasefinal=phaseinitial[W]-(twopi*dx)/lamb   
                              #print('ampinit: ',ampinitial[W])
                              #print('alphno: ',' (1- ',alphanothing ,' ) ')
                              #print('oth: ',np.exp(-m*dx))
                              ampfinal=ampinitial[W]*(1-alphanothing[W])*np.exp(-m*dx)
                              ampinitial[W]=ampfinal
                              phaseinitial[W]=phasefinal%twopi
                              if (phaseinitial[W]>=PI):
                                    phaseinitial[W]=phaseinitial[W]-twopi
                              if(doublehit==1):
                                    if(W==0):   #Used this loop twice before
                                          outputarray1=np.zeros((sizeffttwo, 6))
                                          dhoutputarray1=np.zeros((sizeffttwo,6))  
                                    outputarray1[W,0]=inputarray[W,0]
                                    outputarray1[W,1]=receiverpoint[0]
                                    outputarray1[W,2]=receiverpoint[1]
                                    outputarray1[W,3]=receiverpoint[2]
                                    outputarray1[W,4]=ampinitial[W]/2.0
                                    outputarray1[W,5]=phaseinitial[W]
                                    dhoutputarray1[W,0]=inputarray[W,0]
                                    dhoutputarray1[W,1]=receiverpoint2[0]
                                    dhoutputarray1[W,2]=receiverpoint2[1]
                                    dhoutputarray1[W,3]=receiverpoint2[2]
                                    dhoutputarray1[W,4]=ampinitial[W]/2.0
                                    dhoutputarray1[W,5]=phaseinitial[W]
                                    lastreceiver[0]=receiverpoint[0]
                                    lastreceiver[1]=receiverpoint[1]
                                    lastreceiver[2]=receiverpoint[2]
                                    lastreceiver2[0]=receiverpoint2[0]
                                    lastreceiver2[1]=receiverpoint2[1]
                                    lastrecever2[2]=receiverpoint2[2]
                              else:
                                    #print('this happens outputarray')
                                    if(W==0):
                                          outputarray1=np.zeros((sizeffttwo,6))
                                    outputarray1[W,0]=inputarray[W,0]
                                    outputarray1[W,1]=receiverpoint[0]
                                    outputarray1[W,2]=receiverpoint[1]
                                    outputarray1[W,3]=receiverpoint[2]
                                    outputarray1[W,4]=ampinitial[W]
                                    outputarray1[W,5]=phaseinitial[W]
                                    lastreceiver[0]=receiverpoint[0]
                                    lastreceiver[1]=receiverpoint[1]
                                    lastreceiver[2]=receiverpoint[2]
                        #print('assigned to outputarray1')
                        #print(outputarray1[0,1], outputarray1[1,3], outputarray1[1,4])
                        #print('temparray before: \n',temparray)
                        temparray=fun.receiverHITFUNC(sizefft,outputarray1,RPS.arraysize,temparray)
                        print('non-double hit')
                        #print('temparray after: \n',temparray)
                        #print('receiverHITFUNC completed')
                        if (doublehit==1):
                              print('doublehit')
                              temparray=fun.receiverHITFUNC(sizefft,dhoutputarray1,RPS.arraysize,temparray)
                              count+=1
                        count+=1
                        outputarray1=None
                        if(doublehit==1):
                              dhoutputarray1=None
                  #     If the ray hits the ground then bounce off the ground and continue
                  if (abs(dx-dxground)< 10.0**(-13.0)):
                        Vecip1=veci+np.multiply(dxground,F)
                        tmp=(GROUNDABC[0]*Vecip1[0]+GROUNDABC[1]*Vecip1[1]+GROUNDABC[2]*Vecip1[2]+GROUNDD)
                        if(tmp != GROUNDD): 
                              Vecip1[2]=0.0
                        print('hit ground at ',I)
                        veci=Vecip1
                        #print(veci)
                        dot1=(F[0]*nground[0]+F[1]*nground[1]+F[2]*nground[2])
                        n2=(nground[0]*nground[0]+nground[1]*nground[1]+nground[2]*nground[2])
                        r=np.around(F-2.0*(dot1/n2)*nground,8)
                        length=np.sqrt(r[0]*r[0]+r[1]*r[1]+r[2]*r[2])
                        F=np.around([r[0],r[1],r[2]],8)
                        groundhit=1
                        twopidx=twopi*dxground
                        #     Loop through all the frequencies
                        phaseinitial, ampinitial = update(airabsorb,frecuencias[:,0],phaseinitial,dxground,ampinitial,alphaground,diffusionground)
                        if(PF.radiosity==1 and (diffusionground!=0.0)):
                              for Q in range (0,PatchNo):
                                    if (formfactors[0,Q,1]==1):
                                          if(veci[0]<=(patcharray[Q,W,0]+0.5*patcharray[Q,W,3]) and veci[0]>=(patcharray[Q,W,0]-0.5*patcharray[Q,W,3])):
                                                if(veci[1]<=(patcharray[Q,W,1]+0.5*patcharray[Q,W,4]) and veci[1]>=(patcharray[Q,W,1]-0.5*patcharray[Q,W,4])):
                                                      if(veci[2]<=(patcharray[Q,W,2]+0.5*patcharray[Q,W,5]) and veci[2]>=(patcharray[Q,W,2]-0.5*patcharray[Q,W,5])):
                                                            temp2=complex(abs(patcharray[Q,W,6])*np.exp(XJ*patcharray[Q,W,7]))
                                                            temp3=complex(abs(ampinitial[W]*(1.0-alphaground[W])*diffusionground*exp(-m*dxground))*exp(1j*phasefinal))
                                                            temp4=temp2+temp3
                                                            patcharray[Q,W,6]=abs(temp4)
                                                            patcharray[Q,W,7]=np.arctan(temp4.imag,temp4.real)

                        #for W in range(0,sizeffttwo):
                        #      m=airabsorb[W]
                        #      lamb=PF.soundspeed/inputarray[W,0]
                        #      phasefinal=phaseinitial[W]-(twopidx)/lamb
                        #      ampfinal=ampinitial[W]*(1.0-alphaground[W])*(1.0-diffusionground)*np.exp(-m*dxground)
                        #      phaseinitial[W]=phasefinal%twopi
                        #      if (phaseinitial[W]>PI):
                        #            phaseinitial[W]=phaseinitial[W]-twopi
                        #      if(PF.radiosity==1 and (diffusionground!=0.0)):
                        #            for Q in range (0,PatchNo):
                        #                  if (formfactors[0,Q,1]==1):
                        #                        if(veci[0]<=(patcharray[Q,W,0]+0.5*patcharray[Q,W,3]) and veci[0]>=(patcharray[Q,W,0]-0.5*patcharray[Q,W,3])):
                        #                              if(veci[1]<=(patcharray[Q,W,1]+0.5*patcharray[Q,W,4]) and veci[1]>=(patcharray[Q,W,1]-0.5*patcharray[Q,W,4])):
                        #                                    if(veci[2]<=(patcharray[Q,W,2]+0.5*patcharray[Q,W,5]) and veci[2]>=(patcharray[Q,W,2]-0.5*patcharray[Q,W,5])):
                        #                                          temp2=complex(abs(patcharray[Q,W,6])*np.exp(XJ*patcharray[Q,W,7]))
                        #                                          temp3=complex(abs(ampinitial[W]*(1.0-alphaground[W])*diffusionground*exp(-m*dxground))*exp(1j*phasefinal))
                        #                                          temp4=temp2+temp3
                        #                                          patcharray[Q,W,6]=abs(temp4)
                        #                                          patcharray[Q,W,7]=np.arctan(temp4.imag,temp4.real)
                        #      ampinitial[W]=ampfinal   
                  #     if the ray hits the building then change the direction and continue
                  if (dx==dxbuilding):
                        Vecip1=veci+dx*np.array(F)
                        veci=Vecip1
                        print('hit building at step ',I)
                        #print(veci)
                        n2=(nbox[0]*nbox[0]+nbox[1]*nbox[1]+nbox[2]*nbox[2])
                        nbuilding=nbox/np.sqrt(n2)
                        dot1=(F[0]*nbuilding[0]+F[1]*nbuilding[1]+F[2]*nbuilding[2])
                        r=F-2.0*(dot1/n2)*nbuilding
                        length=np.sqrt(r[0]*r[0]+r[1]*r[1]+r[2]*r[2])
                        F=[r[0],r[1],r[2]]
                        buildinghit=1
                        twopidx=twopi*dx
                        #phaseNew, amplitudeNew = update(airabsorb,frecuencias[:,0],phaseinitial,dx,ampinitial,alpha,diffusion)
                        #m=airabsorb[:]
                        #lamb=PF.soundspeed/inputarray[:,0]                
                        #phasefinal=phaseinitial[:]-(twopidx)/lamb
                        #ampfinal=ampinitial[:]*(1.0-alpha)*(1.0-diffusion)*np.exp(-m*dx)
                        #phaseinitial[:]=phasefinal%twopi
                        #phaseinitial = np.where((phaseinitial[:]>PI), phaseinitial[:]-twopi, phaseinitial)
                        #ampinitial[:]=ampfinal
                        if PF.complexabsorption:
                              if PF.absorbplanes==2:
                                    if (veci[2]>0.0) and (veci[2]<height1):
                                          alpha = alphabuilding[0,:]

                                    elif(veci[2]>height1 and veci[2]<=height2):
                                          alpha=alphabuilding[1,:]
                              if(PF.absorbplanes==3):
                                    if(veci[2]>height2 and veci[2] <=height3):
                                          alpha=alphabuilding[2,:]
                              if(PF.absorbplanes==4):
                                    if(veci[2]>height3):
                                          alpha=alphabuilding[4,:]
                        else:
                              alpha=alphabuilding[0,:]
                        phaseinitial, ampinitial = update(airabsorb,frecuencias[:,0],phaseinitial,dx,ampinitial,alpha,diffusion)
                        #m=airabsorb[W]
                        #lamb=PF.soundspeed/inputarray[W,0]                
                        #phasefinal=phaseinitial[W]-(twopidx)/lamb
                        #ampfinal=ampinitial[W]*(1.0-alpha)*(1.0-diffusion)*np.exp(-m*dx)
                        #phaseinitial[W]=phasefinal%twopi
                        #if (phaseinitial[W]>PI):
                        #      phaseinitial[W]=phaseinitial[W]-twopi
                        #ampinitial[W]=ampfinal
#                        for W in range(0,sizeffttwo):
#                              if(PF.complexabsorption==1):
#                                    if (PF.absorbplanes==2):
#                                          if(veci[2]>0.0 and veci[2]< height1):
#                                                alpha=alphabuilding[0,W]
#                                          elif(veci[2]>height1 and veci[2]<=height2):
#                                                alpha=alphabuilding[1,W]
#                                    if(PF.absorbplanes==3):
#                                          if(veci[2]>height2 and veci[2] <=height3):
#                                                alpha=alphabuilding[2,W]
#                                    if(PF.absorbplanes==4):
#                                          if(veci[2]>height3):
#                                                alpha=alphabuilding(4,W)
#                              else:
#                                    alpha=alphabuilding[0,W]
#                              m=airabsorb[W]
#                              lamb=PF.soundspeed/inputarray[W,0]                
#                              phasefinal=phaseinitial[W]-(twopidx)/lamb
#                              ampfinal=ampinitial[W]*(1.0-alpha)*(1.0-diffusion)*np.exp(-m*dx)
#                              phaseinitial[W]=phasefinal%twopi
#                              if (phaseinitial[W]>PI):
#                                    phaseinitial[W]=phaseinitial[W]-twopi
#                              ampinitial[W]=ampfinal
            else:
#     If there was no interaction with buildings then proceed with one step. 
                  tmpsum=tmpsum+PF.h
                  Vecip1=veci+(PF.h)*np.array(F)
                  veci=Vecip1
                  twopih=twopi*PF.h
#     Loop through all frequencies.
                  phaseinitial, ampinitial = update(airabsorb,frecuencias[:,0],phaseinitial,PF.h,ampinitial,alphanothing,0)  #temporary
                  #for W in range (0,sizeffttwo):
                  #      m=airabsorb[W]
                  #      #lamb=PF.soundspeed/inputarray[W,0]
                  #      lamb=PF.soundspeed/inputarray[W,0]
                  #      phasefinal=phaseinitial[W]-(twopih)/lamb
                  #      ampfinal=ampinitial[W]*(1-alphanothing)*np.exp(-m*PF.h)
                  #      #print('ampinit: ',ampinitial[W])
                  #      #print('ampfin: ',ampfinal[W])
                  #      ampinitial[W]=ampfinal[W]                 
                  #      phaseinitial[W]=phasefinal%twopi
                  #      if (phaseinitial[W] > PI):
                  #            phaseinitial[W]=phaseinitial[W]-twopi
      print('finished ray', ray + 1)
#      if ray == 609:
#            break
########################################################################################################################
########################################################################################################################
########################################################################################################################


#     Once all rays are complete.  Deallocate all arrays that are no longer needed

# Inefficient and causes problems for now. We can move these to a function to get ri of them easier, commenting out for now

#boomarray=None
#receiverarray=None
#ampinitial=None
#phaseinitial=None
      #Gk=np.zeros(PatchNo,sizeffttwo)
      #Gkminus1=np.zeros(PatchNo,sizeffttwo)
#COMEBACK FOR RADIOSITY
#       if (radiosity.eq.1)then
# C     If radiosity is turned on then do the energy exchange. 
#          KMAX=3
#          Npatch=10
#          DO 53 K=1,KMAX
#             DO 55 D=1,PatchNo
#                DO 54 W=1,sizeffttwo
#                   if (K.eq.1)then
#                      Gk(D,W)=cmplx(abs(patcharray(D,W,7)
#      *                    )*exp(XJ*patcharray(D,W,8)))
#                   else
#                      Gkminus1(D,W)=Gk(D,W)
#                      DO 56 I=1,PatchNo
#                         if (I.eq.1)then
#                            Gk(D,W)=0.0
#                         else
#                            if (formfactors(D,I,2).eq.1.0)then 
#                               alpha=alphaground(W)
#                            elseif (formfactors(D,I,2).eq.2.0)then
#                               if( complexabsorption.eq.1)then
#                                  if(absorbplanes.eq.2)then
#                                  if(patcharray(I,1,3).gt.0.0.and.
#      *                                patcharray(I,1,3).le.height1)then
#                                     alpha=alphabuilding(1,W)
#                                  elseif(patcharray(I,1,3).gt.height1
#      *                                   .and.patcharray(I,1,3).le.
#      *                                   height2)then
#                                     alpha=alphabuilding(2,W)
#                                  endif
#                                  endif
#                                  if(absorbplanes.eq.3)then
#                                  if(patcharray(I,1,3).gt.height2
#      *                                   .and.patcharray(I,1,3).le.
#      *                                   height3)then
#                                     alpha=alphabuilding(3,W)
#                                  endif
#                                  endif 
#                                  if(absorbplanes.eq.4)then
#                                  if(patcharray(I,1,3).gt.height3)
#      *                                   then
#                                     alpha=alphabuilding(4,W)
#                                  endif
#                                  endif
#                               else
#                                  alpha=alphabuilding(1,W)
#                               endif
#                            endif
#                            m=airabsorb(W)
#                            temp2=(1-alpha)*exp(-m*formfactors(D,I,3))*
#      *                          formfactors(D,I,1)*Gkminus1(D,W)*exp(
#      *                          -XJ*twopi*inputarray(W,1)*formfactors
#      *                          (D,I,3)/soundspeed)
#                            Gk(D,W)=Gk(D,W)+temp2
#                         endif
#  56                  CONTINUE
#                   endif
#  54            CONTINUE
#                print*, 'finished patch', D, 'of',PatchNo
#  55         CONTINUE
#             print*, arraysize,PatchNo,sizefft
# C     Do energy exchange with other receivers
#             DO 50 D=1,arraysize
#                DO 51 Q=1,PatchNo
#                   Rlm=0.0
#                   DO 58 I=1,Npatch
#                      DO 59 J=1,Npatch
#                         DO 60 S=1,Npatch
#                            tmp1=((patcharray(Q,1,1)-.5*patcharray
#      *                          (Q,1,4)+(patcharray(Q,1,4)/Npatch)
#      *                          *(I-.5))-temparray(D,1,1))*((patcharray(
#      *                          Q,1,1)-.5*patcharray(Q,1,4)+(patcharray(
#      *                          Q,1,4)/Npatch)*(I-.5))-temparray(D,1,1))
#                            tmp2=((patcharray(Q,1,2)-.5*patcharray
#      *                          (Q,1,5)+(patcharray(Q,1,5)/Npatch)
#      *                          *(J-.5))-temparray(D,1,2))*((patcharray(
#      *                          Q,1,2)-.5*patcharray(Q,1,5)+(patcharray(
#      *                          Q,1,5)/Npatch)*(J-.5))-temparray(D,1,2))
#                            tmp3=((patcharray(Q,1,3)-.5*patcharray
#      *                          (Q,1,6)+(patcharray(Q,1,6)/Npatch)
#      *                          *(S-.5))-temparray(D,1,3))*((patcharray(
#      *                          Q,1,3)-.5*patcharray(Q,1,6)+(patcharray(
#      *                          Q,1,6)/Npatch)*(S-.5))-temparray(D,1,3))
#                            Rlm=Rlm+1.0/(NPatch*Npatch*Npatch)*sqrt(tmp1+
#      *                          tmp2+tmp3)
#  60                     Continue
#  59                  CONTINUE
#  58               CONTINUE
#                   Patchlength=sqrt(((patcharray(Q,1,1)-temparray(D,1,1))
#      *                 *(patcharray(Q,1,1)-temparray(D,1,1)))+((patchar
#      *                 ray(Q,1,2)-temparray(D,1,2))*(patcharray(Q,1,2)
#      *                 -temparray(D,1,2)))+((patcharray(Q,1,3)-temparray
#      *                (D,1,3))*(patcharray(Q,1,3)-temparray
#      *                (D,1,3))))
#                   Finitial(1)=(patcharray(Q,1,1)-temparray(D,1,1))
#                   Finitial(2)=(patcharray(Q,1,2)-temparray(D,1,2))
#                   Finitial(3)=(patcharray(Q,1,3)-temparray(D,1,3))
#                   F=(/Finitial(1)/Rlm,Finitial(2)/Rlm,
#      *                 Finitial(3)/Rlm/)
#                   dxbuilding=HUGE
# C     Check to see that the receiver is visible by patches. 
#                   DO 57 I=1,boxnumber,1 
#                      call BOX(boxarraynear(I,1:3),
#      *                    Boxarrayfar(I,1:3),temparray(D,1,1:3),
#      *                    F,dxnear,dxfar,hit, planehit)
#                      if (dxnear.lt.dxbuilding)then
#                         dxbuilding=dxnear
#                      endif
#                      if ((temparray(D,1,1).gt.boxarraynear(I,1)
#      *                    .and.temparray(D,1,2).gt.boxarraynear(I,2)
#      *                    .and.temparray(D,1,3).gt.boxarraynear(I,3))
#      *                    .and.(temparray(D,1,1).lt.boxarrayfar(I,1)
#      *                    .and.temparray(D,1,2).lt.boxarrayfar(I,2)
#      *                    .and.temparray(D,1,3).lt.boxarrayfar(I,3)))
#      *                    then
#                         dxbuilding=-1.0
#                      endif
#  57               CONTINUE
#                   if(TriangleNumber.gt.0)then
#                      DO 67 I=1,TriangleNumber,1 
#                         call Polygon(temparray(D,1,1:3),F,I,3,
#      *                       TriangleNumber,PointNumbers,Trianglearray,
#      *                       BuildingPoints,normal,FaceNormalNo,
#      *                       FaceNormals,dxnear,behind)
#                         if (dxnear.lt.dxbuilding)then
#                            dxbuilding=dxnear
#                         endif
#  67                  CONTINUE
#                   endif
#                   if(SquareNumber.gt.0)then
#                      DO 68 I=1,SquareNumber,1 
#                         call Polygon(temparray(D,1,1:3),F,I,4,
#      *                       SquareNumber,PointNumbers,SquareArray,
#      *                       BuildingPoints,normal,FaceNormalNo,
#      *                       FaceNormals,dxnear,behind)
#                         if (dxnear.lt.dxbuilding)then
#                            dxbuilding=dxnear
#                         endif
#  68                  CONTINUE
#                   endif
#                   if(PolyBuilding.gt.0)then
#                      DO 69 I=1,PolyBuilding
# C     Check that the receivers are not inside the building
#                         CALL INSIDECHECK(temparray(D,1,1:3),
#      *                       BuildingPoints,PointNumbers,F,Trianglearray
#      *                       ,SquareArray,TriangleNumber,SquareNumber,
#      *                       TriangleSequence,SquareSequence,Triangles,
#      *                       Squares,PolyBuilding,I,inside,FaceNormalNo,
#      *                       FaceNormals)
#                         if(inside.eq.1)then
#                            dxbuilding=-1.0
#                         endif
#  69                  CONTINUE
#                   endif
#                   vec3=FaceNormals(int(patcharray(Q,1,10)),1:3)
#                   PIRlm2=PI*Rlm*Rlm
#                   DO 52 W=1,sizeffttwo
#                      if (Gk(Q,W).ne.0.0)then   
#                         if(dxbuilding.lt.Patchlength)then
#                            Ek=0.0
#                         elseif(dxbuilding.ge.Patchlength)then
#                            length=sqrt(vec3(1)*vec3(1)+
#      *                          vec3(2)*vec3(2)+vec3(3)*vec3(3))
#                            cosxilm=(vec3(1)*F(1)+vec3(2)*F(2)+vec3(3)*
#      *                          F(3))/(Rlm*length)
#                            m=airabsorb(W)
#                            Ek=exp(-m*Rlm)*((cosxilm*Gk(Q,W)*exp(-XJ*
#      *                          twopi*inputarray(W,1)*Rlm/soundspeed))/
#      *                          (PIRlm2))
#                         endif
#                         temp2=cmplx(abs(temparray(D,W,5))*exp(XJ*
#      *                       temparray(D,W,6)))
#                         temp3=Ek+temp2
#                         temparray(D,W,5)=ABS(temp3)
#                         temparray(D,W,6)=ATAN2(imagpart(temp3)
#      *                       ,realpart(temp3))
#                      endif
#  52               CONTINUE
#  51            CONTINUE
#                print*, 'finished receiver', D, 'of', arraysize
#  50         CONTINUE
#  53      CONTINUE
#       endif

#Reconstruct the time signal
#timetemparray=fun.TIMERECONSTRUCT(sizefft, timearray, RPS.Receiver.arraysize, temparray)
##print('temparray: ', temparray[0:20])
##print('timearray: ',timearray[0,0,0:3])
##     Write out time signatures for each receiver. 
#OPFile=open(PF.OUTPUTFILE,"w")
#true=fun.Header(PF.OUTPUTFILE)
#OPFile=open(PF.OUTPUTFILE,"a")      #redefining to print both Header and TimeHeader
##print(RPS.arraysize1,'Arraysize')
#if(RPS.planenum>=1):
#      for W in range(0,sizefft):
#            true=fun.TimeHeader(OPFile,timetemparray[0,W,3],RPS.sizex1,RPS.sizey1,RPS.sizez1,RPS.planename1)
#            for D in range(0,RPS.arraysize1):
#                  #if W==1:
#                        #print(D)
#                  OPFile.write('\t%f\t%f\t%f\t%f\n' %(timetemparray[D,W,0],timetemparray[D,W,1],timetemparray[D,W,2],timetemparray[D,W,4]))
#                  #print('finished time',timetemparray[0,W,3] )
##print(timetemparray[1,1,0:2])                  

# New
#for R in ears:
#    #print(R.magnitude.shape)
#    #R.magnitude = np.sum(R.magnitude,axis=0)
#    #R.direction = np.sum(R.direction,axis=0)
#    #timetemparray=TIMERECONSTRUCT(sizefft, RPS.Receiver.arraysize, R.magnitude,R.direction)
#    R.timesignal = TIMERECONSTRUCT(sizefft,R.magnitude,R.direction)
#
#OPFile=open(PF.OUTPUTFILE,"w")
#true=fun.Header(PF.OUTPUTFILE)
#OPFile=open(PF.OUTPUTFILE,"a")      #redefining to print both Header and TimeHeader
#
#for W in range(sizefft):
#    true=fun.TimeHeader(OPFile,timearray[W],RPS.sizex1,RPS.sizey1,RPS.sizez1,RPS.planename1)
#    for R in ears:
#        OPFile.write('\t%f\t%f\t%f\t%f\n' %(R.position[0],R.position[1],R.position[2],R.timesignal[W]))
#
#OPFile.close()

# Newest
for R in ears:
    R.timeReconstruct(sizefft)

OPFile=open(PF.OUTPUTFILE,"w")
true=fun.Header(PF.OUTPUTFILE)
OPFile=open(PF.OUTPUTFILE,"a")      #redefining to print both Header and TimeHeader

for W in range(sizefft):
    true=fun.TimeHeader(OPFile,timearray[W],RPS.sizex1,RPS.sizey1,RPS.sizez1,RPS.planename1)
    for R in ears:
        OPFile.write('\t%f\t%f\t%f\t%f\n' %(R.position[0],R.position[1],R.position[2],R.timesignal[W]))

OPFile.close()



#if(RPS.planenum>=2):
#      W=0
#      while (W<sizefft):
#            true=fun.TimeHeader(OPFile,timetemparray[0,W,3],sizex2,sizey2,sizez2,planename2)
#            D=RPS.arraysize1
#            while (D<RPS.arraysize1+RPS.arraysize2):
#                  OPFile.write(timetemparray[D,W,0:2],timetemparray[D,W,4])
#                  D+=1
#            W+=1
#if(RPS.planenum>=5):
#      W=0
#      while (W<sizefft):
#            true=fun.TimeHeader(OPFile,timetemparray[0,W,3],sizex5,sizey5,sizez5,planename5)
#            D=arraysize1+arraysize2+arraysize3+arraysize4
#            while(D<(arraysize1+arraysize2+arraysize3+arraysize4+arraysize5)):
#                  OPFile.write(timetemparray[D,W,0:2],timetemparray[D,W,4])
#                  D+=1
#            W+=1
OPFile.close()

