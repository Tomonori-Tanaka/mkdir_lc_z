import argparse
import os
import sys
import re
import shutil

ANGSTROM_TO_BOHR = 1.8897261246364832
REPLACED_KEYWORD_LATTICE_CONST = "AAAAA"
REPLACED_KEYWORD_ATOMIC_NUM = "ZZZZZ"
# Replaced keyword for tc or j mode. Usually it is "go"
REPLACED_KEYWORD_SCF_MODE = "go"
AFTER_DECIMAL_POINT_LATTICE_CONST_DIR = 2
AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR = 1
# decimal point of lattice constant in the input file of AkaiKKR.
AFTER_DECIMAL_POINT_BOHR = 5
JOB_SCRIPT_NAME = "job.sh"
JOB_EXECUTION_COMMAND = f"pjsub {JOB_SCRIPT_NAME}"

parser = argparse.ArgumentParser(description='Make directory trees: '
                                             'lattice_const/atomic_number/')

phelp = 'start lattice constant (Angstrom)'
parser.add_argument('lattice_const_start', type=float, help=phelp)

phelp = 'end lattice constant (Angstrom)'
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

phelp = 'Action of this script.'
parser.add_argument('action', choices=['make', 'job', 'del'], help=phelp)

phelp = 'subdirectory name. Keyword is restricted to "tc" or "j" in the current version.'
parser.add_argument('-sub', '--subdir_name', choices=['tc', 'j'], help=phelp)

args = parser.parse_args()

from numpy import linspace

lattice_constants = linspace(args.lattice_const_start, args.lattice_const_end, args.division_num_lattice_const,
                             endpoint=True)
atomic_numbers = linspace(args.atomic_number_start, args.atomic_number_end, args.division_num_atomic_num,
                          endpoint=True)


def return_path(*dir_names):
    """
    Return absolute path of the directory.
    :param dir_names: The names of hierarchies
    :return: absolute path of the directory
    """
    # os.getcwd() returns the directory without end slash!
    path = os.getcwd() + "/"
    for name in dir_names:
        path = path + name + "/"
    return path


def replace_input_text(body_text, **replace_kewword):
    """
    Replace body text with key(GLOBAL VARIABLE!!!) and value.
    :param body_text: body text which will be replaced
    :param replace_kewword: dict consists of replaced keyword (global variable) and the value.
    :return: Replaced body text
    """
    for key, value in replace_kewword.items():
        body_text = re.sub(globals()[key], value, body_text)
    return body_text


# ----- main part -----
if args.action == "make":
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
            path_scf = return_path(lattice_const_str, atomic_num_str)
            path_destination = path_scf

            if args.subdir_name:
                if os.path.exists(path_scf):
                    pass
                else:
                    sys.exit("!ERROR!: Parent directory (SCF directory) does not exist.")
                path_destination = return_path(lattice_const_str, atomic_num_str, args.subdir_name)

            body_replaced = replace_input_text(body_source,
                                               REPLACED_KEYWORD_LATTICE_CONST=lattice_const_bohr,
                                               REPLACED_KEYWORD_ATOMIC_NUM=atomic_num_str,
                                               REPLACED_KEYWORD_SCF_MODE=kkr_mode)
            try:
                os.makedirs(path_destination)
            except:
                print("Caution! The directory tried to make already exists.")

            with open(f'{path_destination}{args.input_file_name}', mode='w', encoding='utf-8') as f:
                f.write(body_replaced)
            shutil.copy(JOB_SCRIPT_NAME, path_destination)
"""
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
            subprocess.call(JOB_EXECUTION_COMMAND.split())
            os.chdir(path_root_dir)
        except:
            print('WARNING! Something wrong happened at the job execution part.')
"""
