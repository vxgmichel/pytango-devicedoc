## Synopsis

Sphinx extension for Tango devices documentation.
Not compatible with POGO generated code, use HLAPI instead.

## Requirement

These packages are required:

- Sphinx
- PyTango 8.1.2

## Installation

Two possibilities:

- Run python setup.py install

Or:

- Copy the 'tangodoc/tangodoc.py' file anywhere you want.
- Make sure that it will be accessible using the python path.

In both cases:

- Append 'tangodoc' to the extensions list in your sphinx configuration file.

## Demo

This repository contains a simple demo of the devicedoc extension.
In order to build the documentation, use the 'demo/build_doc' script.
Then take a look at:

- The 'demo/powersupply.py' module. Example of documented HLAPI Device class. 
- The 'demo/conf.py' sphinx configuration file. Contains a minimalist configuration.
- The 'demo/index.rst' reStructuredText file. Contains the directive to generate the documentation.
- The generated documentation: 'demo/build/index.html'

## Warning

This extension is still not as flexible as I want it to be.
It allows you to use special directive as:

- autotangodevice
- autotangoattribute
- autotangoproperty
- autotangocommand

These haven't been completely tested and are not guaranteed to work.
The safest usage is to stick to the automodule directive as written in the demo.

## Improvements

The use of headers and sections is probably the less flexible part of the code.
Eventually, it should be handled via directive options.

## Contributors

Feel free to improve the different documenters.
In particular, the descriptions could definitely use some customization.

## Contact

Vincent Michel: vincent.michel@maxlab.lu.se
