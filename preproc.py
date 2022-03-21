import sys
import os
import numpy as np
import nibabel
import matplotlib.pyplot as plt


class FileInfo:
    def __init__(self, tr, dim, pixdim, inputData):
        self.tr = tr
        self.dim = dim
        self.pixdim = pixdim
        self.inputData = inputData


def loadFile(_inputFileName):
    niftiFile = nibabel.load(_inputFileName)
    niftiFileHeader = niftiFile.header
    # Remove this
    # print("Headers are ", niftiFileHeader)
    fileInfo = FileInfo(
        niftiFileHeader["pixdim"][4],
        niftiFileHeader["dim"],
        niftiFileHeader["pixdim"],
        niftiFile,
    )
    return fileInfo


# Function to load the Slice Time Acquisition File and check if it is valid or not
# It Performs two checks
# 1. If the length of the values present inside is equal to the number of slices
# 2. If the value of time is within the range of TR
def loadSliceTimeAcquisitionFile(_fileInfo, _sliceTimeAcquisitionFileName):
    try:
        # Opens the given text file
        with open(_sliceTimeAcquisitionFileName) as files:
            # Reads all of the file in the .txt file
            timeAcquisition = files.readlines()
            # Finds the length of the input in the .txt file
            slicesInTimeAcquisitionFileLength = len(timeAcquisition)
            # _fileInfo.dim[3] is the number of slices
            # Checks if the number of lines in the file is equal to the number of slices
            # Remove the print
            # print(
            #     "Slice Acq File Length is ",
            #     slicesInTimeAcquisitionFileLength,
            #     " no of slices is : ",
            #     _fileInfo.dim[3],
            # )
            if slicesInTimeAcquisitionFileLength != _fileInfo.dim[3]:
                # If don't match will throw an exception
                raise Exception("SLICE TIME CORRECTION FAILURE")

            # Assuming the file contains time for all the slices, find if the time for each slice is within TR
            # checkIfAcqSliceFileCorrectTime(_fileInfo,timeAcquisition)
            for sliceTime in timeAcquisition:
                # Iterates through each of the time value and checks if lies within the range of TR
                # Remove This
                # print("Slice Time is ", float(sliceTime), "||", "TR is ", _fileInfo.tr)
                if float(sliceTime) < 0.0 or float(sliceTime) > _fileInfo.tr:
                    # If any of the sliceTime is not within the range of 0.0 to TR then it will throw an exception
                    raise Exception("SLICE TIME CORRECTION FAILURE")
    except Exception as e:
        # Write code to output the error in a txt file
        print(e)
    else:
        # Returns True if no exception is found
        return timeAcquisition
    finally:
        files.close()


def interpolate(_slice1, _slice2, _targetTime, _slice1Time, _slice2Time):
    # Remove print later
    # print(
    #     "Target Time is ",
    #     _targetTime,
    #     "Slice 1 time is ",
    #     _slice1Time,
    #     "Slice 2 time is ",
    #     _slice2Time,
    # )
    # Since slope is y2-y1/x2-1
    slope = (_slice2 - _slice1) / (_slice2Time - _slice1Time)
    # Interpolating the slice at target position using formula for linear 2D interpolation
    interpolatedSlice = _slice1 + (slope * (_targetTime - _slice1Time))
    return interpolatedSlice


# This function will perform sliceTimeCorrection using LInear Interpolation
# This will iterate over each of the slices in each of the volumes and will linear interpolate to the target time
# To avoid complexity I have taken the starting and ending volumes as constant
def sliceTimeCorrection(_fileInfo, _timeAcquisition, _targetTime):
    fmriData = _fileInfo.inputData
    # Stores the correctedData
    # correctedData = np.array(
    #     (fmriData.shape[0], fmriData.shape[1], fmriData.shape[2], fmriData.shape[3] - 1)
    # )
    # print(correctedData.shape)
    # Sample viewing of each slice remove this
    # print("Showing sample slice")
    # plt.imshow(fmriData.get_fdata()[:, :, 10, 1])
    # Looping through each of the volumes of the data (excluding the 1st and the last volume)
    for volumeNo in range(1, fmriData.shape[3] - 1):
        # Looping through each slice in the volume
        for sliceNo in range(0, fmriData.shape[2]):
            slice = fmriData.get_fdata()[:, :, sliceNo, volumeNo]
            # Fetching the corresponding slice time from the acquisition file for the slice
            sliceTime = float(_timeAcquisition[sliceNo])
            # If the time of acquisition of the particular slice is same to that of the target time then we leave it untouched
            if sliceTime == _targetTime:
                correctedSlice = slice
            # Idea is to keep the target in between two points therefore if the time of current slice is less than the targetTime so select
            # the same corresponding position slice in the next volume and if current slice is greater then choose the same corresponding position
            # slice in the previous volume, to easliy interpolate for any given targetTime
            elif sliceTime < _targetTime:
                # In this cas will interpolate between the slice in current iteration and the same position slice in the next volume
                timeCorrectedSlice = interpolate(
                    slice,
                    fmriData.get_fdata()[
                        :, :, sliceNo, volumeNo + 1
                    ],  # same slice in next volume
                    _targetTime,
                    sliceTime,
                    sliceTime
                    + _fileInfo.tr,  # Since the second slice is in next volume so seperated by TR
                )
            elif sliceTime > _targetTime:
                # In this cas will interpolate between the slice in current iteration and the same position slice in the previous volume
                timeCorrectedSlice = interpolate(
                    slice,
                    fmriData.get_fdata()[
                        :, :, sliceNo, volumeNo - 1
                    ],  # same slice in previous volume
                    _targetTime,
                    sliceTime,
                    sliceTime
                    - _fileInfo.tr,  # Since the second slice is in previous volume so seperated by TR
                )
        # correctedData[:, :, sliceNo, volumeNo] = timeCorrectedSlice
        print(timeCorrectedSlice)
    # return correctedData


def main(_inputFileName, _sliceTimeAcquisitionFileName, _targetTime):
    fileInfo = loadFile(_inputFileName)
    timeAcquisition = loadSliceTimeAcquisitionFile(
        fileInfo, _sliceTimeAcquisitionFileName
    )
    if timeAcquisition:
        # If the Acquisition file is good, run linear interpolation
        correctedData = sliceTimeCorrection(fileInfo, timeAcquisition, _targetTime)
        # print(correctedData.shape)


if __name__ == "__main__":
    # As defined in the Assignment question it's assumed that the function call will be made with the following flag in the same order as defined in usage.
    # Usage : python preproc.py -i <input> -o <output> [-tc t <slice time acquisition file> ] [ -tf high low ] [ -sm fwhm ]
    print(sys.argv)
    inputFileName = sys.argv[2]
    sliceTimeAcquisitionFileName = sys.argv[7]
    targetTime = float(sys.argv[6])
    # outputFileName = sys.argv[4]
    main(inputFileName, sliceTimeAcquisitionFileName, targetTime)
