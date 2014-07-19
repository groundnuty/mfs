__author__ = 'groundnuty'


from fuse import FuseOSError, Operations

import errno
import stat
import logging
import time

from .common import (
    logcall,
    read_from_string
)


class MFS(Operations):

    # Expect a flat key value list where keys are file paths
    def __init__(self,files):
        super(MFS, self).__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self.files = files

    @logcall
    def getattr(self, path, fh=None):

        if path == '/':
            #The root folder
            st = dict(
                st_mode=(stat.S_IFDIR | 0755),
                st_nlink=2,
            )
        elif path[1:] in self.files.keys():
            #Files
            st = dict(
                st_mode=(stat.S_IFREG | 0644),
                st_nlink=1,
                st_size=self.files[path[1:]]['len']
            )
        else:
            raise FuseOSError(errno.ENOENT)

        #Current time is as good as any for now
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time.time()
        return st

    @logcall
    def readdir(self, path, fh):
        return [".", ".."] + self.files.keys()

    @logcall
    def read(self, path, size, offset, fh):
        return read_from_string(
            self._getfile(path),
            size,
            offset
        )

    def _getfile(self,path):
        #For the moment simplest the least efficient way possible
        return open(self.files[path[1:]]['id3']).read() + open(self.files[path[1:]]['filler']).read()

    # Disable unused operations:
    # Not sure if we need to disable them
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None





