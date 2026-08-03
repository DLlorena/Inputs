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
from gpaw.mom import prepare_mom_calculation
from ase import Atoms
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if comm.rank != 0:
  import sys
  sys.stdout = open('/dev/null', 'w')
# =================================================

atoms, calc = restart('triplet.gpw', txt='-')
calc.initialize(atoms)
calc.set_positions(atoms)

gs = atoms.get_potential_energy()
print("Potential energy triplet PBE:", gs)

calc.wfs.initialize_wave_functions_from_restart_file()
f_sn = [calc.wfs.kpt_u[x].f_n.copy() for x in range(len(calc.wfs.kpt_u))]
f_sn[1][33] = 0  # change the number of the M0
f_sn[0][34] = 1

calc2 = GPAW(mode=LCAO(force_complex_dtype=True),
        xc="PBE",
        h=0.18,
        occupations={"name": "fixed-uniform"},
        eigensolver=LCAOETDM(
        searchdir_algo={"name": "L-BFGS-P"},
        localizationtype="pm_pz",
        functional={
            "name": "PZ-SIC",
            "scaling_factor": (0.5, 0.5),
            },
            ),
        mixer={"backend": "no-mixing"},
        nbands="nao",
        spinpol=True,
        basis="aug-cc-pVDZ_PBE.sz",
        symmetry="off",
        maxiter=2000,
        txt='triplet_sic2.txt',
        )
        

calc2.initialize(atoms)
calc2.set_positions(atoms)
calc2.atoms = atoms
atoms.calc = calc2

prepare_mom_calculation(calc2, atoms, f_sn)

gs2 = atoms.get_potential_energy()
print("Potential energy triplet PBE-SIC:", gs2)

calc2.write('triplet_sic.gpw', mode='all')

nhomo = 33
orbs = [nhomo, nhomo + 1]
for s in range(calc.wfs.nspins):
    for o in orbs:
            print('orbital %d spin %d' %(o, s))
            orb = calc.get_pseudo_wave_function(band=o, spin=s)
            write('triplet_sic_%d_spin%d.cube' %(o, s), atoms, data=orb)
