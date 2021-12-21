import os
import pprint
import shutil
import subprocess

JOB_SCRIPT_NAME = "job.sh"
JOB_SUBMIT_COMMAND = "pjsub"


class OperationDirTree:

    def __init__(self, *dir_name_lists):
        self.path_parent = os.getcwd()
        self.list_of_dir_name_list = self.__get_cartesian_product(dir_name_lists)
        self.list_path = []
        for name_list in self.list_of_dir_name_list:
            name_list = list(name_list)
            self.list_path.append('/'.join(map(str, name_list)))

    def __get_cartesian_product(self, lists):
        result = [[]]
        for list in lists:
            result = [x+[y] for x in result for y in list]
        return result

    def print_dir_trees(self):
        pprint.pprint(self.list_path)

    def run(self, func):
        for path_destination in self.list_path:
            func(path_destination)

    def make_directory(self):
        for path_destination in self.list_path:
            os.makedirs(path_destination)

    def delete_directory(self):
        for path_destination in self.list_path:
            shutil.rmtree(path_destination)

    def job_execution(self, job_command, job_script):
        for path_destination in self.list_path:
            os.chdir(path_destination)
            subprocess.call([job_command, job_script])
            os.chdir(self.path_parent)

    def copy_files(self, *files):
        for path_destination in self.list_path:
            for file in files:
                shutil.copy(file, path_destination)

