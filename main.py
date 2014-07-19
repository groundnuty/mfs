import logging
from fuse import FUSE
from mfs.mfuse import MFS
import sys

__author__ = 'orzech'

import mfs.common

if __name__ == '__main__':
    logging.basicConfig(filename="pyfs.log", filemode="w")
    logging.getLogger().setLevel(logging.DEBUG)

    FUSE(MFS(mfs.common.loadfiles("data/files.yaml")), sys.argv[1],foreground=True)
