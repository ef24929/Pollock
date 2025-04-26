import re
import math
import argparse
import pathlib
from PIL import Image, ImageDraw

#
# Pollock image format definition
# First pixel of the first cell: [major version, minor version, cellsize]
# First pixel of the second cell: [tnol % 16777216, tnol % 65536, tnol % 256], where tnol = total number of lines - 2
# We do not need to count the first two elements, since they are the metainfo
#
# If the number of lines is 0 or 1, we have a vertical image, due to flooring sqrt!
# After acquiring the metadata, any pixel is good from the cell to get the 3 channel instructions (v1.0)
#
# Pollock assembly allows the usage of labels of 7 chars of capital letters and digits for jumps.
#

V_MAJOR = 1
V_MINOR = 0

e_line = re.compile(r"^\s*$")
c_line = re.compile(r"^\s*#.*$")
push_op = re.compile(r"^push[A-Z0-9]{0,7}(_[1234])?$")

proglist = []
progline = 1
rowline = 0
labels: dict[str, int] = {}

def mesg (instring: str):
    if args.silent is False:
        print(instring)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-d', '--dryrun', action='store_true', default=False, help='no output generated')
    parser.add_argument('-b', '--bytearray', action='store_true', default=False, help='no binary output, just the text bytearray')
    parser.add_argument('-s', '--silent', action='store_true', default=False, help='silent run, no warnings or errors')
    parser.add_argument('-c', '--cellsize', default=10, help='picture cellsize, default value is 10 pixels, valid interval is [2,50]')
    parser.add_argument('-o', '--output', help='name of the binary output file, if not provided, it will be indentical with the source file name')
    args = parser.parse_args()

    path = pathlib.Path(args.filename)

    if int(args.cellsize) < 2 or int(args.cellsize) > 50:
        mesg(f"Invalid cellsize {args.cellsize}. Cell size must be between 2 and 50 pixels.")
        exit(1)

    proglist.append([int(V_MAJOR), int(V_MINOR), int(args.cellsize)])
    proglist.append([0, 0, 0])

    if path.exists() and path.is_file():
        with open(path) as ifile:
            for line in ifile:
                if e_line.match(line):
                    progline += 1
                elif c_line.match(line):
                    progline += 1
                else:
                    editline = re.sub(r"\s*", "", line)
                    editline = re.sub(r";?(#.*)?$", "", editline)
                    if ':' in editline:
                        splitline = re.split(r":", editline)
                        labels[splitline[0]]=rowline
                    else:
                        splitline = ["", editline[:]]
                    opsline = re.split(r";", splitline[1])
                    #print(f"{editline=}\n{splitline=}\n{opsline=}")
                    #print(f"{labels=}")
                    rgbcol = [188, 188, 188]
                    rgbpoint = 0
                    for op in opsline:
                        if push_op.match(op):
                            push_val = op.replace("push", "")
                            if '_' in push_val:
                                pushslice = re.split(r"_", push_val)
                            else:
                                pushslice = [push_val]
                            if pushslice[0].isdecimal() is True:
                                if int(pushslice[0])>127 or int(pushslice[0])<0:
                                    mesg(f"Syntax error in {progline}. Push argument is out of range, using 0.")
                                    pixval = 0
                                else:
                                    pixval = int(pushslice[0])
                            elif pushslice[0].isalnum() is True:
                                if labels.get(pushslice[0]) is not None:
                                    if len(pushslice)==2:
                                        if 1 <= int(pushslice[1]) <= 4:
                                            match int(pushslice[1]):
                                                case 1:
                                                    pixval = int(labels.get(pushslice[0])) % 128
                                                case 2:
                                                    pixval = (int(labels.get(pushslice[0])) >> 7) % 128
                                                case 3:
                                                    pixval = (int(labels.get(pushslice[0])) >> 14) % 128
                                                case 4:
                                                    pixval = (int(labels.get(pushslice[0])) >> 21) % 128
                                        else:
                                            mesg(f"Invalid label slice '{pushslice[0]}_{pushslice[1]}' in {progline}.")
                                            exit(1)
                                    else:
                                        pixval = int(labels.get(pushslice[0]))
                                else:
                                    mesg(f"Invalid label '{pushslice[0]}' in {progline}.")
                                    exit(1)
                            else:
                                mesg(f"Syntax error in {progline}. Invalid push argument, using 0.")
                                pixval = 0
                            rgbcol[rgbpoint] = pixval
                            rgbpoint += 1
                            continue
                        match op:
                            case("add"):
                                pixval = int(0b1000_0000)
                            case("sub"):
                                pixval = int(0b1000_0100)
                            case("mul"):
                                pixval = int(0b1000_1000)
                            case("div"):
                                pixval = int(0b1000_1100)
                            case("rem"):
                                pixval = int(0b1001_0000)
                            case("pop"):
                                pixval = int(0b1001_0100)
                            case("swap"):
                                pixval = int(0b1001_1000)
                            case("dup"):
                                pixval = int(0b1001_1100)
                            case("rot"):
                                pixval = int(0b1010_0000)
                            case("not"):
                                pixval = int(0b1010_0100)
                            case("or"):
                                pixval = int(0b1010_1000)
                            case("and"):
                                pixval = int(0b1010_1100)
                            case("gt"):
                                pixval = int(0b1011_0000)
                            case("eq"):
                                pixval = int(0b1011_0100)
                            case("lt"):
                                pixval = int(0b1011_1000)
                            case("nop"):
                                pixval = int(0b1011_1100)
                            case("halt"):
                                pixval = int(0b1100_0000)
                            case("jmpz"):
                                pixval = int(0b1100_0100)
                            case("jmpnz"):
                                pixval = int(0b1100_1000)
                            case("outc"):
                                pixval = int(0b1100_1100)
                            case("inc"):
                                pixval = int(0b1101_0000)
                            case("outi"):
                                pixval = int(0b1101_0100)
                            case("ini"):
                                pixval = int(0b1101_1000)
                            case("pusha"):
                                pixval = int(0b1101_1100)
                            case("waita"):
                                pixval = int(0b1110_0000)
                            case("neg"):
                                pixval = int(0b1110_0100)
                            case("shl"):
                                pixval = int(0b1110_1000)
                            case("shr"):
                                pixval = int(0b1110_1100)
                            case(""):
                                mesg(f"Syntax error in {progline}. Empty operation, turning it to nop.")
                                pixval = int(0b1011_1100)
                            case _:
                                mesg(f"Syntax error in {progline}. Invalid op: {op}, turning it to nop")
                                pixval = int(0b1011_1100)
                        rgbcol[rgbpoint] = pixval
                        rgbpoint+=1
                    if rgbpoint<3:
                        mesg(f"Syntax error in {progline}. Line length is too short, filling it up with nops.")
                    proglist.append(rgbcol)
                    progline += 1
                    rowline += 1
    else:
        mesg(f"Invalid file {path} to compile.")
        exit(1)
    if len(proglist) >= pow(2,24)-2:
        mesg(f"File length {path} too long to compile.")
        exit(1)
    proglist[1][2] = (len(proglist) - 2) % 256
    proglist[1][1] = ((len(proglist) - 2) >> 8) % 256
    proglist[1][0] = ((len(proglist) - 2) >> 16) % 256
    if args.dryrun is False:
        if args.bytearray is False:
            xsize = math.floor(math.sqrt(len(proglist)))
            xsize2 = xsize ** 2
            if xsize2 == len(proglist):
                ysize = xsize
            else:
                ysize = int(math.ceil(len(proglist) / xsize))
            #print(f"{len(proglist)=} {xsize=}, {ysize=}")
            polpic = Image.new("RGB", (xsize * args.cellsize, ysize * args.cellsize), (188, 188, 188))
            poldraw = ImageDraw.Draw(polpic)
            xcellstart = 0
            ycellstart = 0
            xcellstop = xcellstart + args.cellsize - 1
            ycellstop = ycellstart + args.cellsize - 1
            xline = 1
            for cell in proglist:
                poldraw.rectangle([(xcellstart, ycellstart), (xcellstop, ycellstop)], fill=tuple(cell))
                xcellstart += args.cellsize
                xcellstop = xcellstart + args.cellsize - 1
                xline += 1
                if xline > xsize:
                    xline = 1
                    xcellstart = 0
                    xcellstop = xcellstart + args.cellsize - 1
                    ycellstart += args.cellsize
                    ycellstop = ycellstart + args.cellsize - 1
            if args.output is None:
                savefile = path.stem + ".png"
            else:
                savefile = args.output + ".png"
            polpic.save(savefile)
        else:
            print(f"{proglist}")