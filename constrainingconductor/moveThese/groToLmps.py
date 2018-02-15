import warnings
import mdtraj
import math
import os
import random
import sys
random.seed(12345)
import time

import numpy as np
from groupy.gbb import Gbb
from groupy.box import Box
from groupy.system import System
from groupy.builders.bilayer import Bilayer
import pdb

from optparse import OptionParser


""" Use groupy code to make a template structure for molecules/residues according
to lammps format.
Replace coordinates with equilibirated coordinates from reference structure.
Be wary of ordering of molecules in each system structure, and units"""


base_path = '/raid6/homes/ahy3nz/Programs/setup/Bilayer/Prototypes/'

def _init_parser():
    parser = OptionParser()
    parser.add_option("-f", action="store", type="string", default="converted", dest="filename")
    parser.add_option("-a", "--APL", action="store",type="float", default=60.0, dest = "area_per_lipid")
    parser.add_option("-r", "--rot", action="store", type ="float", default = 12.0, dest = "rotation")
    parser.add_option("--DSPC", action="store",type="float", default=0.0, dest = "DSPC_frac")
    parser.add_option("--DPPC", action="store",type="float", default=0.0, dest = "DPPC_frac")
    parser.add_option("--acid16", action="store",type="float", default=0.0, dest = "acid16_frac")
    parser.add_option("--acid22", action="store",type="float", default=0.0, dest = "acid22_frac")
    parser.add_option("--alc12", action="store",type="float", default=0.0,  dest = "alc12_frac")
    parser.add_option("--alc14", action="store",type="float", default=0.0, dest = "alc14_frac")
    parser.add_option("--alc16", action="store",type="float", default=0.0, dest = "alc16_frac")
    parser.add_option("--alc18", action="store",type="float", default=0.0, dest = "alc18_frac")
    parser.add_option("--alc20", action="store",type="float", default=0.0, dest = "alc20_frac")
    parser.add_option("--alc22", action="store",type="float", default=0.0, dest = "alc22_frac")
    parser.add_option("--alc24", action="store",type="float", default=0.0, dest = "alc24_frac")
    parser.add_option("--ISIS", action="store",type="float", default=0.0, dest = "isis_frac")
    parser.add_option("--SS", action="store",type="float", default=0.0, dest = "ss_frac")
    parser.add_option("--CHOL", action="store",type="float", default=0.0, dest = "chol_frac")
    parser.add_option("--PMEA", action="store",type="float", default=0.0, dest = "pmea_frac")
    parser.add_option("--water", action="store",type="float", default=0.0, dest = "water_frac")
    return parser

def _update_coordinates(system, correct_system, scale_units):
    """" Update system coordiantes with the correct system


    system : gbb.System
    correct_system : mb.Compound
    scale_units : bool
        True if need to convert from nm to A """

    i = 0
    names = [a.name for a in system.gbbs]
    resnames = [a.name for a in correct_system.topology.residues]
    for resid, gbb in enumerate(system.gbbs):
        for j, xyz_j in enumerate(gbb.xyz):
            # Verify residue names
            # With excecptions for water
            gbb_name = names[resid].lower()
            correct_name = resnames[resid].lower()
            if gbb_name != correct_name:
                if not set([gbb_name, correct_name]).issubset(set(['hoh', 'sol', 'water'])):
                    warnings.warn("Warning: resname {0} and {1} do not agree on atoms {2}".format(names[resid], resnames[resid], i), RuntimeWarning)

            if scale_units: 
                new_xyz = [10*coord - (5*length) for coord,length in zip(correct_system.xyz[0][i], correct_system.unitcell_lengths[0])]
            else:
                new_xyz = [coord - (length/2) for coord,length in zip(correct_system.xyz[i], correct_system.periodicity)]
            gbb.xyz[j] = new_xyz
            i +=1
    return system


#if __name__ == "__main__":
def convert(correct_structure):
    """
    correct_structure : str
        filename of the correct structure we are pulling xyz from
        """


    #parser = _init_parser()
    #(options,args) = parser.parse_args()
    
    # Use mdtraj to extract coordinates and box information
    if 'gro' in correct_structure or 'pdb' in correct_structure:
        scale_units = True
    else:
        scale_units = False
    #correct_system = mb.load(correct_structure)
    correct_system = mdtraj.load(correct_structure)
    
    # Create a groupy box
    #correct_box = Box(lengths=10*correct_system.periodicity)
    correct_box = Box(lengths=10*correct_system.unitcell_lengths[0])
    
    # Create the Bilayer in groupy
    dspc = Gbb(xml_prototype=base_path+'DSPC.xml',name='dspc')
    dspc.rotate(angles=[0.0,0.0,-math.pi/4.0])
    dppc = Gbb(xml_prototype=base_path+'DPPC.xml',name='dppc')
    dppc.rotate(angles=[0.0,0.0,-math.pi/4.0])
    acd12 = Gbb(xml_prototype=base_path+'c12-acid.xml',name='acd12')
    acd16 = Gbb(xml_prototype=base_path+'c16-acid.xml',name='acd16')
    acd22 = Gbb(xml_prototype=base_path+'c22-acid.xml',name='acd22')
    alc12 = Gbb(xml_prototype=base_path+'c12-alcohol.xml',name='alc12')
    alc14 = Gbb(xml_prototype=base_path+'c14-alcohol.xml',name='alc14')
    alc16 = Gbb(xml_prototype=base_path+'c16-alcohol.xml',name='alc16')
    alc18 = Gbb(xml_prototype=base_path+'c18-alcohol.xml',name='alc18')
    alc20 = Gbb(xml_prototype=base_path+'c20-alcohol.xml',name='alc20')
    alc22 = Gbb(xml_prototype=base_path+'c22-alcohol.xml',name='alc22')
    alc24 = Gbb(xml_prototype=base_path+'c24-alcohol.xml',name='alc24')
    isis = Gbb(xml_prototype=base_path+'isostearylisostearate.xml',name='isis') 
    isis.rotate(angles=[math.pi,0.0,0.0])
    ss = Gbb(xml_prototype=base_path+'ss.xml',name='ss') 
    ss.rotate(angles=[math.pi,0.0,0.0])
    chol = Gbb(xml_prototype=base_path+'CHOL.xml',name='chol')
    chol.rotate(angles=[math.pi,0.0,0.0])
    pmea = Gbb(xml_prototype=base_path+'PMEA.xml',name='pmea')
    pmea.rotate(angles=[0.0,-math.pi/2,0.0])
    water = Gbb(xml_prototype=base_path+'spc.xml',name='water')
    #DSPC thickness really 16
    lipids = [(dspc,  0.5 , 16.0),
              (dppc,  0, 13.0),
              (acd12,0, 14.0),
              (acd16,0, 22.0),
              (acd22,0, 16.0),
              (alc12, 0, 13.0),
              (alc14, 0, 14.0),
              (alc16, 0, 13.0),
              (alc18, 0.5, 12.0),
              (alc20, 0, 15.0),
              (alc22, 0, 16.0),
              (alc24, 0, 16.0),
              (isis,  0, 15.0),
              (ss,    0, 15.0),
              (chol,  0, 20.0),
              (pmea,  0, 22.0),
              (water, 0, 0.0)]


    #max_rot = options.rotation * math.pi/180
    n_x = n_y = 8
    solvent_per_lipid=20
    random_z_displacement = 3.0
    bilayer = Bilayer(lipids, n_x=n_x, n_y=n_y,
        area_per_lipid=60, mirror=False,
        solvent_per_lipid=20, solvent=water)

    # Construct system object with the correct Box
    system=System(box=correct_box, gbbs=bilayer.molecules)

    system.sort_by_name([x[0].name for x in lipids])

    # Verify number of atoms between groupy system and mbuild system
    #mb_n_atoms = len([p for p in correct_system.particles()])
    mb_n_atoms = correct_system.n_atoms
    groupy_n_atoms = sum([np.shape(thing.xyz)[0] for thing in system.gbbs])
    if mb_n_atoms != groupy_n_atoms:
        sys.exit("Error: MBuild compound has {0} atoms, but groupy compound has {1} atoms!".format(mb_n_atoms, groupy_n_atoms))

    # Update coordinates, correcting for box centered vs cornered on origin
    # Also correcting for the nm -> Angstrom change
    start = time.time()
    system = _update_coordinates(system, correct_system, scale_units)
    end = time.time()

    # Print
    system.print_lammpsdata(filename=(correct_structure[:-4]+'.lammpsdata'),
       ff_param_set='gromos53a6')





