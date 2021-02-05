# RayTrace
# version 1.1.0

# Kimberly A. Riegel, PHD created this program to propagate sonic booms around
# large structures, and to graduate. It is a ray tracing model that 
# will include specular and diffuse reflections. It will print out the
# sound field at ear height, at relevant microphone locations, and at 
# the building walls. It will read in the fft of a sonic boom signature.

# Dr. Riegel, William Costa, and George Seaton porting program from Fortran to python

# Initialize variables and functions
import numpy as np  # matrices and arrays
import matplotlib.pyplot as plt  # for graphing

import Parameterfile as Pf
import Functions as Fun
import ReceiverPointSource as Rps  # For receivers
import GeometryParser as Gp

import time  # Time checks
t = time.time()
phase = 0
amplitude = 0

# What it does not do
"""
      Anything resembling radiosity
"""


def initial_signal(signal_length, fft_output):
    """
    Making the array for the initial signals.
    Input size_fft_two and output_signal
    """
    signal_length2 = int(signal_length // 2)  # Making size_fft_two and setting it as an int again just to be sure
    output_frequency = np.zeros((signal_length2, 3))  # Making output array equivalent to input_array in old code
    throw_array = np.arange(1, signal_length2 + 1)  # Helps get rid of for-loops in old version

    output_frequency[:, 0] = throw_array * Pf.Fs / signal_length  # Tried simplifying the math a bit from original
    output_frequency[:, 1] = abs(fft_output[1:1 + signal_length2] / signal_length)  # Only go up to size_ftt_two
    output_frequency[:, 2] = np.arctan2(np.imag(fft_output[1:1 + signal_length2] / signal_length),
                                        np.real(fft_output[1:1 + signal_length2] / signal_length))

    return output_frequency


def update_freq(dx_update, alpha_update, diffusion_update, lamb, air_absorb):
    """
    Update ray phase and amplitude
    """
    global phase, amplitude  # works directly
    two_pi_dx_update = twopi * dx_update
    ein = phase - (two_pi_dx_update / lamb)
    zwei = ein % twopi
    masque = zwei > np.pi
    drei = masque * zwei - twopi
 
    phase = np.where(masque, drei, ein)
    amplitude *= ((1.0 - alpha_update) * (1.0 - diffusion_update) * np.exp(-air_absorb * dx_update))


def vex(d, f_initial, y, z):
    """The x coordinate of the ray 
    Used for veci"""
    return (d - f_initial[1] * y - f_initial[2] * z) / f_initial[0]


def main():

    global phase
    global amplitude
    global twopi
    twopi = np.pi * 2
    t = time.time()

    # port and import receiver file
    receiver_hit = 0
    ground_hit = 0
    building_hit = 0

    # Initialize counters
    radius2 = Pf.radius**2

    # Read in input file
    input_signal = np.loadtxt(Pf.INPUTFILE)
    k = len(input_signal)
    # masque = input_signal > 0
    huge = 1000000.0

    # Allocate the correct size to the signal and fft arrays
    size_fft = k
    size_fft_two = size_fft // 2
    output_signal = np.fft.rfft(input_signal, size_fft)

    # Create initial signal
    frecuencias = initial_signal(size_fft, output_signal)      # Equivalent to inputArray in original
    air_absorb = Fun.absorption(Pf.ps, frecuencias[:, 0], Pf.hr, Pf.Temp)   # size_fft_two
    lamb = Pf.soundspeed/frecuencias[:, 0]     # Used for updating frequencies in update function
    time_array = np.arange(k) / Pf.Fs

    #       Set initial values
    v_initial = np.array([Pf.xinitial, Pf.yinitial, Pf.zinitial])
    xi_initial = np.cos(Pf.phi) * np.sin(Pf.theta)
    n_initial = np.sin(Pf.phi) * np.sin(Pf.theta)
    zeta_initial = np.cos(Pf.theta)
    f_initial = np.array([xi_initial, n_initial, zeta_initial])
    d4 = np.dot(f_initial, v_initial)   # equivalent to tmp
    #       Create initial boom array
    #  Roll this all into a function later
    y_space = Pf.boomspacing * abs(np.cos(Pf.phi))
    z_space = Pf.boomspacing * abs(np.sin(Pf.theta))
    if Pf.xmin == Pf.xmax:
        ray_max = int((Pf.ymax - Pf.ymin) / y_space) * int((Pf.zmax - Pf.zmin) / z_space)
        print(ray_max, ' is the ray_max')

    j = np.arange(1, 1 + int((Pf.ymax-Pf.ymin) // y_space))
    k_2 = np.arange(1, 1 + int((Pf.zmax-Pf.zmin) // z_space))
    ray_y = Pf.ymin + j * y_space
    ray_z = Pf.zmin + k_2 * z_space

    boom_carpet = ((vex(d4, f_initial, y, z), y, z) for z in ray_z for y in ray_y)
    # Create a receiver array, include a receiver file.
    alpha_nothing = np.zeros(size_fft_two)

    # Making specific receiver points using receiver module
    Rps.Receiver.initialize(Pf.RecInput)
    ears = Rps.Receiver.rList           # easier to write
    for R in ears:          # hotfix
        R.magnitude = np.zeros(size_fft_two)
        R.direction = np.zeros(size_fft_two)
    temp_receiver = np.array(np.zeros(len(ears)))
    #       Initialize normalization factor
    normalization = (np.pi*radius2)/(Pf.boomspacing**2)

    #       Define ground plane
    ground_height = 0.000000000
    ground_n = np.array([0.000000000, 0.000000000, 1.00000000])
    ground_d = -ground_height

    #     Allocate absorption coefficients for each surface for each frequency
    alpha_ground = np.zeros(size_fft_two)
    for D1 in range(0, size_fft_two):       # This loop has a minimal impact on performance
        if frecuencias[D1, 0] >= 0.0 or frecuencias[D1, 0] < 88.0:
            alpha_ground[D1] = Pf.tempalphaground[0]
        elif frecuencias[D1, 0] >= 88.0 or frecuencias[D1, 0] < 177.0:
            alpha_ground[D1] = Pf.tempalphaground[1]
        elif frecuencias[D1, 0] >= 177.0 or frecuencias[D1, 0] < 355.0:
            alpha_ground[D1] = Pf.tempalphaground[2]
        elif frecuencias[D1, 0] >= 355.0 or frecuencias[D1, 0] < 710.0:
            alpha_ground[D1] = Pf.tempalphaground[3]
        elif frecuencias[D1, 0] >= 710.0 or frecuencias[D1, 0] < 1420.0:
            alpha_ground[D1] = Pf.tempalphaground[4]
        elif frecuencias[D1, 0] >= 1420.0 or frecuencias[D1, 0] < 2840.0:
            alpha_ground[D1] = Pf.tempalphaground[5]
        elif frecuencias[D1, 0] >= 2840.0 or frecuencias[D1, 0] < 5680.0:
            alpha_ground[D1] = Pf.tempalphaground[6]
        elif frecuencias[D1, 0] >= 5680.0 or frecuencias[D1, 0] < frecuencias[size_fft_two, 0]:
            alpha_ground[D1] = Pf.tempalphaground[7]

    alpha_building = np.zeros((Pf.absorbplanes, size_fft_two))
    for W in range(Pf.absorbplanes):        # These also look minimal
        for D2 in range(size_fft_two):
            if frecuencias[D2, 0] >= 0.0 or frecuencias[D2, 0] < 88.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 0]
            elif frecuencias[D2, 0] >= 88.0 or frecuencias[D2, 0] < 177.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 1]
            elif frecuencias[D2, 0] >= 177.0 or frecuencias[D2, 0] < 355.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 2]
            elif frecuencias[D2, 0] >= 355.0 or frecuencias[D2, 0] < 710.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 3]
            elif frecuencias[D2, 0] >= 710.0 or frecuencias[D2, 0] < 1420.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 4]
            elif frecuencias[D2, 0] >= 1420.0 or frecuencias[D2, 0] < 2840.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 5]
            elif frecuencias[D2, 0] >= 2840.0 or frecuencias[D2, 0] < 5680.0:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 6]
            elif frecuencias[D2, 0] >= 5680.0 or frecuencias[D2, 0] < frecuencias[size_fft_two, 0]:
                alpha_building[W, D2] = Pf.tempalphabuilding[W, 7]

    #        Mesh the patches for the environment.  Include patching file.
    diffusion_ground = 0.0
    if Pf.radiosity:  # If it exists as a non-zero number
        diffusion = Pf.radiosity
    else:
        diffusion = 0.0

    ray_counter = 0

    if Pf.h < (2 * Pf.radius):
        print('h is less than 2r')
        raise SystemExit

    # These are for debugging, Uncomment this block and comment out the for loop below
    # ray = 606                     # @ Pf.boomSpacing = 1
    # for i in range(606):
    #      ray =      next(boom_carpet)
    #      ray_counter += 1
    # if ray:
    #
    # Begin tracing
    n_box = [0, 0, 0]
    veci = np.array([0, 0, 0])
    print('began rays')
    for ray in boom_carpet:              # Written like this for readability
        veci = ray      # initial ray position
        hit_count = 0

        amplitude = frecuencias[:, 1]/normalization
        phase = frecuencias[:, 2]

        f = np.array(f_initial)                                      # Direction
        for I in range(Pf.IMAX):      # Making small steps along the ray path.
            # For each step we should return, location, phase and amplitude
            dx_receiver = huge
            # Find the closest sphere and store that as the distance
            i = 0
            for R in ears:
                # The way that tempReceiver works now, it's only used here and only should be used here.
                # It's not defined inside the receiver because it's ray dependant.
                temp_receiver[i] = R.sphere_check(radius2, f, veci)    # Distance to receiver
                i += 1
            temp_receiver[np.where((temp_receiver < (10.0**(-13.0))))] = huge
            tmp = np.argmin(temp_receiver)
            dx_receiver = temp_receiver[tmp]

                #     Check Intersection with ground plane
            ground_vd = np.dot(ground_n, f)
            #ground_vd = ground_n[0] * f[0] + ground_n[1] * f[1] + ground_n[2] * f[2]
            if ground_hit == 1:
                dx_ground = huge
            elif ground_vd != 0.0:
                ground_vo = ((np.dot(ground_n, veci)) + ground_d)
                dx_ground = -ground_vo / ground_vd
                if dx_ground < 0.0:
                    dx_ground = huge
            else:
                dx_ground = huge
                
            #   Implement Geometry parser
            if building_hit == 1:   #Avoid hitting building twice
                dx_building = huge
            else:
                dx_building, n_box = Gp.collision_check2(Gp.mesh, veci, f)
            building_hit = 0
            receiver_hit = 0
            ground_hit = 0

            #     Check to see if ray hits within step size
            if dx_receiver < Pf.h or dx_ground < Pf.h or dx_building < Pf.h:
                dx = min(dx_receiver, dx_ground, dx_building)
                #  if the ray hits a receiver, store in an array.  If the ray hits two, create two arrays to store in.
                #for R in ears:
                if dx == dx_receiver:
                    #print('Ray ', ray_counter, ' hit receiver ', R.recNumber)
                    veci += (dx * f)
                    hit_count = hit_count + 1
                    update_freq(dx, alpha_nothing, 0, lamb, air_absorb)
                    ears[tmp].on_hit(amplitude, phase)

                if abs(dx - dx_ground) < 10.0**(-13.0):  # If the ray hits the ground then bounce and continue
                    veci += (dx_ground * f)
                    tmp = np.dot(ground_n, veci)
                    if tmp != ground_d:
                        veci[2] = 0
                    #print('hit ground at ', I)
                    dot1 = np.dot(f, ground_n)
                    n2 = np.dot(ground_n, ground_n)
                    f -= (2.0 * (dot1 / n2 * ground_n))
                    ground_hit = 1
                    #twoPiDx = np.pi * 2 * dx_ground
                    update_freq(dx_ground, alpha_ground, diffusion_ground, lamb, air_absorb)    #     Loop through all the frequencies

                if dx == dx_building:   # if the ray hits the building then change the direction and continue
                    veci += (dx * f)
                    #print('hit building at step ', I)
                    n2 = np.dot(n_box, n_box)
                    n_building = n_box / np.sqrt(n2)
                    n3 = np.dot(n_building, n_building)
                    dot1 = np.dot(f, n_building)
                    f -= (2.0 * (dot1 / n3 * n_building))
                    building_hit = 1

                    alpha = alpha_building[0, :]
                    update_freq(dx, alpha, diffusion, lamb, air_absorb)
            else:  # If there was no interaction with buildings then proceed with one step.
                veci += (Pf.h * f)
                update_freq(Pf.h, alpha_nothing, 0, lamb, air_absorb)
        ray_counter += 1
        #print('finished ray', ray_counter)

    # Reconstruct the time signal and print to output file
    for R in ears:
        R.time_reconstruct(size_fft)

    print('Writing to output file')         #For Matlab compatibility
    fileid = Pf.outputfile
    with open(fileid, 'w') as file:
        Fun.header(fileid)

    with open(fileid, 'a') as file:
        for w in range(size_fft):
            Rps.Receiver.time_header(file, time_array[w], w)
    print('time: ', time.time()-t)

    # Outputting graphs
    t = time.time()

    # ######################################################################
    # Will eventually be moved to a receiver function,
    # here now for ease of access of others reading this
    # ######################################################################
    import matplotlib.font_manager as fm
    # Font
    stdfont = fm.FontProperties()
    stdfont.set_family('serif')
    stdfont.set_name('Times New Roman')
    stdfont.set_size(20)

    for R in ears:
        # For N wave
        pressure = R.signal
        i = R.recNumber
        # plt.figure(i)
        # plt.figure(num = i, figsize=(19.20, 10.80), dpi=120, facecolor='#eeeeee', edgecolor='r')   # grey
        # plt.figure(num = i, figsize=(19.20, 10.80), dpi=120, facecolor='#e0dae6', edgecolor='r')   # muted lilac
        plt.figure(num=i, figsize=(19.20, 10.80), dpi=120, facecolor='#e6e6fa', edgecolor='r')  # lavender
        # plt.plot(time_array,pressure,'r--')
        plt.grid(True)
        plt.plot(time_array, pressure, '#780303')
        # Labeling axes
        plt.xlabel('Time [s]', fontproperties=stdfont)
        plt.ylabel('Pressure [Pa]', fontproperties=stdfont)
        plt.title('Pressure vs Time of Receiver ' + str(i),
                  fontproperties=stdfont,
                  fontsize=26,
                  fontweight='bold')

        # Saving
        plt.savefig(Pf.graphName + str(i) + '.png', facecolor='#e6e6fa')  # lavender
        print('Saved receiver', i)
    print('Graph time: ', time.time() - t)
