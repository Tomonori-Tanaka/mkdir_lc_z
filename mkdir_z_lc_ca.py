import argparse
import re

from numpy import linspace

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
JOB_EXECUTION_COMMAND = f"pjsub {JOB_SCRIPT_NAME}"
CONVERGENCE_CHECK_KEYWORD = "no convergence"
OUTPUT_FILE_NAME = "output.dat"


def return_path(*dir_names):
    """
    Return path of the directory.
    :param dir_names: The names of hierarchies
    :return: path of the directory
    """
    path = ""
    for name in dir_names:
        path = path + name + "/"
    return path


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make directory trees: '
                                                 'atomic_num/lattice_const/c_over_a/')
    help_text = 'start atomic number'
    parser.add_argument('atomic_number_start', type=float, help=help_text)
    help_text = 'end atomic number'
    parser.add_argument('atomic_number_end', type=float, help=help_text)
    help_text = 'element number of atomic number list'
    parser.add_argument('atomic_number_num', type=int, help=help_text)

    help_text = 'start lattice constant in the conventional bcc cell (Angstrom)'
    parser.add_argument('lattice_constant_start', type=float, help=help_text)
    help_text = 'end lattice constant in the conventional bcc cell (Angstrom)'
    parser.add_argument('lattice_constant_end', type=float, help=help_text)
    help_text = 'element number of lattice constant list'
    parser.add_argument('lattice_const_num', type=int, help=help_text)

    help_text = 'start c/a'
    parser.add_argument('c_over_a_start', type=float, help=help_text)
    help_text = 'end c/a'
    parser.add_argument('c_over_a_end', type=float, help=help_text)
    help_text = 'element number of c/a list'
    parser.add_argument('c_over_a_num', type=int, help=help_text)

    help_text = 'action of this script. ' \
                '"make": make directory trees. ' \
                '"job": execute job script. ' \
                '"del": delete directory trees.'
    parser.add_argument('action', choices=['make', 'job', 'del'], help=help_text)

    limit_group = parser.add_mutually_exclusive_group()

    help_text = 'subdirectory name; Keyword is restricted to "tc" or "j" in the current version.'
    limit_group.add_argument('-sub', '--subdir_name', choices=['tc', 'j'], help=help_text)

    help_text = 'absolute path of root dir when copying potential file; ' \
                'This option is only available for the make action not including subdir_name option.'
    limit_group.add_argument('-path', '--root_path', help=help_text)

    help_text = 'calculate only not convergence systems'
    parser.add_argument('--re_calc', action='store_true', help=help_text)

    args = parser.parse_args()

    atomic_number_list = linspace(args.atomic_number_start,
                                  args.atomic_number_end,
                                  args.atomic_number_num,
                                  endpoint=True)
    lattice_constant_list = linspace(args.lattice_const_start,
                                     args.lattice_const_end,
                                     args.lattice_const_num,
                                     endpoint=True)
    c_over_a_list = linspace(args.c_over_a_start,
                             args.c_over_a_end,
                             args.c_over_a_num,
                             endpoint=True)
