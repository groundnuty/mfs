import logging
from fuse import FUSE
from mfs.mfuse import MFS
import sys

__author__ = 'orzech'

import mfs.common

if __name__ == '__main__':
    logging.basicConfig(filename="pyfs.log", filemode="w")
    logging.getLogger().setLevel(logging.DEBUG)

    FUSE(MFS(mfs.common.loadfiles(sys.argv[1]+"/.mfs/config.yaml"),sys.argv[1]), sys.argv[2],foreground=True)
