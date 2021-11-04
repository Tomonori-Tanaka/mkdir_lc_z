import argparse
import numpy as np
import re
import os
import shutil

ANGSTROM_TO_BOHR = 1.8897261246364832
REPLACED_KEYWORD_LATTICE_CONST = "AAAAA"
REPLACED_KEYWORD_ATOMIC_NUM = "ZZZZZ"
AFTER_DECIMAL_POINT_LATTICE_CONST = 2
AFTER_DECOMAL_POINT_ATOMIC_NUM = 1
JOB_SCRIPT_NAME = "job.sh"

parser = argparse.ArgumentParser(description='Make directory trees. lattic const/atomic number/')

phelp = 'start lattice constant (Angstrom)'
parser.add_argument('lattice_const_start', type=float, help=phelp)

phelp = 'end lattice constant (Angstrom'
parser.add_argument('lattice_const_end', type=float, help=phelp)

phelp = 'division number (number of directory) of lattice constant'
parser.add_argument('division_num_lattice_const', type=int, help=phelp)

phelp = 'start atomic number'
parser.add_argument('atomic_number_start', type=int, help=phelp)

phelp = 'end atomic number'
parser.add_argument('atomic_number_end', type=float, help=phelp)

phelp = 'division number (number of directory) of atomic number'
parser.add_argument('division_num_atomic_num', type=int, help=phelp)

phelp = 'input file name of AkaiKKR'
parser.add_argument('input_file_name', help=phelp)

args = parser.parse_args()

lattice_constants = np.linspace(args.lattice_const_start, args.lattice_const_end, args.division_num_lattice_const,
                         endpoint=True)
atomic_numbers = np.linspace(args.atomic_number_start, args.atomic_number_end, args.division_num_atomic_num,
                             endpoint=True)

# read body from input file
with open(args.input_file_name, mode='r', encoding='utf-8') as f:
    body_source = f.read()

for lattice_const in lattice_constants:
    for atomic_num in atomic_numbers:
        lattice_const = round(lattice_const, AFTER_DECIMAL_POINT_LATTICE_CONST)
        atomic_num = round(atomic_num, AFTER_DECOMAL_POINT_ATOMIC_NUM)
        body_replaced = re.sub(REPLACED_KEYWORD_LATTICE_CONST, str(lattice_const), body_source)
        body_replaced = re.sub(REPLACED_KEYWORD_ATOMIC_NUM, str(atomic_num), body_replaced)
        try:
            path = str(lattice_const) + "/" + str(atomic_num) + "/"
            os.makedire
        except:
            print('WARNING! Something wrong happened at the make directory part.')
        with open('{0}{1}'.format(path, args.input_file_name), mode-'w', encoding='utf-8') as f:
            f.write(body_replaced)
        shutil.copy(JOB_SCRIPT_NAME, path)
