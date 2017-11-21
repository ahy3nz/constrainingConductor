import numpy as np
from optparse import OptionParser
import os
import glob
import subprocess
import itertools
from multiprocessing import Pool

# Run this after the permeability simulations have finished
# This means after stage 5 has finisehd running
# And all force files are still in xvg form


def _split_single_file(current_dir, sweep, i, j, all_forces):
    force_index = (j * N_sims) + i
    neg_forces = [-1 * force for force in all_forces[:,j+1]]
    np.savetxt(os.path.join(current_dir, "sweep{}/forceout{}.dat".format(sweep, force_index)), np.column_stack((all_forces[:,0], neg_forces)))

    return 1




# sim_folder/sweep{}/sim{}
# Force files should be moved to sweep{}
sweeps = sorted(glob.glob('sweep*'))


# Read in the forces files, splitting 
# Them into different force files
current_dir = os.getcwd()
for sweep in sweeps:
    os.chdir(os.path.join(current_dir,sweep)) 
    sims = glob.glob('Sim*')
    p = subprocess.Popen("rm forceout*.dat", shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    p.wait()

    for i in range(len(sims)):
        filename = "Stage5_ZCon"+str(i)+"_pullf.xvg"
        os.chdir(os.path.join(current_dir, sweep,"Sim{}".format(i)))
        with open('tracers.out', 'r') as f:
            tracers = list(f)
            N_tracer = len(tracers)

        all_forces = np.loadtxt(filename, skiprows=30, comments=["#", "@"])
        print(os.getcwd())
        # Parallel version
        with Pool() as pool:
               pool.starmap(_split_single_file, zip(itertools.repeat(current_dir), itertools.repeat(sweep), itertools.repeat(i), range(N_tracer), itertools.repeat(all_forces) )) 
        # Serial version
        #for j in range(N_tracer):
        #    force_index = (j* N_sims) + i
        #    np.savetxt(os.path.join(current_dir, "sweep{}/forceout{}.dat".format(sweep, force_index)), 
        #            np.column_stack((all_forces[:, 0], all_forces[:, j+1])))







#for i in range(11):
#    p = subprocess.Popen("mkdir sweep{}".format(i), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    p.wait()
#    p = subprocess.Popen("cp z_windows.out sweep{}".format(i), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    p.wait()
#
#current_dir = os.getcwd()
#for i in range(N_sims):
#    filename = "Stage5_ZCon"+str(i)+"_pullf.xvg"
#    os.chdir(os.path.join(current_dir, "Sim{}".format(i)))
#    all_forces = np.loadtxt(filename, skiprows=30)
#    for j in range(N_tracer):
#        force_index = (N_tracer * i) + j
#        np.savetxt(os.path.join(current_dir, "sweep0/forceout{}.dat".format(force_index)), 
#                np.column_stack((all_forces[:, 0], all_forces[:, j+1])))

# Get all the other force files
#for h in range(10):
#    for i in range(N_sims):
#        filename = "#Stage5_ZCon" + str(i) + "_pullf.xvg." + str(h+1) + "#"
#        os.chdir(os.path.join(current_dir, "Sim{}".format(i)))
#        all_forces = np.loadtxt(filename, skiprows=30)
#        for j in range(N_tracer):
#            force_index = (N_tracer * i) + j
#            np.savetxt(os.path.join(current_dir, "sweep{}/forceout{}.dat".format(h+1, force_index)), 
#                np.column_stack((all_forces[:, 0], all_forces[:, j+1])))
#
