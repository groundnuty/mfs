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
        base_path = self.file_path(path)
        if os.path.islink(base_path) and path.lower().endswith(".mp3"):
            if os.path.exists(base_path):
                return "MP3_EXISTING"
            else:
                return "MP3_MISSING"
        else:
            return "PASSTHROUGH"

    def meta_path(self, path):
        return os.path.normpath(self.src_path+os.path.sep + path + os.path.sep + ".." + os.path.sep + os.readlink(self.src_path+path).replace(".git/annex/objects",".mfs/meta"))

    def meta_size(self, path):
        return os.path.getsize(self.meta_path(path))

    def file_path(self, path):
        return os.path.normpath(self.src_path + os.path.sep + path)

    def filler_path(self):
        return os.path.normpath(self.src_path+os.path.sep+self.config['filler'])
        
    def filler_size(self):
        return os.path.getsize(self.filler_path())

    def getattr(self, path, fh=None):
        handlers = {
                "MP3_EXISTING": self.getattr_delinkify,
                "MP3_MISSING":  self.getattr_mp3_missing,
                "PASSTHROUGH":  self.getattr_passthrough
            }
        return handlers[self._which_case(path)](path, fh)


    def open(self, path, flags):
        handlers = {
                "MP3_EXISTING": self.open_mp3_existing,
                "MP3_MISSING":   self.open_mp3_missing,
                "PASSTHROUGH":   self.open_passthrough
            }
        return handlers[self._which_case(path)](path, flags)

    def release(self, path, fh):
        return os.close(fh)

    def getattr_delinkify(self, path, fh=None):
        base_path = self.src_path+os.path.sep + path
        st = os.stat(base_path)
        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode'] & ~stat.S_IFLNK) | stat.S_IFREG
        return out

    def getattr_mp3_missing(self, path, fh=None):
        base_path = self.file_path(path)
        meta_path = self.meta_path(path)

        st = os.lstat(base_path)

        out = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        out['st_mode'] = (out['st_mode'] & ~stat.S_IFLNK) | stat.S_IFREG
        out['st_size'] = self.meta_size(path) + self.filler_size()
        return out

    def getattr_passthrough(self, path, fh=None):
        base_path = self.src_path + path
        st = os.lstat(base_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))



    def open_mp3_existing(self, path, flags):
        base_path = self.file_path(path)
        return os.open(base_path, flags)

    def open_mp3_missing(self, path, flags):
        base_path = self.meta_path(path)
        return os.open(base_path, flags)

    def open_passthrough(self, path, flags):
        base_path = self.file_path(path)
        return os.open(base_path, flags)

    def readdir(self, path, fh):
        base_path = self.file_path(path)
        entries = os.listdir(base_path)
        try:
            entries.remove(".mfs")
        except ValueError:
            pass
        return ['.', '..'] + entries

    def readlink(self, path):
        base_path = self.file_path(path)
        return os.readlink(base_path)
        

    @logcall
    def read(self, path, size, offset, fh):
        handlers = {
                "MP3_EXISTING": self.read_passthrough,
                "MP3_MISSING":  self.read_mp3_missing,
                "PASSTHROUGH":  self.read_passthrough
            }
        return handlers[self._which_case(path)](path, size, offset, fh)
    
    def read_passthrough(self, path, size, offset, fh):
        base_path = self.file_path(path)
        #The case of existing files
        os.lseek(fh, offset, 0)
        return os.read(fh, size)
    
    
    def read_mp3_missing(self, path, size, offset, fh):
        _size = size
        _offset = offset
        base_path = self.file_path(path)
        #The case of broken symlinks
        #First attempt to read only as much as needed
        filler_path = self.filler_path()
        filler_size = self.filler_size()
        # print filler_size
        meta_size  = self.meta_size(path)

        readdata=""
        
        # meta_size -= offset
        #If the offset is smaller then size of the meta then we need to read some meta
        if offset < meta_size:
            os.lseek(fh,offset,0)
            #If the size of what we want to read is smaller then remaining meta we need only to read meta
            br = os.read(fh,min(size-offset, meta_size-offset))
            readdata += br
            #Set remaining size to read to 0
            # print "br: ", len(br), " req ",min(size-offset, meta_size-offset),
            if len(br) != min(size-offset, meta_size-offset):
                print "This is fatal error"
            size-=len(br)

        #Move the offset to the begining of filler
        offset-=meta_size

        #If we still have something to read
        if size>0:
            fillerh = open(filler_path)
            #If the offset is still non 0 then move
            if offset>0:
                fillerh.seek(offset)
            #Read remaining size, assuming its >= then total filler_size-offset
            while size > 0:
                br = fillerh.read(size)
                readdata+= br
                size -= len(br)
                # print "2 br: ", len(br), " req ", size
                if len(br) == 0:
                    break
            fillerh.close()
        # print len(readdata), " expected ", size
        print path  , _size, _offset, len(readdata)
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





