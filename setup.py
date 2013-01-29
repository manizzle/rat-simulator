from distutils.core import setup
import os, glob, py2exe, sys

setup(
 windows = ['main.py'],
 zipfile = None,
 options = {
  'py2exe': {
        'optimize': 2,
        'excludes' : [ 'Tkinter' ],
        'dist_dir' : 'RatSimulator/',
        'compressed' : True},
        },
 data_files = [('media', glob.glob('media/*.*')), ('RATASM',glob.glob('RATASM/*.*'))]
 )