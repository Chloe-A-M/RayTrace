# Test case, will be merged back into raytrace file
# Initialize variables and functions
import numpy as np
import Parameterfile as PF

import time
import memory_profiler as mem 
t = time.time()

def initial_carpet(radius,F,tmp,x,y,z,arraysize):
    """This function creates the direction of the rays in the initial boom carpet
        See InitialGrid in old versions"""
    receiverarray=np.zeros((arraysize,3))
    D = tmp
    count = 0
    if x[0] == x[1]:
        for i in range(int((z[1]-z[0])//zspace)):
            for j in range(int((y[1]-y[0])//yspace)):
                receiverarray[count,0]=(D-F[1]*(y[0]+(j+1)*yspace)-F[2]*(z[0]+(i+1)*zspace))/F[0]
                receiverarray[count,1]=y[0]+(j+1)*yspace
                receiverarray[count,2]=z[0]+(i+1)*zspace
                count=count+1
        return receiverarray

#       Set initial values
Vinitial =  np.array([PF.xinitial,PF.yinitial,PF.zinitial])
xiinitial  =np.cos(PF.phi)*np.sin(PF.theta)
ninitial   =np.sin(PF.phi)*np.sin(PF.theta)
zetainitial=np.cos(PF.theta)
length =    np.sqrt(xiinitial*xiinitial+ninitial*ninitial+zetainitial*zetainitial)
Finitial=np.array([xiinitial,ninitial,zetainitial])
#tmp=(Finitial[0]*Vinitial[0]+Finitial[1]*Vinitial[1]+Finitial[2]*Vinitial[2])
D = np.dot(Finitial,Vinitial)   #equivalent to tmp
#PLANEABC=np.array([Finitial[0],Finitial[1],Finitial[2],tmp])
x = (PF.xmin,PF.xmax) 
y = (PF.ymin,PF.ymax) 
z = (PF.zmin,PF.zmax) 

#       Create initial boom array
yspace=PF.boomspacing*abs(np.cos(PF.phi))
zspace=PF.boomspacing*abs(np.sin(PF.theta))
if (PF.xmin == PF.xmax):
   raymax=int((PF.ymax-PF.ymin)/yspace)*int((PF.zmax-PF.zmin)/zspace)
print(raymax , ' is the raymax')

print('Memory (befores) : ' + str(mem.memory_usage()) + 'MB')
#
## New technique
#    # See generators file 
#t = time.time()
#def carpet(raymax,radius,F,D,x,y,z):
#    """This function creates the direction of the rays in the initial boom carpet"""
#    for r in raymax:
#        xdir = (D-F[1]*(y[0]+(j)*yspace)-F[2]*(z[0]+(i)*zspace))/F[0]
#        ydir = y[0]+(j)*yspace
#        zdir = z[0]+(i)*zspace
#        #print(r)
#        #yield np.array((xdir,ydir,zdir))
#        yield np.array((xdir,ydir,zdir))
#
#i = 1
#j = 1 
#rayposition = carpet(range(raymax),PF.boomspacing,Finitial,D,x,y,z)
#
#if x[0] == x[1]:
#    imax = int((z[1]-z[0])//zspace)
#    jmax = int((y[1]-y[0])//yspace)
#
#for veci in rayposition:
#    # Positioning for initial rays along initial grid
#    ray = veci
#    j += 1
#    if j > jmax:
#        j = 1
#        i += 1
#
#print('Memory (generator) : ' + str(mem.memory_usage()) + 'MB')
#print('time: ',time.time()-t)
#
## Old Tracing
#t = time.time()
#boomarray = initial_carpet(PF.boomspacing,Finitial,D,x,y,z,raymax)
#print('began rays')
#for ray in range(raymax):
#      veci = boomarray[ray,:]
#print('Memory (grid): ' + str(mem.memory_usage()) + 'MB' )
#print('time: ',time.time()-t)
##

t = time.time()
# Experiment
def vein(y,z):
    "The x coordinate of the ray"
    return (D-F[1]*y-F[2]*z)/F[0]

F = Finitial

j = np.arange(1,1+int((y[1]-y[0])//yspace))
k = np.arange(1,1+int((z[1]-z[0])//zspace))

#rayy = y[0] + (np.arange(1,jmax)*yspace)
#rayz = z[0] + (np.arange(1,kmax)*yspace)
rayy = y[0] + j*yspace
rayz = z[0] + k*zspace
#rayx=(D-F[1]*   (y[0]+(j*yspace)-  F[2]* (z[0]+(k*zspace))/F[0]))

#veci2 = [(y,z) for y in rayy for z in rayz ]
#veci2 = [(y,z) for z in rayz for y in rayy ]
#print(veci2[:5])
#vecix = ((vein(y,z),y,z) for y in rayy for z in rayz )
vecix = ((vein(y,z),y,z) for z in rayz for y in rayy )

#
##for i in range(5):
##    print(rayz[i])
#
##print(vecix)
#_ = 0
#for n in vecix:
#    if _ <5:
#        print(n)
#    _ +=1

for ray in vecix:
    pass
print('New: ',time.time()-t)
print('Memory (new): ' + str(mem.memory_usage()) + 'MB' )

#