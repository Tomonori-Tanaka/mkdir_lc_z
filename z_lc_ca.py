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
    from numpy import linspace
    import operate_dir_tree

    JOB_SCRIPT_NAME = "job.sh"
    JOB_SUBMIT_COMMAND = "pjsub"

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
    lattice_constant_list = linspace(args.lattice_constant_start,
                                     args.lattice_constant_end,
                                     args.lattice_constant_num,
                                     endpoint=True)
    c_over_a_list = linspace(args.c_over_a_start,
                             args.c_over_a_end,
                             args.c_over_a_num,
                             endpoint=True)

    with open(args.input_file_name, mode='r', encoding='utf-8') as f:
        body_source = f.read()

    if args.subdir_name is None:
        kkr_mode = "go"
    else:
        kkr_mode = args.subdir_name

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
    elif args.action == 'del':
        tree_instance.delete_directory()
    elif args.action == 'job':
        tree_instance.job_execution(job_command=JOB_SUBMIT_COMMAND, job_script=JOB_SCRIPT_NAME)

