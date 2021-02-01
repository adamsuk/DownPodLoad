#!/usr/bin/env python

"""
v0.1 - initial write of find_file script

This is the module to find the text file in a given base directory
"""

# imports and dependencies
import os
import fnmatch

def find_file(treeroot, filename='my_pods.txt'):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, filename)
        results.extend(base for f in goodfiles)
    return results

if __name__ == '__main__':
    root_dir = os.getcwd()
    trial_file = 'my_pods_trial.txt'
    dirs = find_file(root_dir, trial_file)
    print(dirs)

