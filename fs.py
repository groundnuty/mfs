#!/usr/bin/env python

import logging

from collections import defaultdict
from errno import ENOENT
from sys import argv, exit
import time 
import stat
import os   

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

class AnnexFS(LoggingMixIn, Operations):
    def __init__(self, src_path):
        if not os.path.isdir(src_path):
            raise StandardError("Source directory does not exist.")
        self.src_path = src_path.encode("utf-8")
  
    def open(self, path, flags):
        handlers = {
                "MP3_EXISTING": self.open_mp3_existing,
                "MP3_MISSING":  self.open_mp3_missing,
                "PASSTHROUGH":  self.open_passthrough
            }
        return handlers[self.which_case(path)](path, flags)

    def open_mp3_existing(self, path, flags):
        # docelowo: otwiera plik zrodlowy
        base_path = self.src_path + path
        return os.open("/Volumes/HDD/Music/Muzyka/Salsowe/Kizomba/2014/Nelson Freitas - I Wish.mp3", flags)

    def open_mp3_missing(self, path, flags):
        # docelowo: zwraca 0
        base_path = self.src_path + path
        return os.open("/Volumes/HDD/Music/Muzyka/Salsowe/Cubana/Antonio Da Costa - Ginecologo del Ritmo.mp3", flags)

    def open_passthrough(self, path, flags):
        base_path = self.src_path + path
        return os.open(base_path, flags)

    def release(self, path, fh):
        return os.close(fh) 

    def read(self, path, size, offset, fh):
        base_path = self.src_path + path
        os.lseek(fh, offset, 0)
        return os.read(fh, size)
        
    def readdir(self, path, fh):
        base_path = self.src_path + os.sep + path + os.sep
        print base_path
        entries = os.listdir(base_path)
        
        files = [f for f in entries if os.path.isfile(base_path + f) if not f.lower().endswith(".jpg")]
        dirs = [f for f in entries if os.path.isdir(base_path + f)]
        symlinks = [f for f in entries if os.path.islink(base_path + f) if not f.lower().endswith(".jpg")]
        
        return ['.', '..'] + dirs + files + symlinks
    
    def which_case(self, path):
        base_path = self.src_path + path
        if os.path.islink(base_path) and path.lower().endswith(".mp3"):
            if os.path.exists(base_path): 
                return "MP3_EXISTING"
            else:
                return "MP3_MISSING"
        else:
            return "PASSTHROUGH"
    
    def getattr_mp3_existing(self, path, fh=None):
        base_path = self.src_path + path
        st = os.lstat(base_path)
        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode']& ~stat.S_IFLNK) | stat.S_IFREG
        out['st_size'] = 11562821
        return out
    
    def getattr_mp3_missing(self, path, fh=None):
        base_path = self.src_path + path
        st = os.lstat(base_path)
        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode']& ~stat.S_IFLNK) | stat.S_IFREG
        out['st_size'] = 14414296
        return out
    
    def getattr_passthrough(self, path, fh=None):
        base_path = self.src_path + path
        st = os.lstat(base_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    
    def getattr(self, path, fh=None):
        handlers = {
                "MP3_EXISTING": self.getattr_mp3_existing,
                "MP3_MISSING": self.getattr_mp3_missing,
                "PASSTHROUGH": self.getattr_passthrough
            }
        return handlers[self.which_case(path)](path, fh)
            
    def readlink(self, path):
        base_path = self.src_path + path
        return os.readlink(base_path)


if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <source dir> <mountpoint>' % argv[0])
        exit(1)

    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(AnnexFS(argv[1]), argv[2], foreground=True, encoding="utf-8", volname="MusicFS", debug=True)