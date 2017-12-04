import groToLmps
import pdb
import os
import numpy as np
import mdtraj
import argparse

def _write_input_header(f, temp=305.0, Nrun=380000, Nprint=1000, 
        structure_file='Stage4_Eq0.lammpsdata'):
    f.write("""clear
variable Nprint equal {Nprint} 
variable Nrun equal {Nrun} 
variable temperature equal {temp}

units real
atom_style full

pair_style lj/cut/coul/long 14.0 14.0 
bond_style harmonic
angle_style hybrid harmonic cosine/squared
dihedral_style hybrid harmonic charmm
improper_style harmonic
special_bonds lj/coul 0.0 0.0 1.0 
kspace_style pppm 1.0e-4
neighbor 2.0 bin 

read_data {structure_file}

include LammpsOostenbrink.txt
    """.format(**locals()))

def _write_rest(f, tracers, z_windows, force_indices, record_force=True):

    ###########
    f.write("""
group water type 57 58
group tracers molecule {}
group allbuttracers subtract water tracers
group bilayer subtract all water
""".format(' '.join(np.asarray(tracers,dtype=int)[:])))
    ############

    ########
    f.write("""
reset_timestep 0
variable ke equal ke
variable enthalpy equal enthalpy
variable pe equal pe
variable step equal step
variable temp equal temp
variable press equal press
variable vol equal vol

variable lx equal lx
variable ly equal ly
variable lz equal lz

timestep 1.0

fix 11 all shake 0.0001 10 10000 b 53 a 55
fix 3 all print ${Nprint} "${step} ${pe} ${press} ${temp} ${lx} ${ly} ${lz}" file system.log screen no
fix 4 water npt temp ${temperature} ${temperature} 100.0 aniso 1.0 1.0 1000.0
fix 12 bilayer nvt temp ${temperature} ${temperature} 100.0 
fix 5 bilayer momentum 1 linear 1 1 1
thermo ${Nprint}
dump d2 all custom 40000 trajectory.lammps id type xu yu zu
dump_modify d2 format line "%d %d %.3f %.3f %.3f" append yes 

dump d1 tracers custom 1000 tracerpos.xyz id mass x y z vx vy vz fx fy fz
dump_modify d1 append yes


""")
    #############

    ############
    #for i, tracer_triplet in enumerate(tracer_information):
    for i, tracer, window, force_index in enumerate(zip(tracers, 
        z_windows,force_indices)):
        #f.write("group t{0} molecule {1}\n".format(i, tracer_triplet[0]))
        f.write("group t{0} molecule {1}\n".format(i, tracer))

        if record_force:
            f.write("compute tracerfz{0} t{0} reduce sum fz\n".format(i))
            f.write("variable redforce{0} equal c_tracerfz{0}\n".format(i))
            #f.write("fix pt{0} all print 3 \"${{step}} ${{redforce{0}}}\" append forceout{1}.dat screen no\n".format(i, tracer_triplet[2]))
            f.write("fix pt{0} all print 3 \"${{step}} ${{redforce{0}}}\" append forceout{1}.dat screen no\n".format(i, force_index))

        #f.write("fix 6{0} t{0} recenter NULL NULL {1} shift t{0}\n".format(i, tracer_triplet[1]))
        f.write("fix 6{0} t{0} recenter NULL NULL {1} shift t{0}\n".format(i, window))
        f.write("fix 7{0} t{0} momentum 1 linear 0 0 1\n".format(i))
        f.write("\n")
    #########

    ########
    f.write("""
run ${Nrun}

write_restart restartfile
""")
    #########
        





    


def _prepare_lmps(eq_structure, z_windows, tracers,
        sim_number=0):
    """ Convert structure to lammps and generate input file"""
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-c', dest='eq_structure',action='store')
    #parser.add_argument('-z', dest='z_windows_file', action='store')
    #parser.add_argument('-t', dest='tracerfile', action='store')
    #parser.add_argument('-s', dest='sim_number', action='store', type=int)
    #args = parser.parse_args()

    # First, convert a structure
    #eq_structure = 'Stage4_Eq0.gro'
    #z_windows_file = 'z_windows.out'
    #tracerfile = 'tracers.out'
    #sim_number=0

    traj = mdtraj.load(eq_structure)
    groToLmps.convert(eq_structure)

    ## Load in the gmx z windows, scale/shift appropriately
    #z_windows = np.loadtxt(z_windows_file)
    z_windows = [np.round(10*(z - traj.unitcell_lengths[0][2]/2),2) for z in z_windows]
    np.savetxt('z_windows_lmps.out', z_windows)
    n_windows = np.shape(z_windows)[0]
    dz = abs(z_windows[0]-z_windows[1])

    ## Load in the tracer information
    #tracer_list = np.loadtxt(tracerfile, dtype=int)
    #n_tracers = np.shape(tracer_list)[0]
    n_tracers = np.shape(tracers)[0]

    force_indices = [sim_number + int(i*n_windows/n_tracers) 
            for i, tracer_id in enumerate(tracers)]


    ## Assign tracers to locations and force output indices
    #tracer_information = [[tracer_id, z_windows[sim_number + int(i*n_windows/n_tracers)],
        #sim_number + int(i*n_windows/n_tracers)] 
            #for i, tracer_id in enumerate(tracer_list)]


    # For now, let's only write a zconstraining file out
    with open('Stage5_ZCon.input','w') as f:
        _write_input_header(f, structure_file=eq_structure[:-4]+'.lammpsdata')
        _write_rest(f, tracers, z_windows, force_indices)


def lmps_conversion(eq_structure, windows, tracers, sim_number):
    """ Main method to do lmps structure conversions and input writing"""
    print("*"*20)
    print("Converting in {}".format(os.getcwd()))
    print("*"*20)
    _prepare_lmps(eq_structure, windows, 
                tracers, sim_number)
                #tracerfile=tracerfile, sim_number=int(sim[-1]))

#    working_dir = os.getcwd()
#    sweep_folders = [f for f in os.listdir() if os.path.isdir(f) and 'sweep' in f]
#    for sweep in sweep_folders:
#        os.chdir(os.path.join(working_dir, sweep))
#        z_windows_file = os.path.join(working_dir, sweep, 'z_windows.out')
#        sim_folders = [g for g in os.listdir() if os.path.isdir(g) and 'Sim' in g]
#        for sim in sim_folders:
#            os.chdir(os.path.join(working_dir, sweep, sim))
#            tracerfile = os.path.join(working_dir, sweep, sim, 'tracers.out')
#            try:
#                eq_structure = [h for h in os.listdir() if os.path.isfile(h) and 'Stage4' in h and '.gro' in h][0]
#                print("Converting in {}".format(os.getcwd()))
#                _prepare_lmps(eq_structure=eq_structure, z_windows_file=z_windows_file, 
#                        tracerfile=tracerfile, sim_number=int(sim[-1]))
#            except IndexError:
#                print("Stage4.gro not found, simulation may have crashed in {}".format(os.getcwd()))
