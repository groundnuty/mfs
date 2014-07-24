mfs (music,meta,media file system)
===

Version: 0.2

- mirroring a source catalog
- replacing broken symlinks with generated mp3 files 


Version: 0.1 

- readonly access to fuse files
- static database based on yaml file attached binary data
- the total size of the media file is computed dynamically when yaml file is loaded to make testing easier
- media files supplied via fuse are full fledged mp3 files that can be open by vlc and itunes. 

To run it:

 ```
 mkdir /tmp/dest
 python main.py data /tmp/pdest
 ```

Dependencies:
- pyfuse
- fuse-python
- mutagen

Tested with python 2.7.5 only on osx 10.9.2 with "fuse for osx" 2.7.0


Icon by iconcubic (http://iconcubic.deviantart.com)