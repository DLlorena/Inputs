import numpy as np
from copy import deepcopy
import sys

from ase.io import read, write
from ase.units import fs, kJ, second, _hbar, Ha, Bohr, kB
from ase.io import read, write, iread, Trajectory
from ase.parallel import parprint, paropen
from ase.mep import NEB
from ase.optimize import MDMin, BFGS
from ase.build.rotate import minimize_rotation_and_translation
from ase.io.trajectory import Trajectory
from ase.mep.neb import idpp_interpolate, interpolate
from ase.mep import NEBTools

from gpaw import GPAW
from gpaw import restart
from gpaw import mom
from gpaw.mpi import world
from gpaw import LCAO
from gpaw.directmin.etdm_lcao import LCAOETDM

from pathlib import Path

np.set_printoptions(threshold=sys.maxsize)


mrc = 7.0
nimages = 16


# ini, calc = restart('C2H2F2_0.gpw', txt=None)
ini= read('cis.xyz')
fi= read('trans.xyz')
ini.center(vacuum=mrc)
cell = ini.get_cell()
parprint(cell)
fi.center(vacuum=mrc)
fi.set_cell(cell)
fi.center()
ini.set_pbc(False)
fi.set_pbc(False)

minimize_rotation_and_translation(ini, fi)

ini_path = [ini.copy() for _ in range(nimages -1 )] + [fi]
parprint(ini_path)


interpolate(ini_path, mic=False, interpolate_cell=False,
            use_scaled_coord=False, apply_constraint=False)  # Linear interpolation

# parprint(ini_path)
neb = NEB(ini_path, remove_rotation_and_translation=True, k=0.1, climb=True, method='improvedtangent', allow_shared_calculator=True)


MDMin.defaults['dt']=0.01
# If the images blow up, make sure to change the default optimization step size in MDMin from 0.2 to 0.01. It's a known issue
idpp_interpolate(neb, fmax=0.01, traj='idpp.traj', log='idpp.log',
                 optimizer=MDMin, mic=False, steps=1000)  # Improved NEB initial guess with IDPP

Path('idpp').mkdir(parents=True, exist_ok=True)

for i, image in enumerate(neb.images):
    image.write('idpp/{}.xyz'.format(i))

Path('iter0').mkdir(parents=True, exist_ok=True)

for i, image in enumerate(neb.images):
    image.write('iter0/{}.xyz'.format(i))

for i, image in enumerate(neb.images):
    image.calc = GPAW(txt='NEB_{}.txt'.format(i), xc='PBE',
                      basis='aug-cc-pVDZ_PBE.sz',
                      mode=LCAO(force_complex_dtype=False),
                      h=0.18,
                      spinpol=True,
                      nbands='nao',
                      eigensolver=LCAOETDM(
                      searchdir_algo={"name": "L-BFGS-P"}),
                      occupations={'name': 'fixed-uniform'},
                      mixer={'backend': 'no-mixing'},
                      convergence={'energy': 1.0e-7, 'forces': 1.0e-4},
                      symmetry='off',
                      parallel={'domain': world.size})

opt = BFGS(neb, trajectory='gpaw.trj', logfile='qn.log', maxstep=0.05)
opt.run(fmax=0.25)

Path('iter1').mkdir(parents=True, exist_ok=True)

for i, image in enumerate(neb.images):
    image.write('iter1/{}.xyz'.format(i))
    image.calc.write('iter1/{}.gpw'.format(i), mode='all')


nebtools = NEBTools(neb.images)
Ef, dE = nebtools.get_barrier()

print("Barrier interpolated:", Ef, "Change in energy:", dE)

Ef2, dE2 = nebtools.get_barrier(fit=False)

print("Barrier NO interpolated:", Ef2, "Change in energy:", dE2)
