import numpy as np
from mpi4py import MPI
from ase.io import read, write
from gpaw import GPAW, restart
from gpaw import PW, LCAO
from ase.units import Bohr
from ase.build import molecule
from gpaw.directmin.tools import excite
from gpaw.directmin.etdm_lcao import LCAOETDM
from gpaw.transformers import Transformer
from gpaw.point_groups import SymmetryChecker
from ase import Atoms
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if comm.rank != 0:
  import sys
  sys.stdout = open('/dev/null', 'w')
# =================================================

def rotate(C, angle, a, b):
    C_a_new = np.cos(angle) * C[a] - np.sin(angle) * C[b]
    C_b_new = np.cos(angle) * C[a] + np.sin(angle) * C[b]

    return C_a_new, C_b_new

atoms, calc = restart('8.gpw', txt='rotate_orb.txt')
calc.initialize(atoms)
calc.set_positions(atoms)

gs = atoms.get_potential_energy()
print("Potential energy before rotation:", gs)

nhomo = 33  # index of homo
mix_angle = 45 * np.pi / 180.0
C_alpha = calc.wfs.kpt_u[0].C_nM.copy()
C_beta = calc.wfs.kpt_u[1].C_nM.copy()

# Mix HOMO and LUMO alpha spin
C_a_new_alpha, C_b_new_alpha = rotate(C_alpha, 45, nhomo, nhomo + 1)
# Mix HOMO and LUMO beta spin
C_a_new_beta, C_b_new_beta = rotate(C_beta, 45, nhomo, nhomo + 1)

# Set new orbitals
calc.wfs.kpt_u[0].C_nM[nhomo] = C_a_new_alpha
calc.wfs.kpt_u[0].C_nM[nhomo + 1] = C_b_new_alpha
calc.wfs.kpt_u[1].C_nM[nhomo] = C_b_new_beta
calc.wfs.kpt_u[1].C_nM[nhomo + 1] = C_a_new_beta

calc.set(#occupations={"name": "fixed-uniform"},
         eigensolver=LCAOETDM(
         searchdir_algo={"name": "L-BFGS-P"},
         linesearch_algo = {'name': 'max-step', 'max_step': 0.1999},),
         #mixer={"backend": "no-mixing"},
         #nbands="nao",
         #basis="aug-cc-pVDZ_PBE.sz",
         #symmetry="off",
         #spinpol=True,
         )

gs2 = atoms.get_potential_energy()
print("Potential energy after rotation:", gs2)

calc.write('rotate_orb_cis.gpw', mode='all')

orbs = [nhomo, nhomo + 1]
for s in range(calc.wfs.nspins):
    for o in orbs:
            print('orbital %d spin %d' %(o, s))
            orb = calc.get_pseudo_wave_function(band=o, spin=s)
            write('ts_gs_%d_spin%d_rotated.cube' %(o, s), atoms, data=orb)
