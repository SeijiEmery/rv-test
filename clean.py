#!/usr/bin/env python3
''' cleans all the generated files '''
import os

def clean_directories (*args):
    import shutil
    for path in args:
        if os.path.isdir(path):
            shutil.rmtree(path)

def clean_generated_files ():
    clean_directories('generated', 'results')

if __name__ == '__main__':
   clean_generated_files()
