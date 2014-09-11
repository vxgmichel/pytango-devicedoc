## Synopsis

Sphinx extension for Tango devices documentation.
Not compatible with POGO generated code, use HLAPI instead.

## Requirement

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

## Syntax

This extension contains the following sphinx directives:

- autotangodevice
- autotangoitem
- autotangoattribute
- autotangoproperty
- autotangocommand

In particular, the autotangoitem directive is pretty useful to customize the documentation:

    My Documentation
    ================

    .. automodule:: mymodule

    .. autoclass:: MyDevice

    Custom Title
    ############

    Another custom title
    --------------------

    .. autotangoitem:: MyDevice.SomeProperty

    .. autotangoitem:: MyDevice.someAttribute

    .. autotangoitem:: MyDevice.SomeCommand

However, the simplest usage for a complete and fully automated documentation is:

    .. automodule:: mymodule
        :members: MyDevice

## Warning

The above syntax is currently the only way to generate the full documentation 
using automatic headers and titles.

For instance, this syntax will get rid of every title:

    .. autotangodevice:: mymodule.MyDevice
        :members: 

## Improvements

The use of headers and sections is probably the less flexible part of the code.
Eventually, it should be handled via directive options.

## Contributors

Feel free to improve the different documenters.
In particular, the descriptions could definitely use some customization.

## Contact

Vincent Michel: vincent.michel@maxlab.lu.se
