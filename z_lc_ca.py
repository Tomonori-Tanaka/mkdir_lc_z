import re


def replace_text_body(text_body, **replace_keyword):
    """
    Replace body text with key(GLOBAL VARIABLE!!!) and value.
    :param body_text: body text which will be replaced
    :param replace_keyword: dict consists of replaced keyword (global variable) and the value.
    :return: Replaced body text
    """
    for key, value in replace_keyword.items():
        body_text = re.sub(globals()[key], value, text_body)
    return text_body


if __name__ == '__main__':
    import argparse
    import numpy as np
    from numpy import linspace
    import operate_dir_tree
    import shutil

    JOB_SCRIPT_NAME = "job.sh"
    JOB_SUBMIT_COMMAND = "pjsub"
    ANGSTROM_TO_BOHR = 1.8897261246364832
    REPLACED_KEYWORD_LATTICE_CONST = "AAAAA"
    REPLACED_KEYWORD_ATOMIC_NUM = "ZZZZZ"
    REPLACED_KEYWORD_C_OVER_A = "CCCCC"
    # Replaced keyword for tc or j mode. Usually it is "go"
    REPLACED_KEYWORD_SCF_MODE = "go"
    AFTER_DECIMAL_POINT_LATTICE_CONST_DIR = 2
    AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR = 1
    AFTER_DECIMAL_POINT_C_OVER_A = 6
    # decimal point of lattice constant in the input file of AkaiKKR.
    AFTER_DECIMAL_POINT_BOHR = 5
    POTENTIAL_FILE_NAME = "potential.data"
    CONVERGENCE_CHECK_KEYWORD = "no convergence"
    OUTPUT_FILE_NAME = "output.dat"

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
    parser.add_argument('lattice_constant_num', type=int, help=help_text)

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

    help_text = 'input file name of AkaiKKR'
    parser.add_argument('input_file_name', help=help_text)

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
    atomic_number_list = np.round(atomic_number_list, AFTER_DECIMAL_POINT_ATOMIC_NUM_DIR)
    lattice_constant_list = linspace(args.lattice_constant_start,
                                     args.lattice_constant_end,
                                     args.lattice_constant_num,
                                     endpoint=True)
    lattice_constant_list = np.round(lattice_constant_list, AFTER_DECIMAL_POINT_LATTICE_CONST_DIR)
    c_over_a_list = linspace(args.c_over_a_start,
                             args.c_over_a_end,
                             args.c_over_a_num,
                             endpoint=True)
    c_over_a_list = np.round(c_over_a_list, AFTER_DECIMAL_POINT_C_OVER_A)

    if args.subdir_name:
        tree_instance = operate_dir_tree.OperationDirTree(atomic_number_list,
                                                          lattice_constant_list,
                                                          c_over_a_list,
                                                          [args.subdir_name])
    else:
        tree_instance = operate_dir_tree.OperationDirTree(atomic_number_list,
                                                          lattice_constant_list,
                                                          c_over_a_list)

    if args.action == 'make':
        tree_instance.make_directory()
        with open(args.input_file_name, mode='r', encoding='utf-8') as f:
            body_source = f.read()
        if args.subdir_name is None:
            kkr_mode = "go"
        else:
            kkr_mode = args.subdir_name

        lists_of_dirs = tree_instance.get_each_element_in_paths()
        for list in lists_of_dirs:
            atomic_number = list[0]
            lattice_constant_bohr = round(list[1] * ANGSTROM_TO_BOHR, AFTER_DECIMAL_POINT_BOHR)
            c_over_a = list[2]

            path_scf = "/".join(map(str, [list[0], list[1], list[2]]))
            body_replaced = replace_text_body(body_source,
                                              REPLACED_KEYWORD_ATOMIC_NUM=str(atomic_number),
                                              REPLACED_KEYWORD_LATTICE_CONST=str(lattice_constant_bohr),
                                              REPLACED_KEYWORD_C_OVER_A=str(c_over_a),
                                              REPLACED_KEYWORD_SCF_MODE=kkr_mode)
            with open(f"{path_scf}/{args.input_file_name}", mode='w', encoding='utf-8') as f:
                f.write(body_replaced)
            if args.subdir_name:
                shutil.copy(f'{path_scf}/{POTENTIAL_FILE_NAME}', f"{path_scf}/{args.subdir_name}")
        tree_instance.copy_files("temporary.dat", JOB_SCRIPT_NAME)


    elif args.action == 'del':
        tree_instance.delete_directory()
    elif args.action == 'job':
        tree_instance.job_execution(job_command=JOB_SUBMIT_COMMAND, job_script=JOB_SCRIPT_NAME)
