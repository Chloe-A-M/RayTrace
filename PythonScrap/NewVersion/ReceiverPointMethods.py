# Python37 Receiver Point 

# Works
#     Create a point reciever

# May have to look into init method, but functions the same as original.

import time 
import numpy as np
import Parameterfile_methods as PF

#           Planning 
# Create Class for Receiver 
#   Define dunder init to take input(x,y,z)
#   Include provision to increase receiver number by 1 each time it is called 
#   Define receiver array based on number of receivers and position
#   Read inputs into array, use number for specificity
#   Maybe clear remaining data after?
 
t=time.time()
class Receiver:
    """
    Receiver class with attributes of position (x,y,z)

    Functionality for pressure not yet added.
    """
    planenum=1
    planename1='Single Point'
    arraysize=0     #Number of receivers. Supposed to be 5 for this test
    sizex=2
    sizey=2
    sizez=1
    initial_frequency = None

    rList = [] #See append_list

    Array = np.array([None])    # I personally prefer writing Receiver.Array to Receiver.receiverarray

    def __init__(self,x,y,z):
        """
        Create and defines position of receiver
        
        Works automatically when class is called
        """
        self.position=np.array((x,y,z))
        self.recNumber = Receiver.arraysize
        Receiver.rList.append(self) #See append_list
        
        ## Testing   -- It works, but doesn't do what I want it to 
        #Receiver.xPoints.append(x)
        #Receiver.yPoints.append(y)
        #Receiver.zPoints.append(z)

        self.pressure = 0
        self.magnitude = 0
        self.direction = 0

        Receiver.arraysize +=1


    def on_Hit(self,amplitude,phase):
        """ 
        My version of old receiver hit function. 
        Modifies direction and magnitude of rays with respect to each receiver
        """
        XJ = complex(0,1)
        #print('initiating hit function')

        temp1 = abs(self.magnitude) * np.exp(XJ*self.direction)
        temp2 = abs(amplitude[:])   * np.exp(XJ*phase[:])
        temp3 = temp1 + temp2 

        self.magnitude = np.sum( abs(temp3)                                 , axis=0)
        self.direction = np.sum( np.arctan2(np.imag(temp3) , np.real(temp3)), axis=0)
        #print('got through the end') 

        # See bug log 3/13 for what happened with positions checks

    @classmethod
    def create_receiverarray(cls):
        """
        Creates receiverarray based on the number of receivers created.
        """
        cls.Array = np.zeros((cls.arraysize,3))

    @classmethod
    def from_receiver(cls,self):
        """
        Adds the receiver to the Receiver array.
        No input needed besides the specific Receiver.
        """
        cls.Array[self.recNumber]=self.position

    @classmethod
    def de_frecuencias(cls,frecuencia):
        """
        Sets the initial frequency.
        1/11: Now sets one default frequency and 
        all arrays will now use a copy when needed
        """
        cls.initial_frequency = frecuencia

    def hitFunction(self):
        """
        Adds pressure from a ray when it hits a receiver

        I don't know if I should define this as an instance
         method because it works on each receiver
         or a static method because it works on all once.
         I'm leaning towards instance now, but that's subject to change 
        """
        pass 
        print("Everything seems to initiate.")
        

#Unused
#class const:
#    """
#    If you're wondering where these came from:
#    Some scrap paper that I never uploaded
#    Defining all constants here instead of redefining them again
#    """
#    PI = 3.1415965358979323846
#    XJ = complex(0.0,1.0)
#    radius = PF.radius # use this or pf
#    radius2 = PF.radius * PF.radius
#    twopi= 2.0 * PI
#    HUGE=1000000.0

# Initializing receivers
def initialize_receivers():
    """Create Individual receivers"""
    R1 = Receiver(93.4428213,28.8397178,0.151)
    R2 = Receiver(64.5832,28.5998,0.151)
    R3 = Receiver(64.5832,28.5998,7.9423)
    R4 = Receiver(-2.40793,31.5003401,0.151)
    R5 = Receiver(75.11005,28.4945787,0.151)

    """Create Array of receiver positions"""
    Receiver.create_receiverarray()
    Receiver.from_receiver(R1)
    Receiver.from_receiver(R2)
    Receiver.from_receiver(R3)
    Receiver.from_receiver(R4)
    Receiver.from_receiver(R5)
    return 


initialize_receivers()

#test = Receiver(7,94,3)
#Receiver.frequency = 83
#test.frequency += 7
#
#print(test.frequency)
#print(Receiver.rList[0].frequency)

#print(Receiver.rList)
#print(Receiver.Array)

#Receiver.rList[1].foo = 3
#print(Receiver.rList[1].foo)
#print(Receiver.rList)
#print(Receiver.Array)

## Test List
#Receiver.append_list(R1)
#Receiver.append_list(R2)
#Receiver.append_list(R3)
#Receiver.append_list(R4)
#Receiver.append_list(R5)

#print(R1)
#print(Receiver.rList)              # A list of objects. Probably not helpful in hindsight 
#print(Receiver.rList[0])
#print(Receiver.rList[0].__dict__)   #Show attributes for receiver

#Receiver.rList[0].pressure = 100    #Add pressure directly from list

#print(R1.pressure)                  #Access pressure from specific receiver

#print(Receiver.rList[0].__dict__)   #Show attributes for receiver
# The receiver can now be accessed from two separate places. This may eliminate the need for Receiver.Array completely

#for i in range(len(Receiver.rList)):
#    print(Receiver.rList[i].position)

## Adding receivers to Array
#Receiver.create_receiverarray()
#Receiver.from_receiver(R1)
#Receiver.from_receiver(R2)
#Receiver.from_receiver(R3)
#Receiver.from_receiver(R4)
#Receiver.from_receiver(R5)

# For backwards compatibility
planenum=1
planename1='Single Point'
#arraysize=5
arraysize1= Receiver.arraysize
sizex=2
sizey=2
sizez=1
sizex1=sizex
sizey1=sizey
sizez1=sizez

#receiverarray = Receiver.Array  #For compatibility with rest of data
#print(receiverarray)
#receiverarray is Receiver.Array #trying to refer to same object instead of equal value
#print(receiverarray)

# ^ These also make runtime wildly varied, nix them when possible ^

print('created receiver array')

#print(R1.position)
#print(R2.position)
#print(Receiver.Array)
#print(Receiver.arraysize)

#print("%8f " % (time.time()-t))
#print(time.time()-t)

#from ReceiverPointMethods import Receiver.Array as receiverarray # copy for backwards compatibility

