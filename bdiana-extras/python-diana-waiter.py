#!/usr/bin/env python

"""Usage: bdiana-waiter.py <input directory> <period> <setup file>

Monitors the given input directory for new input files, waiting for the
specified period (in seconds) before checking again. When new input files
are found, runs the specified bdiana executable and setup file for each of
the files. The input files are deleted after being processed.
"""

import commands, datetime, glob, os, sys, time
from metno import bdiana

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.stderr.write(__doc__)
        sys.exit(1)

    input_dir, period, setup_file = sys.argv[1:]

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

    b = bdiana.BDiana()
    if not b.setup(setup_file):
        sys.stderr.write("Failed to parse the setup file '%s'.\n" % setup_file)
        sys.exit(1)

    while True:

        files = glob.glob(os.path.join(input_dir, "*.input"))
        if files:
            print "%s: Found %i files." % (now(), len(files))

        for file_name in files:

            input_file = bdiana.InputFile(file_name)
            b.prepare(input_file)
            times = b.getPlotTimes()
            if times:
                b.setPlotTime(times[-1])
            else:
                b.setPlotTime(datetime.datetime.now())

            width, height = input_file.getBufferSize()
            if "filename" in input_file.parameters:
                output_path = input_file.parameters["filename"]
            elif "FILENAME" in input_file.parameters:
                output_path = input_file.parameters["FILENAME"]
            else:
                sys.stderr.write("%s: Discarded input file '%s' without an output file name.\n" % (now(), file_name))
                os.remove(file_name)
                continue

            if output_path.endswith(".pdf"):
                b.plotPDF(width, height, output_path)
            elif output_path.endswith(".svg"):
                b.plotSVG(width, height, output_path)
            else:
                image = b.plotImage(width, height)
                image.save(output_path)
    
            print "%s: Processed input file '%s'." % (now(), file_name)

            os.remove(file_name)

        time.sleep(period)

    sys.exit()
