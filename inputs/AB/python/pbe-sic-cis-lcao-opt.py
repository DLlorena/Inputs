from gpaw import GPAW, PW, LCAO
from ase.units import Bohr
from ase.build import molecule
from gpaw.directmin.tools import excite
#from gpaw.directmin.etdm_fdpw import FDPWETDM
from gpaw.directmin.etdm_lcao import LCAOETDM
from gpaw.transformers import Transformer
from gpaw.point_groups import SymmetryChecker
from ase.parallel import paropen as open
from ase.optimize import BFGS
from ase import Atoms
import numpy as np
from ase.io import write
from mpi4py import MPI
from gpaw import restart

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if comm.rank != 0:
    import sys
    sys.stdout = open('/dev/null', 'w')
# =================================================

# Restart
mol, calc = restart('pbe-sic-cis-lcao.gpw', txt='pbe-sic-cis-lcao-opt.txt')

calc.initialize(mol)
calc.set_positions(mol)

center = mol.get_cell().sum(axis=0) / 2.0

gs = mol.get_potential_energy()
print("Ground state energy before (eV): ", gs)

# Optimization step
relax = BFGS(mol, logfile='pbe-sic-cis-lcao-opt.log')
relax.run(fmax=0.02)

gs = mol.get_potential_energy()
print("Ground state energy after opt (eV): ", gs)

# Save calculation (like a chk point file)
calc.write('pbe-sic-cis-lcao-opt.gpw', mode='all')
