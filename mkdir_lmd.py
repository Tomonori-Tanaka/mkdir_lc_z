import argparse
import os
import re
import shutil
import sys
from numpy import linspace
import subprocess

ANGSTROM_TO_BOHR = 1.8897261246364832
REPLACED_KEYWORD_LATTICE_CONST = "AAAAA"
REPLACED_KEYWORD_ATOMIC_NUM = "ZZZZZ"
# Replaced keyword for tc or j mode. Usually it is "go"
REPLACED_KEYWORD_SCF_MODE = "go"
AFTER_DECIMAL_POINT_LATTICE_CONST_DIR = 2
AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR = 1
# decimal point of lattice constant in the input file of AkaiKKR.
AFTER_DECIMAL_POINT_BOHR = 5
POTENTIAL_FILE_NAME = "potential.data"
JOB_SCRIPT_NAME = "job.sh"
JOB_EXECUTION_COMMAND = f"sbatch {JOB_SCRIPT_NAME}"
CONVERGENCE_CHECK_KEYWORD = "no convergence"
OUTPUT_FILE_NAME = "output.dat"
FMG_FILE_NAME = "fmg.in"

parser = argparse.ArgumentParser(description='Make directory trees: '
                                             'lattice_const/atomic_number/')

help_text = 'start lattice constant (Angstrom)'
parser.add_argument('lattice_const_start', type=float, help=help_text)

help_text = 'end lattice constant (Angstrom)'
parser.add_argument('lattice_const_end', type=float, help=help_text)

help_text = 'division number (number of directory) of lattice constant'
parser.add_argument('division_num_lattice_const', type=int, help=help_text)

help_text = 'start atomic number'
parser.add_argument('atomic_number_start', type=float, help=help_text)

help_text = 'end atomic number'
parser.add_argument('atomic_number_end', type=float, help=help_text)

help_text = 'division number (number of directory) of atomic number'
parser.add_argument('division_num_atomic_num', type=int, help=help_text)

help_text = 'input file name of AkaiKKR'
parser.add_argument('input_file_name', help=help_text)

help_text = 'action of this script. ' \
            '"make": make directory trees. ' \
            '"job": execute job script. ' \
            '"del": delete directory trees.'
parser.add_argument('action', choices=['make', 'job', 'del'], help=help_text)

limit_group = parser.add_mutually_exclusive_group()

help_text = 'subdirectory name; Keyword is restricted to "tc" or "j" in the current version.'
limit_group.add_argument('-sub', '--subdir_name', choices=['tc', 'j'], help=help_text)

help_text = 'calculate only not convergence systems'
parser.add_argument('--re_calc', action='store_true', help=help_text)

args = parser.parse_args()


def replace_input_text(body_text, **replace_keyword):
    """
    Replace body text with key(GLOBAL VARIABLE!!!) and value.
    :param body_text: body text which will be replaced
    :param replace_keyword: dict consists of replaced keyword (global variable) and the value.
    :return: Replaced body text
    """
    for key, value in replace_keyword.items():
        body_text = re.sub(globals()[key], value, body_text)
    return body_text

lattice_constants = linspace(args.lattice_const_start, args.lattice_const_end, args.division_num_lattice_const,
                             endpoint=True)
atomic_numbers = linspace(args.atomic_number_start, args.atomic_number_end, args.division_num_atomic_num,
                          endpoint=True)
path_root = os.getcwd()
# read body from input file
with open(args.input_file_name, mode='r', encoding='utf-8') as f:
    body_source = f.read()

# kkr_mode will be used in text replacing step.
if args.subdir_name is None:
    kkr_mode = "go"
else:
    kkr_mode = args.subdir_name

for lattice_const in lattice_constants:
    for atomic_num in atomic_numbers:
        lattice_const_str = "%.*f" % (AFTER_DECIMAL_POINT_LATTICE_CONST_DIR, lattice_const)
        lattice_const_bohr = str(round(lattice_const * ANGSTROM_TO_BOHR, AFTER_DECIMAL_POINT_BOHR))
        atomic_num = round(atomic_num, AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR)
        atomic_num_str = "%.*f" % (AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR, atomic_num)
        # get the absolute path of scf directory
        path_scf = os.path.join(path_root, lattice_const_str, atomic_num_str, "lmd")
        path_destination = path_scf

        if args.subdir_name:
            if os.path.exists(path_scf):
                pass
            else:
                sys.exit("!ERROR!: Parent directory (SCF directory) does not exist.")
            path_destination = os.path.join(path_destination, args.subdir_name)

        if args.action == 'make':
            body_replaced = replace_input_text(body_source,
                                               REPLACED_KEYWORD_LATTICE_CONST=lattice_const_bohr,
                                               REPLACED_KEYWORD_ATOMIC_NUM=atomic_num_str,
                                               REPLACED_KEYWORD_SCF_MODE=kkr_mode)
            try:
                os.makedirs(path_destination)
                with open(os.path.join(path_destination, args.input_file_name), mode='w', encoding='utf-8') as f:
                    f.write(body_replaced)
                shutil.copy(JOB_SCRIPT_NAME, path_destination)
                shutil.copy(FMG_FILE_NAME, path_destination)

                # make lmd potential data
                if not args.subdir_name:
                    os.chdir(path_destination)
                    subprocess.run("fmg < fmg.in", shell=True)
                    os.chdir(path_destination)


                if args.subdir_name:
                    try:
                        shutil.copy(os.path.join(path_scf, POTENTIAL_FILE_NAME), path_destination)
                    except:
                        print("WARNING: Probably potential file data does not exist.")
            except FileExistsError as e:
                print(e.strerror)
                print(e.errno)
                print(e.filename)


        elif args.action == 'job':

            os.chdir(path_destination)
            if args.re_calc:
                with open(f'{path_destination}{OUTPUT_FILE_NAME}', mode='r', encoding='utf-8') as f:
                    output_file_body = f.read()
                    if CONVERGENCE_CHECK_KEYWORD in output_file_body:
                        subprocess.call(JOB_EXECUTION_COMMAND.split())
                    else:
                        continue
            else:
                subprocess.call(JOB_EXECUTION_COMMAND.split())

        elif args.action == 'del':
            try:
                shutil.rmtree(path_destination)
            except:
                print('WARNING! Something wrong happened at the remove directory part.')
