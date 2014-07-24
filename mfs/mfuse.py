__author__ = 'groundnuty'


from fuse import Operations

import stat
import logging
import os

from .common import (
    logcall
)

class MFS(Operations):

    def __init__(self, config, src_path):
        super(MFS, self).__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.src_path = src_path

    def _which_case(self, path):
        base_path = self.src_path + path
        if os.path.islink(base_path) and path.lower().endswith(".mp3"):
            if os.path.exists(base_path):
                return "MP3_EXISTING"
            else:
                return "MP3_MISSING"
        else:
            return "PASSTHROUGH"

    def getattr(self, path, fh=None):
        handlers = {
                "MP3_EXISTING": self.getattr_mp3_existing,
                "MP3_MISSING": self.getattr_mp3_missing,
                "PASSTHROUGH": self.getattr_passthrough
            }
        return handlers[self._which_case(path)](path, fh)

    def open(self, path, flags):
        handlers = {
                "MP3_EXISTING": self.open_mp3_existing,
                "MP3_MISSING":  self.open_mp3_missing,
                "PASSTHROUGH":  self.open_passthrough
            }
        return handlers[self._which_case(path)](path, flags)

    def release(self, path, fh):
        return os.close(fh)

    def getattr_mp3_existing(self, path, fh=None):
        base_path = self.src_path+os.path.sep + os.readlink(self.src_path+path)
        st = os.lstat(base_path)
        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode'] & ~stat.S_IFLNK) | stat.S_IFREG
        return out

    def getattr_mp3_missing(self, path, fh=None):
        base_path = self.src_path+os.path.sep + os.readlink(self.src_path+path).replace("objects","meta")[0:-3]+"meta"
        st = os.lstat(base_path)
        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode'] & ~stat.S_IFLNK) | stat.S_IFREG
        out['st_size'] = out['st_size'] + getattr(os.lstat(self.src_path+os.path.sep+self.config['filler']),'st_size')
        return out

    def getattr_passthrough(self, path, fh=None):
        base_path = self.src_path + path
        st = os.lstat(base_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def open_mp3_existing(self, path, flags):
        base_path = self.src_path + path
        print base_path
        return os.open(base_path, flags)

    def open_mp3_missing(self, path, flags):
        base_path = self.src_path+os.path.sep + os.readlink(self.src_path+path).replace("objects","meta")[0:-3]+"meta"
        print base_path
        return os.open(base_path, flags)

    def open_passthrough(self, path, flags):
        base_path = self.src_path + path
        print "open"+base_path
        return os.open(base_path, flags)

    def readdir(self, path, fh):
        base_path = self.src_path + os.sep + path + os.sep
        entries = os.listdir(base_path)
        entries.remove(".mfs")
        print entries
        return ['.', '..'] + entries

    @logcall
    def read(self, path, size, offset, fh):
        base_path = self.src_path + path
        if os.path.exists(base_path):
            #The case of existing files
            os.lseek(fh, offset, 0)
            return os.read(fh, size)
        else:
            #The case of broken symlinks
            #First attempt to read only as much as needed
            filler_path = self.src_path+os.path.sep+self.config['filler']
            filler_size = getattr(os.lstat(filler_path),'st_size')
            meta_size = getattr(os.lstat(self.src_path+os.path.sep + os.readlink(self.src_path+path).replace("objects","meta")[0:-3]+"meta"),'st_size')

            readdata=""
            meta_size -= offset
            #If the offset is smaller then size of the meta then we need to read some meta
            if meta_size > 0:
                os.lseek(fh,offset,0)
                #If the size of what we want to read is smaller then remaining meta we need only to read meta
                if size-meta_size <= 0:
                    readdata += os.read(fh,size)
                    #Set remaining size to read to 0
                    size=0
                else:
                    #Otherwise we read what we have to and substract that from size
                    readdata += os.read(fh,meta_size)
                    size-=meta_size
            else:
                #Offset was is larger, no need to read meta, but substract remaining offset of filler size
                filler_size += meta_size

            #Move the offset to the begining of filler
            offset-=meta_size

            #If we still have something to read
            if size>0:
                fillerh = open(filler_path)
                #If the offset is still non 0 then move
                if offset>0:
                    fillerh.seek(offset)
                #Read remaining size, assuming its >= then total filler_size-offset
                readdata+=fillerh.read(size)
                fillerh.close()

            return readdata

    # Disable unused operations:
    # Not sure if we need to disable them
    access = None
    flush = None
    getxattr = None
    listxattr = None
    opendir = None
    releasedir = None
    statfs = None





