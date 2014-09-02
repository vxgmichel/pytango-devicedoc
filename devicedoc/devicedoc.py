"""Tango Sphinx extension to automatically generate documentation
from a HLAPI Tango Device class."""

# Imports
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

    def __repr__(self):
        """Generate a readable representation."""
        args = []
        # Add type
        name = type(self).__name__.replace('_',' ')
        base = "{}(".format(name.capitalize())
        # Add kwargs
        for key, value in sorted(self.kwargs.items()):
            if value == "":
                value = "None"
            args.append("{} = {}".format(key, value))
        if len(args) > 1:
            sep = ',\n' + ' ' * len(base)
        else:
            sep = ''
        return base + sep[1:] + sep.join(args) + ')'

    def get_doc(self):
        """Get the documentation from the object."""
        if self.func_doc:
            return self.func_doc
        return self.kwargs.get('doc', '')


# Tango mock
class device_property(BaseMock): pass
class attribute(BaseMock): pass
class command(BaseMock): pass
class DeviceMeta(type): pass
class Device(object):
    __metaclass__ = DeviceMeta


# Monkey patching
def pytango_patch():
    from types import MethodType
    from PyTango import server
    server.attribute = attribute
    server.command = command
    server.device_property = device_property
    server.Device = Device
    server.DeviceMeta = DeviceMeta


# Tango device documenter
class TangoDeviceDocumenter(ClassDocumenter):
    """ Documenter for tango device classes."""
    objtype = 'tangodevice'
    directivetype = 'class'
    section = "{0} Device Documentation"
    valid_types = (attribute, device_property, command)
    priority = ClassDocumenter.priority
    priority += 1

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
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
            BaseTangoDocumenter.reset()
        ClassDocumenter.document_members(self, all_members)


# Tango base documenter
class BaseTangoDocumenter(ClassLevelDocumenter):
    """Base class for documenting tango objects
    (device properties, attirbutes and commands).
    """
    objtype = 'basetango'
    directivetype = 'attribute'
    mocktype = None
    priority = AttributeDocumenter.priority
    priority += 1
    started = defaultdict(bool)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, cls.mocktype)

    @classmethod
    def reset(cls):
        cls.started.clear()

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
        obj_doc = self.object.get_doc() + NL
        return [obj_repr.split(NL), obj_doc.split(NL)] 

    def add_content(self, more_content, no_docstring=False):
        """Patch to add the documentation from the mock object
        before any other documentation."""
        docstrings = self.get_doc()
        for i, line in enumerate(self.process_doc(docstrings)):
            self.add_line(line, '<autodoc>', i)
        ClassLevelDocumenter.add_content(self, more_content, True)
        

# Tango property documenter
class TangoPropertyDocumenter(BaseTangoDocumenter):
    objtype = 'tangoproperty'
    directivetype = 'attribute'
    section = "Device properties"
    mocktype = device_property
    member_order = 70


# Tango attribute documenter
class TangoAttributeDocumenter(BaseTangoDocumenter):
    objtype = 'tangoattribute'
    directivetype = 'attribute'
    section = "Attributes"
    mocktype = attribute
    member_order = 80


# Tango command documenter
class TangoCommandDocumenter(BaseTangoDocumenter):
    objtype = 'tangocommand'
    directivetype = 'attribute'
    section = "Commands"
    mocktype = command
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
    app.add_autodocumenter(TangoCommandDocumenter)