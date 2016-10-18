#! /usr/bin/python3
# -*- coding: utf-8 -*-

'''
      Copyright 2016,暗夜幽灵 <darknightghost.cn@gmail.com>

      This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    at your option) any later version.

      This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

      You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import shutil

class Version:
    def __init__(self, ver_str):
        self.main_ver = int(ver_str.strip()[: -2])
        self.sub_ver = int(ver_str.strip()[-2 :])

    def __str__(self):
        return "%d%.2d"%(self.main_ver, self.sub_ver)

    def __lt__(self, o):
        if self.main_ver > o.main_ver:
            return False

        elif self.main_ver == o.main_ver:
            if self.sub_ver >= o.sub_ver:
                return False

        return True

    def __gt__(self, o):
        if self.main_ver < o.main_ver:
            return False

        elif self.main_ver == o.main_ver:
            if self.sub_ver <= o.sub_ver:
                return False

        return True

    def __eq__(self, o):
        if self.main_ver == o.main_ver \
                and self.sub_ver == o.sub_ver:
            return True

        else:
            return False

    def __ne__(self, o):
        return not self.__eq__(o)

    def __ge__(self, o):
        return not self.__lt__(o)

    def __le__(self, o):
        return not self.__gt__(o)

class PatchFile:
    def __init__(self, path, version, size):
        self.path = path
        self.version = version
        self.size = size

    def __lt__(self, o):
        return self.path < o.path

    def __gt__(self, o):
        return self.path > o.path

    def __eq__(self, o):
        return self.path == o.path

    def __ne__(self, o):
        return not self.__eq__(o)

    def __ge__(self, o):
        return not self.__lt__(o)

    def __le__(self, o):
        return not self.__gt__(o)

    def get_game_file(self):
        return GameFile(self.path, self.version)

class GameFile:
    def __init__(self, path, version):
        self.path = path
        self.version = version
    
    def __lt__(self, o):
        return self.path < o.path

    def __gt__(self, o):
        return self.path > o.path

    def __eq__(self, o):
        return self.path == o.path

    def __ne__(self, o):
        return not self.__eq__(o)

    def __ge__(self, o):
        return not self.__lt__(o)

    def __le__(self, o):
        return not self.__gt__(o)

    def __str__(self):
        return "%s,%s"%(self.path, str(self.version))

def main(argv):
    if len(argv) < 2:
        usage(argv[0])
        return 0

    #Load file list
    print("Loading game files...\n")
    game_list_file, game_file_dict = load_game_file_dict()

    print("Loading patch files...\n")
    patch_path, patch_file_dict = load_patch_file_dict(argv[1])

    print("Checking patch files...\n")
    for k in patch_file_dict.keys():
        if os.path.getsize(os.path.join(patch_path, k).replace("\\", os.sep)) \
                != patch_file_dict[k].size:
            print("Size of file \"%s\" is incorrect!", 
                    os.path.join(patch_path, k))
            return -1

    #Join list and copy file
    file_list = []

    #Join list 
    for f in game_file_dict.keys():
        if not f in patch_file_dict:
            file_list.append(str(game_file_dict[f]) + "\n")

    for f in patch_file_dict.keys():
        if f in game_file_dict.keys():
            if patch_file_dict[f].version <= game_file_dict[f].version:
                file_list.append(str(game_file_dict[f]) + "\n")
                continue

        #Copy file
        print("Copying file \"%s\"..."%(f.replace("\\", os.sep)))
        dst = os.path.abspath(f.replace("\\", os.sep))
        create_dirs(dst)
        shutil.copy(os.path.join(patch_path, f).replace("\\", os.sep),
                dst);

        #Join list
        file_list.append(str(patch_file_dict[f].get_game_file()) + "\n")

    file_list.sort()
    f = open(game_list_file, "w")
    f.writelines(file_list)
    f.close()
    return 0

def create_dirs(path):
    d = os.path.split(path)[0]
    if not os.path.exists(d):
        create_dirs(d)
        os.mkdir(d)

def usage(name):
    print("Usage:\n" \
            "\t%s update.lst-in-patch"%(name))

def load_game_file_dict():
    game_list_file = ""
    for f in os.listdir():
        if f.lower() == "update.lst":
            game_list_file = f
            print("\"%s\" founded in game directory."%(f))
            break

    if game_list_file == "":
        print("\"update.lst\" not found.")
        exit(-1)

    f = open(game_list_file, "r")
    l = f.readlines()
    f.close()
    
    ret = {}
    
    for f in l:
        t = f.split(",")
        ret[t[0]] = GameFile(t[0], Version(t[1]))

    return game_list_file, ret

def load_patch_file_dict(path):
    f = open(path, "r")
    l = f.readlines()
    f.close()

    file_dict = {}
    for f in l:
        t = f.split(",")
        file_dict[t[2]] = PatchFile(t[2], Version(t[5]), int(t[3]))

    data_path = os.path.split(os.path.abspath(path))[0]
    for d in os.listdir(data_path):
        if d.lower() == "data":
            data_path = data_path + os.sep + d

    return data_path, file_dict

ret = main(sys.argv)
exit(ret)
