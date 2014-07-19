__author__ = 'groundnuty'

import os
import logging
log = logging.getLogger(__name__)
import traceback

def loadfiles(filename):
    import yaml
    head, tail = os.path.split(filename)
    fh = open(filename)

    files = dict()
    #dict with filenames as keys is easier to use later
    for f in yaml.safe_load(fh)['files']:

        #the total file length is computer dynamically
        #as I wanted to keep yaml simple for now
        f['id3'] = os.path.join(head,f['id3'])
        f['filler'] = os.path.join(head,f['filler'])
        f['len'] = os.path.getsize(f['id3']) + \
                   os.path.getsize(f['filler'])

        files[f['filename']] = f
    fh.close()
    return files

def logcall(f):
    log = logging.getLogger(f.__name__)

    def getattrs(o):
        collected = []
        for name in dir(o):
            if name.startswith("logme_"):
                collected.append("{}={}".format(name[6:], getattr(o, name)))
        return "{}({})".format(o.__class__.__name__, ", ".join(collected))

    def logged(*args, **kw):
        log.debug("Calling {}(*{}, **{}) on {}".format(
            f.__name__, args, kw, None if not args else getattrs(args[0])))
        try:
            ret = f(*args, **kw)
        except Exception:
            log.debug(
                "Called: {}(*{}, **{}) on {} and got exception {}".format(
                    f.__name__,
                    args,
                    kw,
                    None if not args else getattrs(args[0]),
                    traceback.format_exc(),
                )
            )
            raise
        log.debug("Called: {}(*{}, **{}) on {} -> {}".format(
            f.__name__, args, kw, None if not args else getattrs(args[0]), ret
        ))
        return ret
    return logged

def read_from_string(text, size, offset):
        slen = len(text)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = text[offset:offset+size]
        else:
            buf = ''
        return buf
