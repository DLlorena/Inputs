from gpaw import GPAW, PW, LCAO
from ase.units import Bohr
from ase.build import molecule
from gpaw.directmin.tools import excite
#from gpaw.directmin.etdm_fdpw import FDPWETDM
from gpaw.directmin.etdm_lcao import LCAOETDM
from gpaw.transformers import Transformer
from gpaw.point_groups import SymmetryChecker
from ase import Atoms
import numpy as np
from ase.io import write
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if comm.rank != 0:
    import sys
    sys.stdout = open('/dev/null', 'w')
# =================================================
# Ground State S0

# Formaldehyde molecule:
# Original positions in angstrom
positions_angstrom = [
[-0.02005088520756,  1.50224677470908,  0.90586617327203],   # C
[ 0.17929366751810,  1.97471547362850,  2.22295844064821],   # C
[ 1.04323797524160,  1.58037088780316, -0.02371269229043],   # C
[ 1.40306976369694,  2.50293053080525,  2.59665086046720],   # C
[ 2.25612866618743,  2.12865808658246,  0.36364266547859],   # C
[ 2.44539454360201,  2.59232560934093,  1.66855708430474],   # C
[-1.31739537632249, -0.73247127245774, -0.89873413956414],   # C
[-1.63177040290844, -1.13519358480075, -2.21655708802218],   # C
[-0.84880869373490, -1.69639914557676,  0.02427870986690],   # C
[-1.47646305785466, -2.45697194235031, -2.59760532976765],   # C
[-0.71653055383054, -3.01875069680063, -0.37032435242747],   # C
[-1.02745955464158, -3.40835152469566, -1.67617692160747],   # C
[-0.65300194702562,  1.91816944155049,  2.92270330892296],   # H
[ 0.88742269690473,  1.24121807035223, -1.04538308511192],   # H
[ 1.54721678134824,  2.86534677945914,  3.61402686879606],   # H
[ 3.06408046850727,  2.21338136129519, -0.36261321920596],   # H
[ 3.39801642965784,  3.03397279106001,  1.95826145298148],   # H
[-2.00269385746000, -0.38312331475379, -2.91105551263690],   # H
[-0.63007234993365, -1.39687332488294,  1.04682740786595],   # H
[-1.72171955158649, -2.75804942785159, -3.61568400411701],   # H
[-0.38239658328228, -3.76401947302623,  0.35098298900158],   # H
[-0.93260133346859, -4.45252335542659, -1.97146317439733],   # H
[-1.57841685171025,  0.57473086436707, -0.57172528307729],   # N
[-1.28447999369711,  1.07466039166946,  0.58627884062005],   # N
]

# Create the molecule object in angstroms
mol = Atoms('C12H10N2', positions=positions_angstrom)

calc = GPAW(mode=LCAO(force_complex_dtype=True),
    xc="PBE",
    h=0.18,
    # mode=FD(force_complex_dtype=True),
    # setups={atom: "upaw_eff"},
    # charge=charge,
    occupations={"name": "fixed-uniform"},
    # eigensolver=FDPWETDM(searchdir_algo={"name": "lbfgsp"}),
    eigensolver=LCAOETDM(
    searchdir_algo={"name": "L-BFGS-P"},
    localizationtype="pz",
    functional={
        "name": "PZ-SIC",
        "scaling_factor": (0.5, 0.5),
        # "upaw_core": corr,
        #"sic_coarse_grid": True,
        # "localscaling": {
        #     "LS": False,
        #     "variational": False,
        #     "type": "isoorb",
        #     "scale": 1.0,
        #     "debug": True,
        #     "val": 1,
        #     "core": True,
        #     "phase": False,
        #     "laplace": False,
        # },
        #grad_tol_pz_localization: 1.0e-4,
        },
        ),
    mixer={"backend": "no-mixing"},
    nbands="nao",
    #nbands=-5,
    spinpol=True,
    #basis="dzp",
    basis="aug-cc-pVDZ_PBE.sz",
    symmetry="off",
    #convergence={"eigenstates": 1e-8},
    maxiter=600,
    txt='pbe-sic-ts.txt')

mol.calc = calc
calc.atoms = mol
calc.create_setups(LCAO(), 'PBE')

# Set cell to contain basis functions entirely
rc = []
for a in range(len(calc.setups)):
    for l in range(len(calc.setups[a].basis.bf_j)):
        rc.append(calc.setups[a].basis.bf_j[l].rc * Bohr)
    mol.center(vacuum=max(rc))
print(max(rc))
max_l = max(mol.get_cell().diagonal())
mol.set_cell([max_l, max_l, max_l])
mol.center() 
gs = mol.get_potential_energy()
print("Ground state energy (eV): ", gs)

# Save calculation (like a chk point file)
calc.write('pbe-sic-ts.gpw', mode='all')
