# RayTrace
# version 1.1.0

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
#import GeometryParser as BG

import time
t = time.time()
      
# What it does not do
"""
      Interacts with geometry parser
      Have a way of reading in complex geometries - Yes, but not yet integrated
      Anything resembling radiosity
"""

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



def updateFreq(dx,alpha,diffusion):
      """
      Update ray phase and amplitude
      """
      global phase,amplitude        # works directly

      twopidx = twopi * dx
      tempphase = phase[:] - (twopidx/lamb)
      tempphase %= twopi

      phase = np.where( (tempphase > PI),      tempphase-twopi,      tempphase)
      amplitude *= ((1.0-alpha) * (1.0-diffusion) * np.exp(airabsorb*dx))

# port and import receiver file
receiverhit=0
groundhit=0

# Initialize counters 
PI = np.pi
twopi = PI*2
XJ=(0.0,1.0)
radius2 = PF.radius**2
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

# Allocate the correct size to the signal and fft arrays
sizefft=K
sizeffttwo=sizefft//2
outputsignal=np.fft.fft(inputsignal,sizefft)
#ampinitial=np.empty(sizeffttwo)
#phaseinitial=np.empty(sizeffttwo)

#       Create initial signal 
frecuencias = initial_signal(sizefft,outputsignal)      # Equivalent to inputarray in original
airabsorb=fun.ABSORPTION(PF.ps,frecuencias[:,0],PF.hr,PF.Temp)        #sizeffttwo
lamb = PF.soundspeed/frecuencias[:,0]     # Used for updating frequencies in update function
timearray = np.arange(K) /PF.Fs

#       Set initial values
Vinitial =  np.array([PF.xinitial,PF.yinitial,PF.zinitial])
xiinitial  =np.cos(PF.phi)*np.sin(PF.theta)
ninitial   =np.sin(PF.phi)*np.sin(PF.theta)
zetainitial=np.cos(PF.theta)
length =    np.sqrt(xiinitial*xiinitial+ninitial*ninitial+zetainitial*zetainitial)
Finitial=np.array([xiinitial,ninitial,zetainitial])
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

# Making specific receiver points using receiver module
RPS.Receiver.initialize(PF.RecInput)
ears = RPS.Receiver.rList           #easier to write
for R in ears:          #hotfix
      R.magnitude = np.zeros(sizeffttwo)
      R.direction = np.zeros(sizeffttwo)
RPS.arraysize = RPS.Receiver.arraysize
receiverpoint  = np.zeros(3)
receiverpoint2 = np.zeros(3)

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

#receiverarray1=None                #It looks like in the new version we make this, don't use it, then delete it
#if RPS.planenum >=2 :
#    RPS.receiverarray2=None
#if RPS.planenum >=3 :
#    RPS.receiverarray3=None
#if RPS.planenum >=4 :
#    RPS.receiverarray4=None
#if RPS.planenum >=5 :
#    RPS.receiverarray5=None
#if RPS.planenum >=6 :
#    RPS.receiverarray6=None
#if RPS.planenum >=7 :
#    RPS.receiverarray7=None

#       Initialize normalization factor 
normalization=(PI*radius2)/(PF.boomspacing**2) 
temparray=np.empty((    RPS.Receiver.arraysize,sizeffttwo,6))
timetemparray=np.zeros((RPS.Receiver.arraysize,sizefft,5))

outputarray1=np.zeros((sizeffttwo,6))
dhoutputarray1=np.zeros((sizeffttwo,6))  

#       Define ground plane
groundheight=0.000000000
GROUNDABC=np.array([0.000000000,0.000000000,1.00000000])
GROUNDD=-groundheight
groundD= -groundheight
nground=np.array([0.0,0.0,1.0])

#     Allocate absorption coefficients for each surface for each frequency
alphaground=np.zeros(sizeffttwo)
for D in range(1,sizeffttwo):       #This loop has a minimal impact on performance
    if   frecuencias[D,1] >= 0.0 or    frecuencias[D,1] < 88.0 :
        alphaground[D]=PF.tempalphaground[1]
    elif frecuencias[D,1] >= 88.0 or   frecuencias[D,1] < 177.0 :
        alphaground[D]=PF.tempalphaground[2]
    elif frecuencias[D,1] >= 177.0 or  frecuencias[D,1] < 355.0 :
        alphaground[D]=PF.tempalphaground[3]
    elif frecuencias[D,1] >= 355.0 or  frecuencias[D,1] < 710.0 :
        alphaground[D]=PF.tempalphaground[4]
    elif frecuencias[D,1] >= 710.0 or  frecuencias[D,1] < 1420.0 :
        alphaground[D]=PF.tempalphaground[5]
    elif frecuencias[D,1] >= 1420.0 or frecuencias[D,1] < 2840.0 :
        alphaground[D]=PF.tempalphaground[6]
    elif frecuencias[D,1] >= 2840.0 or frecuencias[D,1] < 5680.0 :
        alphaground[D]=PF.tempalphaground[7]
    elif frecuencias[D,1] >= 5680.0 or frecuencias[D,1] < frecuencias[sizeffttwo,1]:
        alphaground[D]=PF.tempalphaground[8]

alphabuilding = np.zeros((PF.absorbplanes,sizeffttwo))
for W in range(1,PF.absorbplanes):        #These also look minimal
    for D in range(1,PF.absorbplanes):
        if   frecuencias[D,1] >= 0.0   or  frecuencias[D,1] < 88.0:
            alphabuilding[W,D]=PF.tempalphabuilding[W,1]
        elif frecuencias[D,1] >= 88.0  or  frecuencias[D,1] < 177.0:
            alphabuilding[W,D] = PF.tempalphabuilding [W,2]
        elif frecuencias[D,1] >= 177.0 or  frecuencias[D,1] < 355.0 :
            alphabuilding[W,D] = tempalphabuilding[W,3]
        elif frecuencias[D,1] >= 355.0 or  frecuencias[D,1] < 710.0 :
            alphabuilding[W,D] = tempalphabuilding[W,4]
        elif frecuencias[D,1] >= 710.0 or  frecuencias[D,1] < 1420.0 :
            alphabuilding[W,D] = tempalphabuilding[W,5]
        elif frecuencias[D,1] >= 1420.0 or frecuencias[D,1] < 2840.0 :
            alphabuilding[W,D] = tempalphabuilding[W,6]
        elif frecuencias[D,1] >= 2840.0 or frecuencias[D,1] < 5680.0 :
            alphabuilding[W,D] = tempalphabuilding[W,7]
        elif frecuencias[D,1] >= 5680.0 or frecuencias[D,1] < frecuencias[sizeffttwo,1] :
            alphabuilding[W,D] = tempalphabuilding[W,8]

#        Mesh the patches for the environment.  Include patching file. 
diffusionground = 0.0
if PF.radiosity:  # If it exists as a non-zero number
      import SingleBuildingGeometry
      diffusion = PF.radiosity
else:
      diffusion = 0.0

#count=0
#     Loop through the intial ray locations
print('began rays')
ray = 606                     # @ PF.boomspacing = 1
#ray = 455174                 # @ PF.boomspacing = 0.06
if ray:
#for ray in range(RAYMAX):
      hitcount=0
      #tmpsum=0.0
      doublehit=0
      amplitude = frecuencias[:,1]/normalization
      phase=frecuencias[:,2]
      #print(list(phase))
      if (PF.h < (2*PF.radius)): 
            print('h is less than 2r')
            #break
      F = np.array(Finitial)         # If not defined this way it will make them the same object. This will break the entire program. Do not change
      veci = boomarray[ray,:]
      for I in range(PF.IMAX):      # Making small steps along the ray path.  For each step we should return, location, phase and amplitude
            dxreceiver=HUGE
            # Find the closest sphere and store that as the distance
            for R in ears:
                  # The way that tempreceiver works now, it's only used here and only should be used here. It's not defined inside the receiver because it's ray dependant.
                  tempreceiver = R.SphereCheck(radius2,F,veci)    #distrance to receiver
                  if (receiverhit >= 1):  #if you hit a receiver last time, don't hit it again
                        if np.all(R.position ==lastreceiver):
                              tempreceiver=HUGE
                        if np.all(F == checkdirection):
                              OC = R.position - veci
                              OCLength = np.dot(OC,OC)
                              if(OCLength < radius2):
                                    tempreceiver=HUGE
                  if(receiverhit >= 2):
                        if np.all(R.position == lastreceiver):
                              tempreceiver=HUGE
                  if (tempreceiver < dxreceiver):   
                        R.dxreceiver=tempreceiver
                        dxreceiver=tempreceiver
                        receiverpoint= R.position
                  elif (tempreceiver == dxreceiver and tempreceiver != HUGE):
                        receivercheck=tempreceiver          
                        if np.all(R.position==receiverpoint):
                              doublehit=0
                        else:
                              #receiverpoint2 = R.position
                              R2 = R
                              doublehit=1
                              print('double hit')

            #     Check Intersection with ground plane
            GROUNDN=GROUNDABC
            GROUNDVD=GROUNDN[0]*F[0]+GROUNDN[1]*F[1]+GROUNDN[2]*F[2]
            if (groundhit==1):
                  dxground=HUGE
            elif (GROUNDVD!=0.0):
                  GROUNDVO=((GROUNDN[0]*veci[0]+GROUNDN[1]*veci[1]+GROUNDN[2]*veci[2])+GROUNDD)
                  dxground1=(-1.000)*GROUNDVO*(1.000)/GROUNDVD
                  dxground=dxground1
                  Vecip1=veci+dxground*F
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
            for Q in range(0,BG.Boxnumber):
                  dxnear, dxfar, hit, planehit=fun.BOX(BG.Boxarraynear[Q], BG.Boxarrayfar[Q],veci,F)
                  if (dxnear < dxbuilding):
                        dxbuilding=dxnear
                        Vecip1=veci+np.multiply(dxbuilding,F)
                        whichbox=Q
                        nbox=fun.PLANE(Vecip1, BG.Boxarraynear[whichbox],BG.Boxarrayfar[whichbox], planehit)
            #     Check intersection with Triangles
            if(BG.TriangleNumber > 0):
                  for Q in range(0, BG.TriangleNumber):
                        dxnear, behind = fun.Polygon(veci,F,Q,3,TriangleNumber,PointNumbers,Trianglearray,BuildingPoints,normal,FaceNormalNo,FaceNormals)
                        if (dxnear < dxbuilding):
                              dxbuilding=dxnear
                              nbox=normal
                              whichbox=Q
            #     Check intersection with Squares
            if(BG.SquareNumber>0):
                  for Q in range(0,BG.SquareNumber):
                        dxnear, behind=Polygon(veci,F,Q,4,SquareNumber,PointNumbers,SquareArray,BuildingPoints,normal,FaceNormalNo,FaceNormals)
                        if (dxnear < dxbuilding):
                              dxbuilding=dxnear
                              nbox=normal
                              whichbox=Q
            buildinghit=0
            receiverhit=0
            groundhit=0

            #     Check to see if ray hits within step size
            if (dxreceiver < PF.h or dxground < PF.h or dxbuilding < PF.h):
                  dx=min(dxreceiver,dxground,dxbuilding)
                  #tmpsum = tmpsum + dx
                  #     if the ray hits a receiver, store in an array.  If the ray hits two, create two arrays to store in.
                  for R in ears:
                        if dx == R.dxreceiver:
                              print('Ray ',ray +1,' hit receiver ',R.recNumber,' at step ',I)
                              veci += (dx*F)
                              receiverhit=1
                              checkdirection=F
                              if(doublehit==1):
                                    receiverhit=2
                              hitcount=hitcount+1
                              updateFreq(dx,alphanothing,0)
                              lastreceiver = receiverpoint
                              outputarray1[:,0] = frecuencias[:,0]
                              outputarray1[:,1:4] = receiverpoint[:]
                              outputarray1[:,5] = phase[:]
                              if doublehit == 1 :
                                    #R2 = R      #Supposed to be other R, but just a placeholder for now
                                    R.on_Hit(amplitude/2,phase)
                                    R2.on_Hit(amplitude/2,phase)
                              else:
                                    R.on_Hit(amplitude,phase)

                              #if(doublehit==1):
                              #      outputarray1[:,4]=amplitude[:]/2.0
                              #      dhoutputarray1[:,0]=inputarray[:,0]
                              #      dhoutputarray1[:,1:4]=receiverpoint2[:]
                              #      dhoutputarray1[:,4]=amplitude[:]/2.0
                              #      dhoutputarray1[:,5]=phase[:]
                              #      lastreceiver2 = receiverpoint2
                              #else:
                              #      outputarray1[:,4]=amplitude[:]
                              #temparray=fun.receiverHITFUNC(sizefft,outputarray1,RPS.arraysize,temparray)   # looks like it does the same thing as on_Hit. Here later
                              #R.on_Hit(amplitude,phase)
                              #if (doublehit==1):
                              #      #temparray=fun.receiverHITFUNC(sizefft,dhoutputarray1,RPS.arraysize,temparray) #Using objects may circumvent the need to have this, but it stays for now
                              #      count+=1
                              #count+=1
                  if (abs(dx-dxground)< 10.0**(-13.0)):                  #     If the ray hits the ground then bounce off the ground and continue
                        #Vecip1=veci+np.multiply(dxground,F)
                        veci += (dxground*F)
                        tmp = np.dot(GROUNDABC,veci)

                        if(tmp != GROUNDD): 
                              veci[2] = 0
                        print('hit ground at ',I)
                        dot1 = np.dot(F,nground)
                        n2 = np.dot(nground,nground)
                        F -= (2.0*(dot1/n2 *nground))
                        length = np.sqrt(np.dot(F,F))
                        groundhit=1
                        twopidx=twopi*dxground
                        #     Loop through all the frequencies
                        updateFreq(dxground,alphaground,diffusionground)
                        if(PF.radiosity==1 and (diffusionground!=0.0)):
                              for Q in range (0,PatchNo):
                                    if (formfactors[0,Q,1]==1):
                                          if(veci[0]<=(patcharray[Q,W,0]+0.5*patcharray[Q,W,3]) and veci[0]>=(patcharray[Q,W,0]-0.5*patcharray[Q,W,3])):
                                                if(veci[1]<=(patcharray[Q,W,1]+0.5*patcharray[Q,W,4]) and veci[1]>=(patcharray[Q,W,1]-0.5*patcharray[Q,W,4])):
                                                      if(veci[2]<=(patcharray[Q,W,2]+0.5*patcharray[Q,W,5]) and veci[2]>=(patcharray[Q,W,2]-0.5*patcharray[Q,W,5])):
                                                            temp2=complex(abs(patcharray[Q,W,6])*np.exp(XJ*patcharray[Q,W,7]))
                                                            temp3=complex(abs(amplitude[W]*(1.0-alphaground[W])*diffusionground*exp(-m*dxground))*exp(1j*phasefinal))
                                                            temp4=temp2+temp3
                                                            patcharray[Q,W,6]=abs(temp4)
                                                            patcharray[Q,W,7]=np.arctan(temp4.imag,temp4.real)
                  if (dx==dxbuilding):                  #     if the ray hits the building then change the direction and continue
                        veci += (dx*F)
                        print('hit building at step ',I)
                        n2 = np.dot(nbox,nbox)
                        nbuilding=nbox/np.sqrt(n2)
                        dot1= np.dot(F,nbuilding)
                        F -= (2.0*(dot1/n2 *nbuilding))
                        length = np.sqrt(np.dot(F,F))
                        buildinghit=1
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
                        updateFreq(dx,alpha,diffusion)
                        
            else:
                  #     If there was no interaction with buildings then proceed with one step. 
                  #tmpsum=tmpsum+PF.h
                  #print(phase[:5])
                  veci += (PF.h*F)
                  updateFreq(PF.h,alphanothing,0)
      #if (ray % 50) == 0:     # For debugging
      #      print('finished ray ',ray+1)
      print('finished ray', ray + 1)

#Gk=np.zeros(PatchNo,sizeffttwo)
#Gkminus1=np.zeros(PatchNo,sizeffttwo)
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
for R in ears:
      R.timeReconstruct(sizefft)

print('Writing to output file')
OPFile=open(PF.OUTPUTFILE,"w")
true=fun.Header(PF.OUTPUTFILE)
OPFile=open(PF.OUTPUTFILE,"a")      #redefining to print both Header and TimeHeader

for W in range(sizefft):
    true=fun.TimeHeader(OPFile,timearray[W],RPS.sizex1,RPS.sizey1,RPS.sizez1,RPS.planename1)
    for R in ears:
        OPFile.write('\t%f\t%f\t%f\t%f\n' %(R.position[0],R.position[1],R.position[2],np.real(R.timesignal[W])))

OPFile.close()
print(time.time()-t)