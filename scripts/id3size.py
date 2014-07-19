__author__ = 'groundnuty'

from mutagen.mp3 import MP3
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="id3size.py")
    parser.add_argument(dest='filepath', type=str, default=1,
                        help="path to file with id3 tag")

    args = parser.parse_args()

    f = MP3(args.filepath)
    print f.tags.size