import os

def setcwd_to_file_location(file):
    abspath = os.path.abspath(file)
    dname = os.path.dirname(abspath)
    os.chdir(dname)