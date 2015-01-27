"""A module for generating valid, simple XML.

This module allows you to build XML documents using python code. It is
designed to be as simple as possible. So you might have

>>> b = xml.book(xml.title('The Title'), xml.author('Ian Millington'))

and have it rendered to xml with:

>>> b.xml
'<book><title>The Title</title><author>Ian Millington</author></book>'

Notice that multiple arguments get mapped to multiple child tags in
sequence. The most onerous problem with this is that tags that are not
valid python identifiers are not valid: you can't have <book-title>
for example (namespaces are even more common, but they are handled
differently - see below). Fortunately you can get tags corresponding
to any string using dictionary syntax:

>>> b = xml.book(xml['book-title']('The Title'))
>>> b.xml
'<book><book-title>The Title</book-title></book>'

Tag properties are given as keyword arguments

>>> xml.book(title='The Title').xml
'<book title="The Title"/>'

If you have both properties and child-tags, because of python syntax the
children go first:

>>> xml.book(xml.content("..."), title='The Title').xml
'<book title="The Title"><content>...</content></book>'

This may be confusing, if you're used to XML coding. To get around
this you can include all your children in a list with the special
keyword argument '_':

>>> xml.book(title='The Title', _=[xml.content("...")]).xml
'<book title="The Title"><content>...</content></book>'

You can also mix the two styles, but that can get confusing.

There's one other 'special' keyword argument. If you need properties
that aren't valid python keywords, you can pass in a dictionary
manually using '__':

>>> xml.book(__={'book-title': 'The Title'}).xml
'<book book-title="The Title"/>'

As well as other tags and strings, any python object appearing in the
xml tree will get rendered to xml by having its 'xml' property
accessed, if that fails it will be turned into a python string using
str().

>>> from datetime import datetime
>>> xml.book(datetime(1970,1,1)).xml
'<book>1970-01-01 00:00:00</book>'

The .xml check isn't performed for objects appearing as the value in a
property, however. Because properties can't contain other text, they
will always be converted to a string.



DTD and XML header

The approach above is the very simplest that can work. More commonly
you'll want to have the normal XML-document furniture present. You do
this using an instance of type XMLCreator. A basic one is provided:
makeXML. You simply call instances of this class with the XML tree
you've built, rather than accessing their .xml property directly.

>>> b = xml.book(xml.title('The Title'), xml.author('Ian Millington'))
>>> makeXml(b)
'<?xml version="1.0"?><book><title>The Title</title><author>Ian Millington</author></book>'

The makeXml simply adds the XML version tag. There is a makeXhtml
creator which is a bit more sophisticated:

>>> makeXhtml(xml.html(xml.head(xml.title('My Title')), xml.body('Content')))
'<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html><head><title>My Title</title></head><body>Content</body></html>'

It is recommended that you always go through a XMLCreator (rather than
calling .xml directly on the xml tree you've built), because creators
add extra namespace handling support.



Creating Your Own Namespaces and Creators

If you are creating your own XML application, you'll probably want to
make a new creator. You may also need a new namespace (but it is less
likely).

To make a new XmlCreator:

makeMyXmlDialect = XMLCreator(systemDTD, publicDTD, rootTag)

The DTD elements make the creator use a <!DOCTYPE ...> definition. The
rootTag also appears in the DTD (and makes sure that the xml used does
match that tag).

To make a new XmlNamespace:

myXmlNamespace = XMLNamespace(name, uri, listOfAllowedTags)

For example:

>>> mx = XMLNamespace('mx', 'http://www.adobe.com/2006/mxml')
>>> app = mx.Application()
>>> makeXml(app)
'<?xml version="1.0"?><mx:Application xmlns:mx="http://www.adobe.com/2006/mxml"/>'

If you mix namespaces in a document, the generator puts all the
namespace declarations in the opening tag, it doesn't attempt to
minimise their scope:

>>> mx = XMLNamespace('mx', 'http://www.adobe.com/2006/mxml')
>>> data = XMLNamespace('data', 'http://www.example.com/data')
>>> app = mx.Application(mx.DataProvider(data.User('Ian')))
>>> makeXml(app)
'<?xml version="1.0"?><mx:Application xmlns:data="http://www.example.com/data" xmlns:mx="http://www.adobe.com/2006/mxml"><mx:DataProvider><data:User>Ian</data:User></mx:DataProvider></mx:Application>'

This, of course, means you can't have identically named namespaces
with different URLs at different points in the document.



How It Works

Tree building works by using XMLNamespace instances (of which the
global 'xml' is one). These namespaces accept any object access (so
xml.title is accepted even though title isn't a predefined property of
xml), returning a new XMLNodeBuilder class.

So when you do:

>>> b = xml.book('My Book')

The xml.book bit returns a brand new class, which you are then
instantiating with 'My Book' as its only __init__ argument. The
instance you get can then be asked to generate its XML with
.getAsXml() (or the .xml property).

>>> b.xml
'<book>My Book</book>'

XMLCreators use this mechanism, but can also interrogate the created
instances to find out what namespaces they use.
"""
from cStringIO import StringIO
import new

class XMLNamespace (object):
    """Represents one name-space used for creating an XML
    document. There is one special namespace defined 'xml'."""

    class XMLNodeBuilderBase (object):
        """A helper class used to create an XML document: the base of
        anything appearing in the XML tree."""

        def __init__(self, *args, **kws):
            """Creates a new builder node. This doesn't need to be
            called from subclasses, as long as __storeChildren is
            called."""

            self._storeChildren(args, kws)

        def _storeChildren(self, args, kws):
            """Finds explicit and implicit children of this node and
            stores them."""
            # Extract explicit children
            if "_" in kws:
                args = list(args) + kws['_']
                del kws['_']

            # Store children for later
            self._children = list(args)

        def getAsXml(self, namespaces={}):
            """Converts the builder into XML, must be implemented in
            subclasses."""
            raise NotImplementedError()
        xml = property(getAsXml)

        def addChildren(self, children):
            """Adds new children to the builder."""
            self._children.extend(children)

        def addChild(self, child):
            """Adds a new child to the builder."""
            self._children.append(children)

        def updateNamespaces(self, namespaces):
            """Adds any additional namespaces to the given dictionary."""
            # Get our children's nodes too
            for child in self._children:
                if isinstance(child, XMLNamespace.XMLNodeBuilderBase):
                    child.updateNamespaces(namespaces)

    class XMLCDATABuilder(XMLNodeBuilderBase):
        """A helper class representing a CDATA block."""
        def getAsXml(self):
            result = StringIO()
            result.write("<![CDATA[")
            for child in self._children:
                result.write(XMLNamespace._getAsXmlOf(child))
            result.write("]]>")
            return result.getvalue()
        xml = property(getAsXml)

    class XMLCommentedCDATABuilder(XMLNodeBuilderBase):
        """A helper class representing a CDATA block for XHTML style
        or script, where its contents are wrapped in a commented CDATA
        tags."""
        def getAsXml(self):
            result = StringIO()
            result.write("/*<![CDATA[*/")
            for child in self._children:
                result.write(XMLNamespace._getAsXmlOf(child))
            result.write("/*]]>*/")
            return result.getvalue()
        xml = property(getAsXml)

    class XMLCommentBuilder(XMLNodeBuilderBase):
        """A helper class representing a CDATA block."""
        def getAsXml(self):
            result = StringIO()
            result.write("<!--")
            for child in self._children:
                result.write(XMLNamespace._getAsXmlOf(child))
            result.write("-->")
            return result.getvalue()
        xml = property(getAsXml)

    class XMLNodeBuilder (XMLNodeBuilderBase):
        """A helper class that is used to create an XML document."""

        def __init__(self, *args, **kws):
            """Creates a new builder node."""
            self._storeChildren(args, kws)

            # Extract explicit properties
            if "__" in kws:
                properties = kws['__']
                del kws['__']
                for key, val in properties.items():
                    kws[key] = val

            if "_empty" in kws:
                self.empty = kws['_empty']
                del kws['_empty']
            else:
                self.empty = True

            # Store attributes for later
            self._attributes = kws

        def getAsXml(self, namespaces={}):
            """Converts the builder into XML."""

            result = StringIO()
            result.write("%s<%s" % (" "*0, self.fullName))

            # Add namespace declarations as attributes
            nsitems = namespaces.items()
            nsitems.sort()
            for kw, val in nsitems:
                result.write(' xmlns:%s="%s"' % (kw, val))

            # Add other keyword arguments as attributes
            for kw, val in self._attributes.items():
                result.write(' %s="%s"' % (kw, val))

            # Finish off the opening tags and create the child nodes
            if self._children:
                result.write(">")
                for arg in self._children:
                    result.write(XMLNamespace._getAsXmlOf(arg))
                result.write("</%s>" % self.fullName)
            elif self.empty:
                result.write("/>")
            else:
                result.write("></%s>" % self.fullName)

            return result.getvalue()
        xml = property(getAsXml)

        def addAttribute(self, key, value):
            """Adds a new attribute to the builder. If the names of
            these attributes match existing attributes, the existing
            values will be overwritten."""
            self._attributes[key] = value

        def addAttributes(self, attributeDict):
            """Adds a new set of attributes to the builder. If the
            names of these attributes match existing attributes, the
            existing values will be overwritten."""
            for key, value in attributeDict:
                self._attributes[key] = value

        def updateNamespaces(self, namespaces):
            """Adds any additional namespaces to the given dictionary."""
            if self.namespace._name not in namespaces:
                self.namespace._addToCollection(namespaces)

            super(XMLNamespace.XMLNodeBuilder, self).updateNamespaces(
                namespaces
                )

    def __init__(self, name=None, uri=None, nodesAllowed=None):
        """Creates a new namespace, with the given set of allowed nodes."""

        self._name = name
        self._uri = uri
        if name and not uri:
            raise ValueError("Can't have a namespace prefix with no uri.")
        elif not name and uri:
            raise ValueError("Can't have a uri without a namespace prefix.")

        # The list of allowed nodes
        self._nodesAllowed = nodesAllowed

    def __getattr__(self, name):
        """Creates and returns a callable object that can create its own
        XML."""

        # Check if we're allowed this node
        if self._nodesAllowed:
            if name not in self._nodesAllowed:
                raise ValueError("Node '%s' isn't allowed in this namespace." %
                                 name)

        # Work out the full name for the new node (including namespace prefix).
        if self._name:
            fullName = "%s:%s" % (self._name, name)
            className = "%s%s" % (self._name.capitalize(), name.capitalize())
        else:
            fullName = name
            className = name.capitalize()

        # Create a custom builder class and return it
        B = new.classobj(
            '%sBuilder' % className,
            (XMLNamespace.XMLNodeBuilder,),
            dict(namespace = self, name = name, fullName = fullName)
            )

        return B

    def __getitem__(self, name):
        """For names that aren't valid python identifiers, this is an
        alternative."""
        return self.__getattr__(name)

    def _addToCollection(self, namespaces):
        """Adds this namespace to the given dictionary."""
        if self._name:
            namespaces[self._name] = self._uri

    def _cdata(self, *args, **kwargs):
        return self.XMLCDATABuilder(*args, **kwargs)

    def _ccdata(self, *args, **kwargs):
        return self.XMLCommentedCDATABuilder(*args, **kwargs)

    def _comment(self, *args, **kwargs):
        return self.XMLCommentBuilder(*args, **kwargs)

    @staticmethod
    def _getAsXmlOf(item):
        """Returns the given item in xml form."""
        try:
            return item.xml
        except AttributeError, err:
            return str(item)



class XMLCreator(object):
    """This is the class that creates XML files."""
    def __init__(self, system=None, public=None, root=None):

        # Force the root node
        self.root = root

        # Create an empty doctype if none is given
        self.systemDTD = system
        self.publicDTD = public

    def __call__(self, rootNode=None, **kws):
        """Creates and returns a new XML document. This should
        eventually use the DOM for construction, but now just creates
        the thing in text."""

        # Check for a valid root node
        if not rootNode:
            raise ValueError("You must specify a root node.")
        elif self.root and rootNode.fullName != self.root:
            raise ValueError(
                "This generator requires '%s' for its root, got '%s'." %
                (self.root, rootNode.fullName)
                )

        # Build the document
        output = StringIO()
        if 'encoding' in kws:
            encodingstr = ' encoding="%s"' % kws['encoding']
        else:
            encodingstr = ''
        if 'standalone' in kws:
            if kws['standalone']: sastr = ' standalone="yes"'
            else: sastr = ' standalone="no"'
        else:
            sastr = ''
        output.write('<?xml version="1.0"%s%s?>' % (encodingstr, sastr))

        # Extract the document type definition elements
        if 'system' in kws:
            systemDTD = kws['system']
        else:
            systemDTD = self.systemDTD
        if 'public' in kws:
            publicDTD = kws['public']
        else:
            publicDTD = self.publicDTD

        # Check if we need to build a doctype declaration
        if systemDTD:
            output.write('<!DOCTYPE %s' % rootNode.fullName)
            if publicDTD:
                output.write(' PUBLIC "%s"' % publicDTD)
                if systemDTD:
                    # We don't need to give the explicit 'SYSTEM'
                    output.write(' "%s"' % systemDTD)
            else:
                output.write(' SYSTEM "%s"' % systemDTD)
            output.write('>')

        # Compile various data from the tree
        namespaces = {}
        rootNode.updateNamespaces(namespaces)

        # Create the content
        output.write(rootNode.getAsXml(namespaces))
        return output.getvalue()

# Create a generic root (unnamed) namespace.
xml = html = XMLNamespace()

# Create a basic XML document type
makeXml = XMLCreator()

# And a basic XHTML document type
makeXhtml = XMLCreator(
    root="html",
    system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
    public="-//W3C//DTD XHTML 1.0 Strict//EN"
    )

if __name__ == '__main__':
    import doctest
    doctest.testmod()