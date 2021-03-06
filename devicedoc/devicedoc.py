"""Tango Sphinx extension to automatically generate documentation
from a HLAPI Tango Device class."""

# Imports
from importlib import import_module
from sphinx.util import force_decode
from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, AttributeDocumenter
from sphinx.ext.autodoc import ClassLevelDocumenter
from collections import defaultdict


# Mock
class BaseMock(object):
    """Mocking base class."""

    def __init__(self, func=None, **kwargs):
        """Save kwargs and function documentation."""
        self.kwargs = kwargs
        self.func_doc = func.__doc__ if func else None

    def __call__(self, func):
        """Decorator support."""
        self.func_doc = func.__doc__
        return self

    def setter(self, func):
        """Decorator support."""
        return self

    def deleter(self, func):
        """Decorator support."""
        return self

    def __repr__(self):
        """Generate a readable representation."""
        args = []
        # Add type
        name = type(self).__name__.replace('_', ' ')
        base = "{}:\n".format(name.capitalize())
        # Add kwargs
        for key, value in sorted(self.kwargs.items()):
            if key in ["doc", "fget", "fset", "fisallowed"]:
                continue
            if value == "":
                value = "None"
            try:
                value = value.__name__
            except AttributeError:
                pass
            args.append("    - {0} : {1}".format(key, value))
        if not args:
            return base[:-2] + '.'
        return base + '\n'.join(args)

    def get_doc(self, encoding=None):
        """Get the documentation from the object."""
        doc = self.func_doc or self.kwargs.get('doc') or ''
        return force_decode(doc, encoding)


# Tango mock

class class_property(BaseMock):
    """Mock for class property."""
    pass


class device_property(BaseMock):
    """Mock for device property."""


class attribute(BaseMock):
    """Mock for TANGO attribute."""
    def write(self, method):
        pass


class command(BaseMock):
    """Mock for TANGO command."""
    __tango_command__ = True
    __name__ = "tango_command"


class DeviceMeta(type):
    """Mock for device metaclass."""
    pass


class Device(object):
    """Mock for device class."""
    __metaclass__ = DeviceMeta

    def run_server(self, cls):
        pass


# Monkey patching
def pytango_patch():
    from PyTango import server
    server.attribute = attribute
    server.command = command
    server.device_property = device_property
    server.class_property = class_property
    server.Device = Device
    server.DeviceMeta = DeviceMeta


# Reload object
def reload_object(obj):
    """Reload an object if possible"""
    if not isinstance(obj, type):
        return obj
    try:
        module = reload(import_module(obj.__module__))
        return getattr(module, obj.__name__)
    except:
        return obj


# Tango device documenter
class TangoDeviceDocumenter(ClassDocumenter):
    """ Documenter for tango device classes."""
    objtype = 'tangodevice'
    directivetype = 'class'
    section = "{0} Device Documentation"
    valid_types = (attribute, class_property, device_property, command)
    priority = ClassDocumenter.priority
    priority += 1

    def import_object(self):
        reload(import_module(self.modname))
        return ClassDocumenter.import_object(self)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        member = reload_object(member)
        return isinstance(member, DeviceMeta)

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):
        """Patch to add a header."""
        # Get object
        if not self.parse_name() or not self.import_object():
            return
        # Add header
        if all_members:
            self.indent, temp = '', self.indent
            section = self.section.format(self.object.__name__)
            self.add_line(section, '<autodoc>')
            self.add_line("*" * len(section), '<autodoc>')
            self.indent = temp
        # Generate documentation
        ClassDocumenter.generate(self, more_content, real_modname,
                                 check_module, all_members)

    def filter_members(self, members, want_all):
        """Filter to keep only objects of valid types."""
        filt = lambda arg: isinstance(arg[1], self.valid_types)
        filtered_members = filter(filt, members)
        return [(name, member, True) for name, member in filtered_members]

    def document_members(self, all_members=False):
        """Prepare environment for automatic device documentation"""
        if all_members:
            self.options.member_order = 'groupwise'
            self.env.config.autodevice = True
            TangoItemDocumenter.reset()
        ClassDocumenter.document_members(self, all_members)


# Tango item documenter
class TangoItemDocumenter(ClassLevelDocumenter):
    """Base class for documenting tango objects
    (device properties, attirbutes and commands).
    """
    objtype = 'tangoitem'
    directivetype = 'attribute'
    member_order = -1
    types = [class_property, device_property, attribute, command]
    priority = AttributeDocumenter.priority + 1
    started = defaultdict(bool)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return any(isinstance(member, mocktype) for mocktype in cls.types)

    @classmethod
    def reset(cls):
        cls.started.clear()

    def import_object(self):
        """Load an object."""
        # Get the object
        if not ClassLevelDocumenter.import_object(self):
            return False
        # Reload modules
        self.parent = reload_object(self.parent)
        reload(import_module(self.modname))
        # Get the new object
        return ClassLevelDocumenter.import_object(self)

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):
        """Patch to add a header."""
        # Get object
        if not self.parse_name() or not self.import_object():
            return
        # Check if header needed
        tangotype = type(self.object)
        autodevice = getattr(self.env.config, 'autodevice', False)
        if autodevice and not self.started[tangotype]:
            # Tag as started
            self.started[tangotype] = True
            self.indent, temp = '', self.indent
            # Add header
            self.add_line(self.section, '<autodoc>')
            self.add_line("-" * len(self.section), '<autodoc>')
            self.indent = temp
        # Generate documentation
        ClassLevelDocumenter.generate(self, more_content, real_modname,
                                      check_module, all_members)

    def get_doc(self, encoding=None, ignore=1):
        """Patch to get the docs from the mock object."""
        NL = '\n'
        MU = ' |'
        obj_repr = repr(self.object).replace(NL, NL+MU) + NL
        obj_doc = self.object.get_doc(encoding) + NL
        return [obj_repr.split(NL), obj_doc.split(NL)]

    def add_content(self, more_content, no_docstring=False):
        """Patch to add the documentation from the mock object
        before any other documentation."""
        encoding = self.analyzer and self.analyzer.encoding
        docstrings = self.get_doc(encoding)
        for i, line in enumerate(self.process_doc(docstrings)):
            self.add_line(line, '<autodoc>', i)
        ClassLevelDocumenter.add_content(self, more_content, True)


# Tango class property documenter
class TangoClassPropertyDocumenter(TangoItemDocumenter):
    priority = TangoItemDocumenter.priority + 1
    objtype = 'tangoclassproperty'
    section = "Class properties"
    types = [class_property]
    member_order = 60


# Tango property documenter
class TangoPropertyDocumenter(TangoItemDocumenter):
    priority = TangoItemDocumenter.priority + 1
    objtype = 'tangoproperty'
    section = "Device properties"
    types = [device_property]
    member_order = 70


# Tango attribute documenter
class TangoAttributeDocumenter(TangoItemDocumenter):
    priority = TangoItemDocumenter.priority + 1
    objtype = 'tangoattribute'
    section = "Attributes"
    types = [attribute]
    member_order = 80


# Tango command documenter
class TangoCommandDocumenter(TangoItemDocumenter):
    priority = TangoItemDocumenter.priority + 1
    objtype = 'tangocommand'
    section = "Commands"
    types = [command]
    member_order = 90


# Setup the sphinx extension
def setup(app):
    """Sphinx extension setup function."""
    if not isinstance(app, Sphinx):
        return
    pytango_patch()
    app.add_autodocumenter(TangoDeviceDocumenter)
    app.add_autodocumenter(TangoAttributeDocumenter)
    app.add_autodocumenter(TangoPropertyDocumenter)
    app.add_autodocumenter(TangoClassPropertyDocumenter)
    app.add_autodocumenter(TangoCommandDocumenter)
    app.add_autodocumenter(TangoItemDocumenter)
