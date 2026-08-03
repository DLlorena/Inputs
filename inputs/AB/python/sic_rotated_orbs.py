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

atoms, calc = restart('rotate_orb_cis.gpw', txt='-')
calc.initialize(atoms)
calc.set_positions(atoms)

gs = atoms.get_potential_energy()
print("Potential energy PBE:", gs)

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
        txt='rotate_orb_sic_cis.txt',
        )
        

calc2.initialize(atoms)
calc2.set_positions(atoms)
calc2.atoms = atoms
atoms.calc = calc2

gs2 = atoms.get_potential_energy()
print("Potential energy PBE-SIC:", gs2)

calc2.write('rotate_orb_sic_cis.gpw', mode='all')

nhomo = 33
orbs = [nhomo, nhomo + 1]
for s in range(calc.wfs.nspins):
    for o in orbs:
            print('orbital %d spin %d' %(o, s))
            orb = calc.get_pseudo_wave_function(band=o, spin=s)
            write('cis_gs_sic_%d_spin%d_rotated.cube' %(o, s), atoms, data=orb)
