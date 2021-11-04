import argparse
import os
import re
import shutil

import numpy as np

ANGSTROM_TO_BOHR = 1.8897261246364832
REPLACED_KEYWORD_LATTICE_CONST = "AAAAA"
REPLACED_KEYWORD_ATOMIC_NUM = "ZZZZZ"
AFTER_DECIMAL_POINT_LATTICE_CONST_DIR = 2
AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR = 1
AFTER_DECIMAL_POINT_BOHR = 5
JOB_SCRIPT_NAME = "job.sh"
JOB_EXECUTION_COMMAND = f"pjsub {JOB_SCRIPT_NAME}"

parser = argparse.ArgumentParser(description='Make directory trees. lattic const/atomic number/')

phelp = 'start lattice constant (Angstrom)'
parser.add_argument('lattice_const_start', type=float, help=phelp)

phelp = 'end lattice constant (Angstrom'
parser.add_argument('lattice_const_end', type=float, help=phelp)

phelp = 'division number (number of directory) of lattice constant'
parser.add_argument('division_num_lattice_const', type=int, help=phelp)

phelp = 'start atomic number'
parser.add_argument('atomic_number_start', type=float, help=phelp)

phelp = 'end atomic number'
parser.add_argument('atomic_number_end', type=float, help=phelp)

phelp = 'division number (number of directory) of atomic number'
parser.add_argument('division_num_atomic_num', type=int, help=phelp)

phelp = 'input file name of AkaiKKR'
parser.add_argument('input_file_name', help=phelp)

phelp = 'execute job script'
parser.add_argument('--job', action='store_true', help=phelp)

args = parser.parse_args()

lattice_constants = np.linspace(args.lattice_const_start, args.lattice_const_end, args.division_num_lattice_const,
                                endpoint=True)
atomic_numbers = np.linspace(args.atomic_number_start, args.atomic_number_end, args.division_num_atomic_num,
                             endpoint=True)

# read body from input file
with open(args.input_file_name, mode='r', encoding='utf-8') as f:
    body_source = f.read()

if not args.job:
    for lattice_const in lattice_constants:
        for atomic_num in atomic_numbers:
            # lattice_const = round(lattice_const, AFTER_DECIMAL_POINT_LATTICE_CONST)
            lattice_const_bohr = round(lattice_const * ANGSTROM_TO_BOHR, AFTER_DECIMAL_POINT_BOHR)
            lattice_const_str = "%.*f" % (AFTER_DECIMAL_POINT_LATTICE_CONST_DIR, lattice_const)
            atomic_num = round(atomic_num, AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR)
            atomic_num_str = "%.*f" % (AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR, atomic_num)
            body_replaced = re.sub(REPLACED_KEYWORD_LATTICE_CONST, str(lattice_const_bohr), body_source)
            body_replaced = re.sub(REPLACED_KEYWORD_ATOMIC_NUM, str(atomic_num), body_replaced)
            try:
                path = lattice_const_str + "/" + atomic_num_str + "/"
                os.makedirs(path)
            except:
                print('WARNING! Something wrong happened at the make directory part.')
            with open(f'{path}{args.input_file_name}', mode='w', encoding='utf-8') as f:
                f.write(body_replaced)
            shutil.copy(JOB_SCRIPT_NAME, path)

if args.job:
    import subprocess
    path_root_dir = os.getcwd()
    for lattice_const in lattice_constants:
        for atomic_num in atomic_numbers:
            lattice_const_str = "%.*f" % (AFTER_DECIMAL_POINT_LATTICE_CONST_DIR, lattice_const)
            atomic_num = round(atomic_num, AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR)
            atomic_num_str = "%.*f" % (AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR, atomic_num)
            try:
                path = lattice_const_str + "/" + atomic_num_str + "/"
                os.chdir(path)
                subprocess.call(JOB_EXECUTION_COMMAND)
                os.chdir(path_root_dir)
            except:
                print('WARNING! Something wrong happened at the job execution part.')