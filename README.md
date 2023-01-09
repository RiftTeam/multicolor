![mulTIColor Logo](https://repository-images.githubusercontent.com/474191033/6b4ec005-585c-4c27-a4f4-b6eea5f3b6ea)

mulTICcolor
===========

A converter for mulitcolor-mode on the [TIC-80](https://tic80.com/).

The [TIC-80](https://tic80.com/) normaly supports a max. [resolution](https://github.com/nesbox/TIC-80/wiki/display) of 240 pixels x 136 pixels with a [palette](https://github.com/nesbox/TIC-80/wiki/palette) of 16 RGB-colors.
But it is possible to change the palette every scanline with some [tweaks](https://github.com/nesbox/TIC-80/wiki/palette#more-than-16-colors), resulting in max. 2176 or even 4216 colors on screen.

**mulTICcolor** converts an image (240 x 136 pixels) to a version with max. 16 or 31 colors per line.
The result will be saved as an image and as a [Lua](https://www.lua.org)-script with all the palettes, pixels and a display-routine (when using the "o"-option).


Information
===========

To reduce the colors to 16 per line, there are 3 options by default to achieve this:
1. [PIL](https://pillow.readthedocs.io/en/stable/) (Python Image Library, built-in)
2. [IrfanView](https://www.irfanview.com/) (external executable)
3. [ImageMagick](https://imagemagick.org/index.php) (external executable)

You might have to adjust the paths for [IrfanView](https://www.irfanview.com/) and [ImageMagick](https://imagemagick.org/index.php) in the configfile (**mtc.cfg**).
You can also add other converters or paths for a different operating system to the config aswell. Make sure to include the three keywords **{IN}**, **{OUT}** and **{RANGE}** to your entries. 
They ensure, that the current line of the image which is written to a temporary file can be converted and imported again afterwards. There is an optional keyword **{TEMPDIR}**, which can be used to store additional files for a converter like [IrfanView](https://www.irfanview.com/), if needed.

Based on the source image, all available options should be tried and the best result can be used directly.
But it is recommended to manually edit/optimize the best result by the creator of the original image.

When using the -o option, a .[lua](https://www.lua.org)-script will be generated (too), which contains the palettes and pixel data.
The **pal**-variable will contain 136 palettes with 16 or 31 RGB-colors, each in hex (from 00 to ff).
The **gfx**-variable will contain 240 x 136 pixels (color-index in hex, from 0 to f with 16 colors / from 00 to 1e with 31 colors).
When using [RLE (Run-length encoding)](https://en.wikipedia.org/wiki/Run-length_encoding) the pixels are stored in the **rle**-variable.


Requirements
============

- Python (3.6, or greater) - https://www.python.org/
- Pillow (Python Imaging Library) - https://pypi.org/project/Pillow/


Installation
============
If missing, **Pillow** can be installed using **pip** (for Python3).

Linux: 

    $ pip install pillow
Windows:

    $ python -m pip install pillow


Quickstart
==========

**mulTIColor** is easy to use and its really simple to convert an image to multicolor-mode.
Just run `multicolor` using the provided example images:

    $ multicolor.py piggie_power_without_the_price.png

    Generates a preview of the converted image, will be shown by the OS's default image viewer.

Specify an output name to generate the lua-script and save the preview:

    $ multicolor.py kittens.png -o smallcats
	
	The preview is saved as "smallcats-mtc.png" and the lua-script as "smallcats.lua".

Use a different converter to reduce the colors of the image per line:

    $ multicolor.py dryad.png -c iview -o resultsmyvary
	
	Have a look at the provided config file "mtc.cfg" for the paths and binaries.

Switch the range to 31 colors per line to get a, hopefully, better result:

    $ multicolor.py kittens.png -c iview -r 31 -o somemorecolors

Encode the pixel data as rle (run-length encoded) to save some space:

    $ multicolor.py kittens.png -o smallerscript -m rle


Commandline options
===================

    $ multicolor.py --help
	
    Usage: multicolor imagefile [OPTION...]
    Generate TIC-80 multicolor images
    
    mandatory arguments:
      imagefile          imagefile with graphicsdata (e.g.: .png, .gif, etc.)
    
    optional arguments:
      -c, --converter    converter: pil (default), see mtc.cfg for more
      -o, --output       outputfile for multicolor values (.lua)
      -f, --force        force overwrite of outputfile when it already exist
      -r, --range        range of colors per line (16 or 31)
      -m, --mode         mode to encode values: raw (default) or rle
      -v, --version      show version info
      -h, --help         show this help
    
    The optional arguments are only needed if the default setting does not meet the
    required needs. A specific name for the outputfile can be set (-o / --output).
    The range of maximum colors per line (of the image file) can be set to 16 or 31.
	Mode (-m / --mode) to encode the pixel data via rle (run-length encoding) or as
	raw, which is the default. To reduce the colors of the image per line, various
	converters (-c / --converter) can be used. These can be configured in "mtc.cfg".
	Additional defined are: "iview" for IrfanView, "magick" for ImageMagick.
    
    examples:
	  multicolor imagefile.png
      multicolor graphic.gif -o multicolor.lua
      multicolor pixels.png -c iview -o mydata.lua
      multicolor colorful.gif -r 16 -o only16.lua
      multicolor truecol.png -m rle -o compress.lua
      multicolor logo.gif -o overwriteme.lua


Files
=====

* **multicolor.py** (the converter itself)
* **images/piggie_power_without_the_price.png** (example image (23960 colors), [original](https://demozoo.org/graphics/205191/) by [Bossman](https://demozoo.org/sceners/32053/)/[Rift](https://www.pouet.net/groups.php?which=11428))
* **images/kittens.png** (example image (23704 colors), [original](https://demozoo.org/graphics/302070/) by [Evil](https://demozoo.org/sceners/5794/)/[Accession](https://www.pouet.net/groups.php?which=1004))
* **images/dryad.png** (example image (17056 colors), [original](https://demozoo.org/graphics/266505/) by [Lycan](https://demozoo.org/sceners/21309/)/[LNX](https://www.pouet.net/groups.php?which=11760))
* **components/display16.lua** (the display-routine for 16 colors)
* **components/display31.lua** (the display-routine for 31 colors)
* **components/rle-decoder.lua** (the decoder when using rle-mode)


Disclaimer
==========

There is no warranty for the scripts or it's functionality, use it at your own risk.

The icon/logo consists of the [Sweetie 16](https://lospec.com/palette-list/sweetie-16)-palette © by [GrafxKid](https://grafxkid.tumblr.com/) & a [Shredder clipart](https://www.clipartmax.com/middle/m2H7N4d3G6N4b1H7_shredder-machine-icon-clipart-paper-office-shredders-shredder-machine-icon/) © by [Clipartmax](https://clipartmax.com/).


Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/PhilSwiss/multicolor/issues


Contributing
============

Development of `mulTIColor` happens at GitHub: https://github.com/PhilSwiss/multicolor
