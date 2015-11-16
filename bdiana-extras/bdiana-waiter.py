#!/usr/bin/env python

"""Usage: bdiana-waiter.py <input directory> <period> <bdiana> <setup file>

Monitors the given input directory for new input files, waiting for the
specified period (in seconds) before checking again. When new input files
are found, runs the specified bdiana executable and setup file for each of
the files.
"""

import commands, glob, os, sys, time

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

if __name__ == "__main__":

    if len(sys.argv) != 5:
        sys.stderr.write(__doc__)
        sys.exit(1)

    input_dir, period, bdiana, setup_file = sys.argv[1:]

    if not os.path.exists(input_dir):
        try:
            os.mkdir(input_dir)
        except OSError:
            sys.stderr.write("Failed to create input directory '%s'.\n" % input_dir)
            sys.exit(1)
        print "%s: Created input directory '%s'." % (now(), input_dir)

    try:
        period = int(period)
    except ValueError:
        sys.stderr.write("Please specify an integer period of time in seconds.\n")
        sys.exit(1)

    while True:

        files = glob.glob(os.path.join(input_dir, "*.input"))
        if files:
            print "%s: Found %i files." % (now(), len(files))

        for file_name in files:

            result = os.system(" ".join([commands.mkarg(bdiana), "-s",
                commands.mkarg(setup_file), "-i", commands.mkarg(file_name)]))
            
            if result != 0:
                sys.stderr.write("%s: Failed to process '%s'.\n" % (now(), file_name))
            else:
                print "%s: Processed input file '%s'." % (now(), file_name)

            os.remove(file_name)

        time.sleep(period)

    sys.exit()
