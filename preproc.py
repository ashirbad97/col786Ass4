import sys
import os
from typing import final
import nibabel

class FileInfo:
    def __init__(self, tr, dim, pixdim):
        self.tr  = tr
        self.dim = dim
        self.pixdim = pixdim

def loadFile(_inputFileName):
    niftiFile = nibabel.load(_inputFileName)
    niftiFileHeader = niftiFile.header
    fileInfo = FileInfo(niftiFileHeader["pixdim"][4],niftiFileHeader["dim"],niftiFileHeader["pixdim"])
    return fileInfo

# Function to load the Slice Time Acquisition File and check if it is valid or not
# It Performs two checks
# 1. If the length of the values present inside is equal to the number of slices
# 2. If the value of time is within the range of TR
def loadSliceTimeAcquisitionFile(_fileInfo,_sliceTimeAcquisitionFileName):
    try:
        # Opens the given text file
        with open(_sliceTimeAcquisitionFileName) as files:
            # Reads all of the file in the .txt file
            timeAcquisition = files.readlines()
            # Finds the length of the input in the .txt file
            slicesInTimeAcquisitionFileLength = len(timeAcquisition)
            # _fileInfo.dim[3] is the number of slices
            # Checks if the number of lines in the file is equal to the number of slices
            if (slicesInTimeAcquisitionFileLength != _fileInfo.dim[3]):
                # If don't match will throw an exception
                raise Exception("SLICE TIME CORRECTION FAILURE")

            # Assuming the file contains time for all the slices, find if the time for each slice is within TR
            # checkIfAcqSliceFileCorrectTime(_fileInfo,timeAcquisition)
            for sliceTime in timeAcquisition :
                # Iterates through each of the time value and checks if lies within the range of TR
                if (float(sliceTime) < 0.0 or float(sliceTime) > _fileInfo.dim[3]):
                    # If any of the sliceTime is not within the range of 0.0 to TR then it will throw an exception
                    raise Exception("SLICE TIME CORRECTION FAILURE")
    except Exception as e:
        # Write code to output the error in a txt file
        print(e)
    else:
        # Returns True if no exception is found
        return True
    finally:
        files.close()

def main(_inputFileName,_sliceTimeAcquisitionFileName):
    fileInfo = loadFile(_inputFileName)
    isAcqFileGood = loadSliceTimeAcquisitionFile(fileInfo,_sliceTimeAcquisitionFileName)
    # CHANGE THIS !!!!!!!!!!!!!!!. Forcing the isAcqFileGood value to be true
    if(isAcqFileGood):
        # If the Acquisition file is good, run linear interpolation
        sliceTimeCorrection()

if __name__ == "__main__":
    # As defined in the Assignment question it's assumed that the function call will be made with the following flag in the same order as defined in usage.
    # Usage : python preproc.py -i <input> -o <output> [-tc t <slice time acquisition file> ] [ -tf high low ] [ -sm fwhm ]
    print(sys.argv)
    inputFileName = sys.argv[2]
    sliceTimeAcquisitionFileName = sys.argv[5]
    # outputFileName = sys.argv[4]
    main(inputFileName,sliceTimeAcquisitionFileName)