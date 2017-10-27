#!/usr/bin/env python

from struct import unpack

HEADING_LINE_LENGTH = 38

TYPES = [
    "attribute",
    "coordinate (RST)",
    "TMD data ID",
    "Parent object ID",
    "Matrix value",
    "TMD data",
    "Light source",
    "Camera",
    "Object control"
]

def rint32(file):
    return unpack('<i', file.read(4))[0]

def ruint32(file):
    return unpack('<I', file.read(4))[0]

def rint16(file):
    return unpack('<h', file.read(2))[0]

def ruint16(file):
    return unpack('<H', file.read(2))[0]

def rbyte(file):
    return file.read(1)

def rubyte(file):
    return unpack('<B', file.read(1))[0]

def rchar(file):
    return unpack('<c', file.read(1))[0]

def rchararr(file, size):
    return unpack('<s', file.read(size))[0]

def skipbytes(file, num):
    if num is 0:
        return
    file.read(num)

def print_type(type):
    print(TYPES[type] if type < len(TYPES) else "{0:4b}".format(type))

def printHeading(text):
    print("\n=== {0} {1}".format(text, '='*(HEADING_LINE_LENGTH - (len(text) + 1))))

def readPacket(tod):
    objectID = ruint16(tod)
    typeAndFlag = rubyte(tod)
    type = typeAndFlag & 0xF
    flag = typeAndFlag & 0xF0
    packetLength = rubyte(tod)
    #print("ID: {0}".format(objectID))
    print_type(type)
    #print("flag: {0:b}".format(flag))
    print("packet len: {0}".format(packetLength))
    print (packetLength)
    skipbytes(tod, (packetLength * 4) - 4)

def readFrame(tod):
    frameSize = ruint16(tod)
    numPackets = ruint16(tod)
    frameNumber = ruint32(tod)
    print("Frame {0}".format(frameNumber))
    print("Packet count: {0}".format(numPackets))
    print("Frame length: {0} words".format(frameSize))
    
    for i in range(0, numPackets):
        readPacket(tod)


def readTOD(tod):
    magic = rubyte(tod)
    if magic != 0x50:
        print("TOD file not found!")
        return False
    printHeading("TOD")
    version = rubyte(tod)
    resolution = ruint16(tod)
    numFrames = ruint32(tod)
    print("Version: {0}".format(version))
    print("Resolution: {0} ticks".format(resolution))
    print("Frame count: {0}".format(numFrames))

    for i in range(0, numFrames):
        readFrame(tod)

def readMOS(mos):
    magic = rint32(mos)
    if magic != 0x20534F4D:
        print("MOS file not found!")
        return False
    printHeading("MOS")
    numTODs = ruint32(mos)
    todOffset = ruint32(mos)
    todLength = ruint32(mos) if numTODs > 1 else 0
    print("Num TODs: {0}".format(numTODs))
    print("TOD offset: 0x{0:X}".format(todOffset))
    print("TOD length: {0} bytes".format("N/A" if todLength is 0 else todLength))
    return readTOD(mos)

def readMOM(mom):
    magic = rint32(mom)
    if magic != 0x204D4F4D:
        print("MOM file not found!")
        return False
    printHeading("MOM")
    momLength = ruint32(mom)
    tmdOffset = ruint32(mom)
    print("Mom length: {0} bytes".format(momLength))
    print("TMD offset: 0x{0:X}".format(tmdOffset))
    return readMOS(mom)

def readLMM(lmm):
    magic = rint32(lmm)
    if magic != 0x204C4D4D:
        print("MML file not found!")
        return False
    printHeading("LMM")
    momCount = ruint32(lmm)
    momOffset = ruint32(lmm)
    print ("Number of MOMs: " + str(momCount))
    return readMOM(lmm)


def readLBD(filename):
    print("Reading LBD: " + filename)

    with open(filename, "rb") as lbd:
        magic = rint32(lbd)
        if magic != 0x10001:
            print(filename + " is not an LBD file")
            return False
        skipbytes(lbd, 12)
        offset = ruint16(lbd)
        printHeading("LBD")
        print("LMM offset: 0x{0:X}".format(offset))
        lbd.seek(offset, 0)
        return readLMM(lbd)


if __name__ == "__main__":
    readLBD("files/M013.LBD")