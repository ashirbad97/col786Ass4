import sys
import os
import nibabel


# As defined in the Assignment question it's assumed that the function call will be made with the following flag in the same order as defined in usage.
# Usage : python preproc.py -i <input> -o <output> [-tc t <slice time acquisition file> ] [ -tf high low ] [ -sm fwhm ]

inputFileName = sys.argv[2]
# outputFileName = sys.argv[4]

# Remove these later
print("Input file name is ", inputFileName)
# print("Output file name is ", outputFileName)


def loadFile(inputFileName):
    niftiFile = nibabel.load(inputFileName)
    niftiFileHeader = niftiFile.header
    print(niftiFileHeader)


loadFile(inputFileName)
