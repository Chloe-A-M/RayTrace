# this function detects when it crosses a plane
# much of it is hardcoded, but that can all be fixes
import numpy as np
import pywavefront as pwf
#from Parameterfile import h as stepSize     #temporary, just used to make sure we do not overstep
stepSize = 10
#FaceNormals = [(-1,0,0),(0,1,0),(1,0,0),(0,-1,0),(0,0,1)]  Desired
epsilon = 1e-6  # how small angle between ray and plane has to be to count as parallel
HUGE = 1000000.0



def faceNormal(face):
    a = np.array(face[0])
    b = np.array(face[1])
    c = np.array(face[2])
    d = np.cross((b-a),(c-a))   # [D]irection
    return d

def edgeTest(triangle,P,N):
    """
    Checks if some point P is inside a triangle, uses a given Normal
    """

    edge = ((triangle[1] - triangle[0]), 
            (triangle[2] - triangle[1]), 
            (triangle[0] - triangle[2]))

    chi =  ((P - triangle[0]), 
            (P - triangle[1]), 
            (P - triangle[2]))

    sha = ( N.dot(np.cross(edge[0],chi[0])) > 0, 
            N.dot(np.cross(edge[1],chi[1])) > 0, 
            N.dot(np.cross(edge[2],chi[2])) > 0)

    return np.all(sha)

def collisionCheck(FACE,VECI,F):
    """
    find if a ray hits the face for our mesh function

    the caps lock just reinforces that the variables are only used inside this function set
    """
    F = np.array(F)         # hotfix
    N = faceNormal(FACE)    # compute plane normal
            # Finding intersection [P]oint
    # parallel check
    NF = np.dot(N,F)        # rayDir in notes, plane normal dot F
    isParallel = (abs(NF) < epsilon)    # bool, vD in old code
    #print('NF ',NF)
    if isParallel:
        return HUGE
        #print('parallel','\n',FACE)

    d = np.dot(N,FACE[0])   # is tri[0] and v0 in notes

    # find distance between origin and intersect
    t = -(np.dot(N,VECI) + d) / NF          # dx, distance that ray travels
    #print('t is ', t)
    if (t < 0):         # ray starts behind the face, break
        #print('ray behind face','\n',FACE)
        return HUGE
    elif (t > stepSize):
        #3print('too far away, ignoring','\n',FACE)
        return HUGE    # does not hit inside step, ignore it

    else:               # if and only if it hits within the step then
        p = VECI + (t * F)
        #print(p,FACE)
        isHit = edgeTest(FACE,p,N)
        #print(isHit)
        if isHit == True:
            print('hits at ', p,'\n',FACE)
        #return isHit
        return t
        #return p        # should return p as it is the dx, just a placeholder for now

ipname = 'Env/SingleBuilding.obj'
ipfile = pwf.Wavefront(ipname)    # Read in geometry file
env = pwf.ObjParser(ipfile,ipname, strict=False, encoding="utf-8", 
        create_materials=True, collect_faces=True, parse=True, cache=False)
vertices = env.wavefront.vertices                                           # useful
faces = env.mesh.faces                                                      # list of keys to vertices

#Boxnumber = 1     # supposed to import from s, come back to this later
    # Is this similar to Will's bands?
#Boxarraynear=np.array([10,10,0])
#Boxarrayfar= np.array([64.4322,46.9316,8.2423])

#mesh = [np.array((vertices[f[0]],vertices[f[1]],vertices[f[2]])) for f in env.mesh.faces]

mesh = [np.array((
        (vertices[f[0]][0], vertices[f[0]][2], vertices[f[0]][1]),
        (vertices[f[1]][0], vertices[f[1]][2], vertices[f[1]][1]),
        (vertices[f[2]][0], vertices[f[2]][2], vertices[f[2]][1])))
    for f in env.mesh.faces]    # Brute force technique just to get source to x,y,z

#for face in mesh:
#    #print(face)
#    foo = collisionCheck(face,veci,F)
    #print(foo)
    #if foo == True:
    #    print(foo,hit,'dxbuilding: ',dxBuilding)
#
#
## start here   (debugging)
#myFaces = []
#    # trying to make more usable faces
##print(mesh)
#for f in env.mesh.faces:
#    myFaces.append((vertices[f[0]],vertices[f[1]],vertices[f[2]]))
##print(myFaces)
#
