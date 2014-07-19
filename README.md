mfs (music,meta,media file system)
===

Target Version: 0.1 

Currently supported features:

- readonly access to fuse files
- static database based on yaml file attached binary data
- the total size of the media file is computed dynamically when yaml file is loaded to make testing easier
- media files supplied via fuse are full fledged mp3 files that can be open by vlc and itunes. 

To run it:

 ```
 mkdir dest
 python main.py dest
 ```


Dependencies:
- pyfuse
- fuse-python
- mutagen

Tested with python 2.7.5 only on osx 10.9.2 with "fuse for osx" 2.7.0