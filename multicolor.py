#!/usr/bin/python3
#
# mulTIColor - convert images to TIC-80 multicolor mode
#
# Hint: python -m pip install pillow (install PIL on Windows)
#
# last updated by Decca / RiFT on 18.03.2021 23:45
#


# import modules
from PIL import Image
import subprocess
import argparse
import tempfile
import os.path
import sys


# replace argparse-error message with own, nicer help/usage
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("Usage: multicolor imagefile [OPTION...]\n"
              "Generate TIC-80 multicolor images\n"
              "\n"
              "mandatory arguments:\n"
              "  imagefile          imagefile with graphicsdata (e.g.: .png, .gif, etc.)\n"
              "\n"
              "optional arguments:\n"
              "  -c, --converter    converter: pil (default), see mtc.cfg for more\n"
              "  -o, --output       outputfile for multicolor values (.lua)\n"
              "  -f, --force        force overwrite of outputfile when it already exist\n"
              "  -m, --mode         mode to encode values: raw (default) or rle\n"
              "  -v, --version      show version info\n"
              "  -h, --help         show this help\n"
              "\n"
              "The optional arguments are only needed if the default setting does not meet the\n"
              "required needs. A specific name for the output file can be set (-o / --output).\n"
              "Mode (-m / --mode) to encode the pixel data via rle (run-length encoding) or as\n"
              "raw, which is the default. To reduce the colors of the image per line, various\n"
              "converters (-c / --converter) can be used. These can be configured in \"mtc.cfg\".\n"
              "Additional defined are: \"iview\" for IrfanView, \"magick\" for ImageMagick.\n"
              "\n"
              "examples:\n"
              "  multicolor imagefile.png \n"
              "  multicolor graphic.gif -o multicolor.lua\n"
              "  multicolor pixels.png -c iview -o mydata.lua\n"
              "  multicolor truecol.gif -m rle -o compress.lua\n"
              "  multicolor logo.png -o overwriteme.lua -f\n", file=sys.stderr)
        self.exit(1, '%s: ERROR: %s\n' % (self.prog, message))


# set commandline arguments
parser = ArgumentParser(prog='mulTIColor', add_help=False)
parser.add_argument('image',
                    metavar='imagefile',
                    type=str,
                    help='imagefile with pixels')
parser.add_argument('-c', '--converter',
                    metavar='converter',
                    const='pil',
                    default='pil',
                    type=str,
                    nargs='?',
                    action='store',
                    help='converter to reduce colors per line')
parser.add_argument('-o', '--output',
                    metavar='outputfile',
                    type=str,
                    action='store',
                    help='outputfile for multicolor data')
parser.add_argument('-f', '--force',
                    action='store_true',
                    help='force overwrite of outputfile')
parser.add_argument('-m', '--mode',
                    metavar='mode',
                    const='raw',
                    default='raw',
                    choices=('raw', 'rle'),
                    type=str,
                    nargs='?',
                    action='store',
                    help='encode data in other formats than raw')
parser.add_argument('-v', '--version',
                    action='version',
                    version='%(prog)s 0.9')
args = parser.parse_args()


# get commandline arguments
imageFile = args.image
outputConv = args.converter
outputFile = args.output
outputEnc = args.mode
outputForce = args.force


# set or init vars
configFile = "mtc.cfg"
convCommand = None


# load image file
print("       Image: " + imageFile)
try:
    orgImg = Image.open(imageFile)
except Exception as error:
    print("ERROR: " + str(error), file=sys.stderr)
    exit(1)


# get image mode & format
orgMode = orgImg.mode
orgFormat = orgImg.format
orgFormat = '.' + orgFormat.lower()
print("      Format: " + orgFormat + " (" + orgMode + ")")


# get image dimensions
orgSizeX, orgSizeY = orgImg.size
print("  Resolution: " + str(orgSizeX) + " x " + str(orgSizeY))


# get image colors & amount
orgColors = orgImg.convert('RGB').getcolors(maxcolors=(orgSizeX * orgSizeY))
print("      Colors: " + str(len(orgColors)))


# check image dimensions
if orgSizeX > 240:
    print("ERROR: image is wieder than 240 pixels")
    exit(1)
if orgSizeY > 136:
    print("ERROR: image is higher than 136 pixels")
    exit(1)


# create new image for pasting
newImg = Image.new(mode="RGB", size=(orgSizeX, orgSizeY))


# check and read config for external converter
if outputConv != 'pil':
    if not os.path.isfile(configFile):
        print("ERROR: no configuration file found (" + configFile + ")")
        exit(1)
    else:
        with open(configFile) as file:
            for line in file:
                if line.startswith(outputConv + " = "):
                    # print(line)  # DEBUG
                    name, command = line.split('=', 1)
                    convCommand = command.strip()
                    # print(convCommand)  # DEBUG
                else:
                    continue
        # check and parse converter command
        if not isinstance(convCommand, str):
            print("ERROR: converter \"" + outputConv + "\" is not defined")
            exit(1)
        else:
            # check and replace keywords
            if not all(x in convCommand for x in ["{IN}", "{OUT}"]):
                print("ERROR: {IN} and/or {OUT} are missing")
                exit(1)
            else:
                tmpDir = (tempfile.gettempdir())
                inFile = tmpDir + "\\mtc-infile" + orgFormat
                outFile = tmpDir + "\\mtc-outfile" + orgFormat
                convSubproc = convCommand.replace('{IN}', '"' + inFile + '"')
                convSubproc = convSubproc.replace('{OUT}', '"' + outFile + '"')
                # print(convSubproc)  # DEBUG
            # check converter binary
            convBinary = convCommand.split('"')[1].split('"')[0]
            # print(convBinary)  # DEBUG
            if not os.path.isfile(convBinary):
                print("ERROR: " + convBinary + " not found")
                exit(1)
                # print("---")  # DEBUG


# function when using an external converter
def ext_conv(convLine):
    # save line to reduce
    try:
        convLine.save(inFile)
    except Exception as error:
        print("ERROR: " + str(error), file=sys.stderr)
    # execute converter
    subprocess.run(convSubproc)
    # load reduced line
    try:
        doneLine = Image.open(outFile)
    except Exception as error:
        print("ERROR: " + str(error), file=sys.stderr)
    return doneLine


# convert image to 16 colors per line
print("   Converting with " + outputConv + "...")
offsetY = 0
toReduce = 0
alreadyOk = 0
while offsetY < orgSizeY:
    Line = orgImg.crop((0, offsetY, orgSizeX, offsetY+1))
    Colors = Line.convert('RGB').getcolors(maxcolors=(orgSizeX))
    if len(Colors) > 16:
        if outputConv == 'pil':
            newLine = Line.convert("P", palette=Image.ADAPTIVE, colors=16)
        else:
            extLine = ext_conv(Line)
            newLine = extLine.convert("P", palette=Image.ADAPTIVE, colors=16)
        newImg.paste(newLine, (0, offsetY))
        toReduce = toReduce + 1
    else:
        newImg.paste(Line, (0, offsetY))
        alreadyOk = alreadyOk + 1
    offsetY = offsetY + 1
print("  already ok: " + str(alreadyOk))
print("     reduced: " + str(toReduce))


# delete tempfiles if necessary
if outputConv != 'pil':
    if os.path.isfile(inFile):
        os.remove(inFile)
    if os.path.isfile(outFile):
        os.remove(outFile)


# get values from converted image
print("   Generating data...")
Pixels = ""
Palette = ""
offsetY = 0
offsetX = 0
while offsetY < orgSizeY:
    Line = newImg.crop((0, offsetY, orgSizeX, offsetY+1))
    rawLine = Line.convert("P", palette=Image.ADAPTIVE, colors=16)
    # pixel values in hex (0 to f)
    while offsetX < orgSizeX:
        palIndex = rawLine.getpixel((offsetX, 0))
        hexVal = '%0*x' % (1, palIndex)
        Pixels = Pixels + hexVal
        offsetX = offsetX + 1
    offsetY = offsetY + 1
    offsetX = 0
    # palette in hex (00 to ff)
    rawPalette = rawLine.getpalette()
    rgbEntries = 16 * 3
    rgbPalette = rawPalette[:rgbEntries]
    for entry in rgbPalette:
        hexVal = '%0*x' % (2, entry)
        Palette = Palette + hexVal


# compress pixel data (rle: only append number if value repeats more than twice)
if outputEnc == 'rle':
    enc = ""
    prev = ""
    count = 1
    for symbol in Pixels:
        value = chr(int(symbol, 16)+65)
        if value != prev:
            if prev:
                enc = enc + prev
                if count == 2:
                    enc = enc + prev
                elif count > 2:
                    enc = enc + str(count-1)
            count = 1
            prev = value
        else:
            count = count + 1
    enc = enc + prev
    if count == 2:
        enc = enc + prev
    elif count > 2:
        enc = enc + str(count-1)
    if not enc[-1].isdigit():
        enc = enc + "0"


# show final image when no outputfile
if not isinstance(outputFile, str):
    print("  try to show image...")
    newImg.show()
    print("  done.")
    exit()


# check if output file already exist
def check_file(outputName):
    if not outputForce:
        if os.path.isfile(outputName):
            print("ERROR: file already exist")
            exit(1)
    else:
        return


# include display component for the outputfile
displayFile = os.path.join(os.path.curdir, "components", "display.lua")
if os.path.isfile(displayFile):
    with open(displayFile, "r") as file:
        fileLines = [line.strip('\n') for line in file.readlines()]
        codeStart = next((index for index, tag in enumerate(fileLines) if tag == '-- CODEBLOCK'), -1)
        compDisplay = "\n".join(fileLines[codeStart+1:]) + "\n"
else:
    compDisplay = "\n no display component found!\n"


# include decoder component for the outputfile
if outputEnc == "rle":
    decoderFile = os.path.join(os.path.curdir, "components", "rle-decoder.lua")
    if os.path.isfile(decoderFile):
        with open(decoderFile, "r") as file:
            fileLines = [line.strip('\n') for line in file.readlines()]
            codeStart = next((index for index, tag in enumerate(fileLines) if tag == '-- CODEBLOCK'), -1)
            compDecoder = "\n".join(fileLines[codeStart+1:]) + "\n"
    else:
        compDecoder = "\n no decoder component found!\n"
else:
    compDecoder = ""


# save generated data to outputfile (lua-script)
dataFile = outputFile + ".lua"
print(" try to save: " + str(dataFile))
check_file(dataFile)
try:
    with open(dataFile, 'w') as file:
        file.write("-- title:  " + str(imageFile) + "\n")  # write header
        file.write("-- author: mulTIColor\n")
        file.write("-- script: lua\n")
        file.write("\n")
        file.write('pal = "' + Palette + '"\n')  # write palette
        file.write("\n")
        if outputEnc == 'rle':
            file.write('rle = "' + enc + '"\n')  # write RLE
        else:
            file.write('gfx = "' + Pixels + '"\n')  # write pixels (RAW)
        file.write(compDecoder)
        file.write(compDisplay)
except Exception as error:
    print("ERROR: " + str(error), file=sys.stderr)
    exit(1)


# save converted image to outputfile (with prefix)
outputFile = outputFile + "-mtc"
print(" try to save: " + str(outputFile))
check_file(outputFile)
try:
    newImg.save(outputFile)
except ValueError as error:
    if 'unknown file extension' in str(error):
        print(" try to save: " + str(outputFile) + str(orgFormat))
        check_file(outputFile + orgFormat)
        try:
            newImg.save(outputFile + orgFormat)
        except Exception as error:
            print("ERROR: " + str(error), file=sys.stderr)
            exit(1)
    else:
        print("ERROR: " + str(error), file=sys.stderr)
        exit(1)
except Exception as error:
    print("ERROR: " + str(error), file=sys.stderr)
    exit(1)


# end message
print(" done.")


# end of code
exit()
