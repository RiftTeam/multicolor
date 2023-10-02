#!/usr/bin/python3
#
# mulTIColor - convert images to TIC-80 multicolor mode
#
# Hint: python -m pip install pillow (install PIL on Windows)
#
# last updated by Decca / RiFT on 02.10.2023 14:55


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
              "  -r, --range        range of colors per line (16 or 31)\n"
              "  -b, --bordercolor  bordercolor (R G B) to prevent streaking\n"
              "  -m, --mode         mode to encode values: raw (default) or rle\n"
              "  -v, --version      show version info\n"
              "  -h, --help         show this help\n"
              "\n"
              "The optional arguments are only needed if the default setting does not meet the\n"
              "required needs. A specific name for the output file can be set (-o / --output).\n"
              "The maximum range (-r / --range) of colors per line, can be set to 16 or 31.\n"
              "To prevent colorstreaking in the border, a specific color (-b / --bordercolor)\n"
              "can be set. WARNING: this will reduce the overall colors to 15 or 30 per line!\n"
              "Mode (-m / --mode) to encode the pixel data via rle (run-length encoding) or as\n"
              "raw, which is the default. To reduce the colors of the image per line, various\n"
              "converters (-c / --converter) can be used. These can be configured in \"mtc.cfg\".\n"
              "Additional defined are: \"iview\" for IrfanView, \"magick\" for ImageMagick.\n"
              "\n"
              "examples:\n"
              "  multicolor imagefile.png \n"
              "  multicolor graphic.gif -o multicolor.lua\n"
              "  multicolor pixels.png -c iview -o mydata.lua\n"
              "  multicolor colorful.gif -r 16 -o only16.lua\n"
              "  multicolor border.jpg -r 31 -b 255 127 64 -o frame.lua\n"
              "  multicolor truecol.png -m rle -o compress.lua\n"
              "  multicolor logo.gif -o overwriteme.lua -f\n", file=sys.stderr)
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
parser.add_argument('-r', '--range',
                    metavar='range',
                    const=16,
                    default=16,
                    choices=(16, 31),
                    type=int,
                    nargs='?',
                    action='store',
                    help='range of colors per line (16 or 31)')
parser.add_argument('-b', '--bordercolor',
                    metavar='255',
                    type=int,
                    nargs=3,
                    action='store',
                    help='bordercolor (R G B) to prevent streaking')
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
                    version='%(prog)s 1.3')
args = parser.parse_args()


# get commandline arguments
imageFile = args.image
outputConv = args.converter
outputFile = args.output
outputEnc = args.mode
outputBorder = args.bordercolor
outputRange = args.range
outputForce = args.force


# set or init vars
configFile = "mtc.cfg"
iniFile = ""
convCommand = None
convBinary = None
if outputRange > 16:
    digits = 2
else:
    digits = 1


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
dominantColor = max(orgColors)
print("      Colors: " + str(len(orgColors)))


# check and set bordercolor
if len(orgColors) > 16:
    if isinstance(outputBorder, list):
        borderColor = tuple(outputBorder)
        print(" Bordercolor: " + str(borderColor).replace("(", "").replace(")", ""))
        borderHex = ""
        for color in borderColor:
            borderHex = borderHex + str('%0*x' % (2, color))
        # reduce colorrange per line, because of the bordercolor
        workRange = outputRange - 1
    else:
        workRange = outputRange
    print("       Range: " + str(workRange) + " colors")
else:
    # empty outputRange when image is not multicolor
    workRange = outputRange
    outputRange = ""
    print("       Range: indexed colors")


# check image dimensions
if orgSizeX > 240:
    print("ERROR: image is wider than 240 pixels")
    exit(1)
if orgSizeY > 136:
    print("ERROR: image is higher than 136 pixels")
    exit(1)


# check and read config for external converter
if outputConv != 'pil':
    if not os.path.isfile(configFile):
        print("ERROR: no configuration file found (" + configFile + ")")
        exit(1)
    else:
        with open(configFile) as file:
            for line in file:
                if line.startswith(outputConv + " = "):
                    name, command = line.split('=', 1)
                    convCommand = command.strip()
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
                # print(tmpDir)  # DEBUG
                inFile = os.path.join(tmpDir, 'mtc-infile' + orgFormat)
                outFile = os.path.join(tmpDir, 'mtc-outfile' + orgFormat)
                convSubproc = convCommand.replace('{IN}', '"' + inFile + '"')
                convSubproc = convSubproc.replace('{OUT}', '"' + outFile + '"')
                # Range & TempDir are optional, no need for checks
                convSubproc = convSubproc.replace('{RANGE}', '"' + str(workRange) + '"')
                convSubproc = convSubproc.replace('{TEMPDIR}', '"' + tmpDir + '"')
            # check converter binary
            convBinary = convCommand.split('"')[1].split('"')[0]
            if not os.path.isfile(convBinary):
                print("ERROR: " + convBinary + " not found")
                exit(1)


# create ini-file for Irfanview if needed
if convBinary is not None:
    # print(os.path.basename(convBinary))  # DEBUG
    if "i_view" in os.path.basename(convBinary):
        if "32" in os.path.basename(convBinary):
            iniFile = os.path.join(tmpDir, 'i_view32.ini')
        else:
            iniFile = os.path.join(tmpDir, 'i_view64.ini')
        try:
            with open(iniFile, 'w') as file:
                file.write("[Batch]\n")
                file.write("AdvUseBPP=1\n")
                file.write("AdvBPP=" + str(workRange) + "\n")
                file.write("AdvUseFSDither=0\n")
                file.write("AdvDecrQuality=1\n")
        except Exception as error:
            print("ERROR: " + str(error), file=sys.stderr)
            exit(1)


# remove file-extension for saner filenaming
if outputFile.endswith(".lua"):
    outputFile = outputFile[:-len(".lua")]


# function when using an external converter
def ext_conv(convLine):
    # save line to reduce
    try:
        convLine.save(inFile)
    except Exception as error:
        print("ERROR: " + str(error), file=sys.stderr)
    # execute converter
    subprocess.run(convSubproc, shell=True)
    # load reduced line
    try:
        doneLine = Image.open(outFile)
    except Exception as error:
        print("ERROR: " + str(error), file=sys.stderr)
    return doneLine


# function to convert a multicolor-image to range of colors per line
def convert_range():
    print("   Converting with " + outputConv + "...")
    offsetY = 0
    toReduce = 0
    alreadyOk = 0
    while offsetY < orgSizeY:
        Line = orgImg.crop((0, offsetY, orgSizeX, offsetY + 1))
        Colors = Line.convert('RGB').getcolors(maxcolors=(orgSizeX))
        if len(Colors) > workRange:
            if outputConv == 'pil':
                newLine = Line.convert("P", palette=Image.ADAPTIVE, colors=workRange)
            else:
                extLine = ext_conv(Line)
                newLine = extLine.convert("P", palette=Image.ADAPTIVE, colors=workRange)
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
        if os.path.isfile(iniFile):
            os.remove(iniFile)


# function to get values from a converted multicolor-image
def get_multicolor():
    Pal = ""
    Pix = ""
    offsetY = 0
    offsetX = 0
    while offsetY < orgSizeY:
        # set bordercolor
        if isinstance(outputBorder, list):
            Pal = Pal + borderHex
            palOffset = 1
        else:
            palOffset = 0
        Line = newImg.crop((0, offsetY, orgSizeX, offsetY + 1))
        rawLine = Line.convert("P", palette=Image.ADAPTIVE, colors=workRange)
        # pixel values in hex (0 to f)
        while offsetX < orgSizeX:
            palIndex = rawLine.getpixel((offsetX, 0))
            hexVal = '%0*x' % (digits, (palIndex + palOffset))
            Pix = Pix + hexVal
            offsetX = offsetX + 1
        offsetY = offsetY + 1
        offsetX = 0
        # palette in hex (00 to ff)
        rawPalette = rawLine.getpalette()
        rgbEntries = workRange * 3
        rgbPalette = rawPalette[:rgbEntries]
        for entry in rgbPalette:
            hexVal = '%0*x' % (2, entry)
            Pal = Pal + hexVal
    return (Pix, Pal)


# function to get values from an indexed-image
def get_indexed():
    # set palette for output file
    stdPalette = "1a1c2c5d275db13e53ef7d57ffcd75a7f07038b76425717929366f3b5dc941a6f673eff7f4f4f494b0c2566c86333c57"  # SWEETIE-16 palette
    newPalette = newImg.getpalette()  # get original palette from image
    rgbEntries = (2 ** 4) * 3
    rgbPalette = newPalette[:rgbEntries]
    Pal = ""
    for entry in rgbPalette:
        hexVal = '%0*x' % (2, entry)
        Pal = Pal + hexVal
    Pal = Pal + stdPalette[len(Pal):]  # fill up with default palette
    # swap values (low & high nibble) for the unified decoder
    Pal = ''.join([Pal[val:val + 2][::-1] for val in range(0, len(Pal), 2)])  # (https://stackoverflow.com/a/4606057)
    Pix = ""
    # get values from converted image
    offsetY = 0
    offsetX = 0
    while offsetY < orgSizeY:
        while offsetX < orgSizeX:
            palIndex = newImg.getpixel((offsetX, offsetY))
            hexVal = '%0*x' % (1, palIndex)
            Pix = Pix + hexVal
            offsetX = offsetX + 1
            # print(palIndex, hexVal)  # DEBUG
        # exit(1)  # DEBUG
        offsetY = offsetY + 1
        offsetX = 0
    return (Pix, Pal)


# start the conversion
print("   Generating data...")
if len(orgColors) > 16:
    # create new image for pasting
    newImg = Image.new(mode="RGB", size=(orgSizeX, orgSizeY))
    # convert lines to color-range
    convert_range()
    # get multicolor values
    Pixels, Palette = get_multicolor()
else:
    # check image mode and convert if neccessary
    if orgMode != 'P':
        newImg = orgImg.convert("P", palette=Image.ADAPTIVE, colors=len(orgColors))
        print("     WARNING: image converted to indexed colors, results may vary")
    else:
        newImg = orgImg
    # set digits to 16 colors only
    digits = 1
    # get indexed values
    Pixels, Palette = get_indexed()


# compress 16 colors pixel data (rle: only append number if value repeats more than twice)
def encode_rle16(data):
    enc = ""
    prev = ""
    count = 1
    for symbol in data:
        value = chr(int(symbol, 16) + 65)
        if value != prev:
            if prev:
                enc = enc + prev
                if count == 2:
                    enc = enc + prev
                elif count > 2:
                    enc = enc + str(count - 1)
            count = 1
            prev = value
        else:
            count = count + 1
    enc = enc + prev
    if count == 2:
        enc = enc + prev
    elif count > 2:
        enc = enc + str(count - 1)
    if not enc[-1].isdigit():
        enc = enc + "0"
    return enc


# compress 31 colors pixel data (rle: only append number if value repeats more than twice)
def encode_rle31(data):
    enc = ""
    prev = ""
    count = 1
    for char1, char2 in zip(data[::digits], data[digits - 1::digits]):
        value = chr(int(char1 + char2, 16) + 65)
        if value != prev:
            if prev:
                enc = enc + prev
                if count == 2:
                    enc = enc + prev
                elif count > 2:
                    enc = enc + str(count - 1)
            count = 1
            prev = value
        else:
            count = count + 1
    enc = enc + prev
    if count == 2:
        enc = enc + prev
    elif count > 2:
        enc = enc + str(count - 1)
    if not enc[-1].isdigit():
        enc = enc + "0"
    enc = enc.replace('\\', '&')
    return enc


# compress the data if needed
if outputEnc == 'rle':
    if digits == 1:
        RlePalette = encode_rle16(Palette)  # RLE encode palette (0-f/1 digit)
        RlePixels = encode_rle16(Pixels)  # RLE encode pixels (0-f/1 digit)
    if digits == 2:
        RlePalette = encode_rle16(Palette)  # RLE encode palette (still 0-f/1 digit)
        RlePixels = encode_rle31(Pixels)  # RLE encode pixels (31colors/2 digits)
else:
    RawPalette = Palette
    RawPixels = Pixels


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
displayFile = os.path.join(os.path.dirname(__file__), "components", "display" + str(outputRange) + ".lua")
if os.path.isfile(displayFile):
    with open(displayFile, "r") as file:
        fileLines = [line.strip('\n') for line in file.readlines()]
        codeStart = next((index for index, tag in enumerate(fileLines) if tag == '-- CODEBLOCK'), -1)
        compDisplay = "\n".join(fileLines[codeStart + 1:]) + "\n"
else:
    print("ERROR: no display component found")
    compDisplay = "\n-- ERROR: no display component found!\n"


# include decoder component for the outputfile
if outputEnc == "rle":
    decoderFile = os.path.join(os.path.dirname(__file__), "components", "rle-decoder" + str(outputRange) + ".lua")
    if os.path.isfile(decoderFile):
        with open(decoderFile, "r") as file:
            fileLines = [line.strip('\n') for line in file.readlines()]
            codeStart = next((index for index, tag in enumerate(fileLines) if tag == '-- CODEBLOCK'), -1)
            compDecoder = "\n".join(fileLines[codeStart + 1:]) + "\n"
    else:
        print("ERROR: no decoder component found")
        compDecoder = "\n-- ERROR: no decoder component found!\n"
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
        if outputEnc == 'rle':
            file.write('rlp = "' + RlePalette + '"\n')  # write RLE palette
            file.write("\n")
            file.write('rlg = "' + RlePixels + '"\n')  # write RLE pixels
        else:
            file.write('pal = "' + RawPalette + '"\n')  # write palette (RAW)
            file.write("\n")
            file.write('gfx = "' + RawPixels + '"\n')  # write pixels (RAW)
        if len(orgColors) <= 16:
            file.write("\n")
            file.write('res = ' + str(orgSizeX - 1) + '\n')  # write resolution of lines
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
