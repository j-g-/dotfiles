#!/bin/env python
# Dotfiles symlinks handler script, with support for storing defined files and
# symlink paths in a file.json file, each directory represents a package
# paths are expanded as /home-dir/dotdir/package/file and a simlink is placed
# /home-dir/"defined_path"
# options for testing symlinked files, listing packages in json , and 
# prewiewing what symlinks may be created are included as aguments
# TODO:
# options for backing up existing configurations files that might be found 
# create a tk gui

import os
from io import StringIO
import json
import shutil
import argparse
import sys

home_dir = os.environ["HOME"]
dotdir =  os.path.join(home_dir,'.dotfiles')
backup_dir =  os.path.join(home_dir ,'.dotfiles.backup')
version = "0.1"
rows, cols = os.popen('stty size', 'r').read().split()
rows, cols = int(rows) , int(cols)

#TODO use these:
#dot_local_repo =  os.environ["HOME"] + "/.dotfiles/repo/"
#dot_repo_url = "" 
dot_files = { }
class CLS:
    """ Colors and tags for terminal """
    dark      = '\033[30m'
    red       = '\033[31m'
    green     = '\033[32m'
    yellow    = '\033[33m' 
    blue      = '\033[34m'
    magenta   = '\033[35m'
    lightblue = '\033[36m'
    none      = '\033[0m'

    bdark      = '\033[40m'
    bred       = '\033[41m'
    bgreen     = '\033[42m'
    byellow    = '\033[43m' 
    bblue      = '\033[44m'
    bmagenta   = '\033[45m'
    blightblue = '\033[46m'
    tags = {
        'symlinked':          bgreen+dark  +'   Symlinked!   '+none+' ',
        'warn_not_symlink':   bred+dark    +' Not Symlinked! '+none+' ',
        'warn_wrong_symlink': bmagenta+dark+' Wrong Symlink! '+none+' ',
        'warn_fnoexist':      bred+dark    +'    No File!    '+none+' ',
        'package':            bgreen+dark  +' Package '+none+' ',
    }
    
# TODO: Implement DotPath object for handling multi-os cases
#class DotPath(object):
    #"""docstring for Path"""
    #def __init__(self, package, source, dest_dict ):
        #super(Path, self).__init__()
        #self.source = source
        #self.dest_dict = dest_dict
        
    #def check(self):
        #"""docstring for check"""

    #def expand(self):
        #"""docstring for check"""
        
class WrongSymlinkError(OSError):
    """docstring for WrongSymlinkError"""
    def __init__(self, bad_dest, file_in_home):
        self.file_in_home = file_in_home
        self.bad_dest = bad_dest
    def __str__(self):
        return repr(self.bad_dest),repr(self.file_in_home)

class DotFileExistsError(OSError):
    """ Error when file  already exists """
    def __init__(self, dest=u""):
        self.dest = dest
    def __str__(self):
        return repr(self.dest)
        
class DotFileNotFoundError(OSError):
    """ Error when file doesn't exists """
    def __init__(self, dest=u""):
        self.dest = dest
    def __str__(self):
        return repr(self.dest)

class DotFile:
    """docstring for DotFile"""
    def __init__(self, package_name = "", paths = dict()):
        self.package_name = package_name
        self.paths_dict = paths
        self.expanded_paths_dict =  self.expandPaths(paths)

    def addPath(self):
        pass

    def readPaths(self):
        """docstring for readPaths"""
        pass

    def backup(self, file_name):
        source, dest = self.expandLink(file_name)
        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)
        backup_path=os.path.join(backup_dir,self.package_name,file_name)
        os.makedirs(os.path.dirname(backup_path))
        shutil.copyfile(dest,backup_path)


    def symlinkPaths(self):
        """docstring for symlinkPaths"""
        paths_dict = self.paths_dict
        print ( CLS.yellow + (cols * "-")+ CLS.none)
        print (" Symlinking package: " + CLS.magenta + self.package_name + CLS.none)
        print ( CLS.yellow + (cols * "-")+ CLS.none)
        for file_name in paths_dict: 
            source, dest = self.expandLink(file_name)
            try:
                if self.isLinked(file_name):
                    print(CLS.tags["symlinked"] + CLS.green + dest + 
                        CLS.none + " -> " + CLS.lightblue + source + CLS.none +
                        " was symlinked")
                    #Symlink done go to next
                    continue
            except WrongSymlinkError as e:
                print(CLS.tags["warn_wrong_symlink"] + CLS.red +  dest + 
                    CLS.none + " -> " + CLS.yellow + os.readlink(dest)+ CLS.none)
                print("Correcting! delting link " + dest)
                os.remove(dest)

            except DotFileExistsError as e:
                print(CLS.tags["warn_not_symlink"] + CLS.red +  dest + CLS.none) 
                print("Correcting! making backup of found file ")
                self.backup(file_name)
                os.remove(dest)

            except DotFileNotFoundError as e:
                print(CLS.tags["warn_fnoexist"] +  dest )
                base_path = os.path.dirname(dest)
                if not os.path.exists(base_path):
                    os.makedirs(base_path)

            #Doing symlink
            print (CLS.tags["package"]+self.package_name + ">> symlinking "+
                    " source: " + CLS.green+source + CLS.none + 
                    " dest: " + CLS.lightblue+dest )
            os.symlink(source,dest)


    def isLinked(self, file_name):
        source, dest = self.expandLink(file_name)
        if os.path.exists(dest)  and os.path.exists(source):
            if  os.path.islink(dest):
                if  os.readlink(dest) == source :
                    return True
                else:
                    raise WrongSymlinkError(dest, os.readlink(dest))
            else:
                raise DotFileExistsError(dest)

        else:
            raise DotFileNotFoundError(dest)



    def removePaths(self):
        """docstring for symlinkPaths"""
        pass

    def restorePaths(self):
        """docstring for restorePaths"""
        pass

    def printPaths(self, compact=False):
        """""
        Prints the paths in this DotConfig, with a source and destination 
        for the symlink, the paths are expanded by default
        """

        print( CLS.lightblue + (cols * "-")+ CLS.none)
        print(" Files for package: "+ CLS.green + self.package_name + CLS.none)
        print( CLS.lightblue + (cols * "-")+ CLS.none)

        paths_dict =  dict()
        
        if compact :
            paths_dict = self.paths_dict
        else:
            paths_dict = self.expanded_paths_dict


        for f in paths_dict:
            source = f 
            dest = paths_dict[f]
            print(CLS.yellow+"Symlink: " + 
                    CLS.green + dest +
                    CLS.none+" >> "+
                    CLS.lightblue + source + CLS.none)

    def expandPaths(self, paths={}):
        expanded_paths={}
        for file_name in paths:
            src, dest = self.expandLink(file_name)
            expanded_paths[src]=dest
        return expanded_paths

    def expandLink(self, file_name):
        """ 
        Expands a set of paths to symlink, 
        returns file_in_repo, file_in_home
        """
        file_in_repo = os.path.join(dotdir,self.package_name,file_name)
        file_in_home = os.path.join(home_dir,self.paths_dict[file_name])
        return file_in_repo, file_in_home
    
    def testPaths(self):
        """Test if expanded paths are symlinked"""
        paths_dict = self.paths_dict
        print ( CLS.yellow + (cols * "-")+ CLS.none)
        print (" Test package: " + CLS.magenta + self.package_name + CLS.none)
        print ( CLS.yellow + (cols * "-")+ CLS.none)
        for file_name in paths_dict: 
            source, dest = self.expandLink(file_name)
            try:
                if self.isLinked(file_name):
                    print(CLS.tags["symlinked"] + CLS.green + dest + 
                        CLS.none + " -> " + CLS.lightblue + source + CLS.none)
            except WrongSymlinkError as e:
                print(CLS.tags["warn_wrong_symlink"] + CLS.red +  dest + 
                    CLS.none + " -> " + CLS.yellow + os.readlink(dest)+ CLS.none)
            except DotFileExistsError as e:
                print(CLS.tags["warn_not_symlink"] + CLS.red +  dest + CLS.none) 
            except DotFileNotFoundError as e:
                print(CLS.tags["warn_fnoexist"] +  dest )

def print_filled(text=""):
    fill = int( (int(cols) - len(text))/2 )
    fill2 = (int(cols) - len(text)) - fill
    print ( CLS.bgreen+fill*" " + CLS.dark+text + 
            CLS.bgreen+fill2*" "  +  CLS.none)
    
    

def createDotfiles():
    """docstring for createDotfiles"""
    #io =  StringIO()
    jd = json.JSONDecoder()
    f_dotstore = open(dotdir +"/files.json")

    dotdict = jd.decode(f_dotstore.read())
    f_dotstore.close()
    #print(dotdict)
    dot_files = dict()

    for package in dotdict:
        paths_dict = dotdict[package]
        dot_files[package] = DotFile(package, paths_dict)

    return dot_files

def updateDotfiles():
    """docstring for updateDotfiles"""
    #TODO
    pass

def restoreDotfiles():
    """docstring for restoreDotfiles"""
    pass

def disableDotfile():
    """docstring for restoreDotfiles"""
    pass

def checkDotfiles(packages=None):
    print_filled(" Printing configuration files for packages in files.json " )
    #Printing
    if len(packages) == 0 or packages == ['all']:
        for package in dot_files :
            dot_files[package].printPaths()
    else :
        for package in packages :
            dot_files[package].printPaths()

def listDotfiles():
    print_filled(" Printing packages available in files.json " )
    #Printing
    for package in dot_files :
       print(CLS.tags["package"]+ package)

def testDotfiles(packages=None): 
    print_filled(" Testing configuration files for packages in files.json " )
    #Testing
    if len(packages) == 0 or packages == ['all']:
        for package in dot_files :
            dot_files[package].testPaths()
    else :
        for package in packages :
            dot_files[package].testPaths()

def enableDotfiles(packages=[]):
    """docstring for restoreDotfiles"""
    if packages == ['all'] :
        for pac in dot_files:
            dot_files[pac].symlinkPaths()
    else:
        for pac in packages:
            dot_files[pac].symlinkPaths()

def commitPush():
    """docstring for restoreDotfiles"""
    pass

def getArgs():
    """Parses command-line arguments and returns args if sys.argv has more 
    than 1 argument, otherwise prints help and exits"""
    parser = argparse.ArgumentParser( 
            prog="dotfiles.py",
            description="Dotfiles symlinks handler")
    parser.add_argument("-s", "--show",  action="store_true",
            help="Prints the list of dotfiles in files.json")

    parser.add_argument("-t", "--test", action="store_true",
            help="Prints a test for the symlinks that should be placed")

    parser.add_argument("-l", "--list", action="store_true",
            help="Prints packages avilabe in files.json")

    parser.add_argument("-e", "--enable", action="store_true",
            help="Enables a set of cofiguration files for package")

    parser.add_argument("-d", "--disable", action="store_true",
            help="Disables a set of cofiguration files for package")

    parser.add_argument("-u", "--update", action="store_true",
            help="Update a set of cofiguration files for package")

    parser.add_argument("-r", "--restore", action="store_true",
            help="Restore a set of cofiguration files for package")

    parser.add_argument("packages", nargs=argparse.REMAINDER )

    parser.add_argument("-c", "--chage-repo", dest="repo", action="store",
            help="Change the repository of cofiguration files to repo")

    parser.add_argument("-p", "--push-changes",action="store_true",
            help="Push changes in the repository repo to remote origin")

    args = parser.parse_args()

    if  len(sys.argv) < 2:
        parser.print_help()
        exit(1)
    else:
        return args
    
if __name__ == '__main__':
    dot_files = createDotfiles()
    args = getArgs()
    if args.show:
        checkDotfiles(args.packages)
    if args.test:
        testDotfiles(args.packages)
    if args.enable:
        enableDotfiles(args.packages)
    if args.list:
        listDotfiles()
    exit()
