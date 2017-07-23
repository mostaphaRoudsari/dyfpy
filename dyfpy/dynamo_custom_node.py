"""Dynamo Custom Node.

By: Mostapha Sadeghipour Rousari (mostapha@ladybug.tools)

Collection of classes and methods to create a dynamo custom node from a python
component in Grasshopper.
"""

from xml.dom.minidom import Document
from uuid import uuid4
import os


class Workspace(object):
    """Dynamo Node."""

    VERSION = "1.2.0.2690"
    X = 400
    Y = -100
    ZOOM = 0.4
    CHILDREN = ('namespaceResolutionMap', 'elements', 'connectors', 'notes',
                'annotations', 'presets', 'cameras')

    def __init__(self, name, description, category, subcategory, wsId=None):
        self.name = name
        self.description = description
        self.category = category
        self.subcategory = subcategory
        self.wsId = wsId or uuid4()
        self.__namespaceResolutionMap = []
        self.__elements = []
        self.__connectors = []
        self.__notes = []
        self.__annotations = []
        self.__presets = []
        self.__cameras = []

    @property
    def namespaceResolutionMap(self):
        return self.__namespaceResolutionMap

    @property
    def elements(self):
        """Elements in Dynamo definition"""
        return self.__elements

    def addElement(self, element):
        assert isinstance(element, DynamoNode), \
            '{} is not a DynamoNode!'.format(element)
        self.__elements.append(element)

    @property
    def connectors(self):
        """List of connectors."""
        return self.__connectors

    def addConnector(self, srcNode, targetNode, srcIndex=0, targetIndex=0):
        connection = Connection(srcNode, targetNode, srcIndex, targetIndex)
        self.__connectors.append(connection)

    @property
    def notes(self):
        """List of notes."""
        return self.__notes

    @property
    def annotations(self):
        return self.__annotations

    @property
    def presets(self):
        return self.__presets

    @property
    def cameras(self):
        return self.__cameras

    def addCamera(self, camera):
        assert isinstance(camera, Camera), 'Camera input is not a Camera!'
        self.__cameras.append(camera)

    def toDyf(self):
        doc = Document()
        ws = doc.createElement("Workspace")
        ws.setAttribute("Version", self.VERSION)
        ws.setAttribute("X", str(self.X))
        ws.setAttribute("Y", str(self.Y))
        ws.setAttribute("zoom", str(self.ZOOM))
        ws.setAttribute("Name", self.name)
        ws.setAttribute("Description", self.description)
        ws.setAttribute("ID", str(self.wsId))
        ws.setAttribute("Category", '.'.join((self.category, self.subcategory)))
        doc.appendChild(ws)

        # add child objects
        for child in self.CHILDREN:
            elm = doc.createElement(child[0].upper() + child[1:])
            # get elements for child
            childs = getattr(self, child)
            if len(childs) == 0:
                ws.appendChild(elm)
            for ch in childs:
                # creat the child
                self.addChild(doc, ws, elm, ch)

        text = '\n'.join(doc.toprettyxml(indent="  ").split('\n')[1:])

        doc.unlink()

        return text.replace('&amp;', '&')

    def addChild(self, doc, grandparent, parent, child):
        chElm = doc.createElement(child.type)
        for n, v in child.attr.iteritems():
            chElm.setAttribute(n, v)

        # add text values if any
        if child.text:
            t = doc.createTextNode(child.text)
            chElm.appendChild(t)

        parent.appendChild(chElm)
        grandparent.appendChild(parent)

        for ch in child.children:
            self.addChild(doc, parent, chElm, ch)

    def save(self, path):
        """Save to dyf file."""
        fp = os.path.join(path, self.name + '.dyf')
        with open(fp, 'wb') as outf:
            outf.write(self.toDyf())


class DynamoElement(object):

    TYPE = None

    def __init__(self):
        self.attr = {}
        self.text = None

    @property
    def children(self):
        return []

    @staticmethod
    def toXML(input):
        if isinstance(input, bool):
            return str(input).lower()
        else:
            return str(unicode(input))

    @property
    def type(self):
        return self.TYPE


class Symbol(DynamoElement):

    TYPE = 'Symbol'

    def __init__(self, value):
        DynamoElement.__init__(self)
        self.attr = {'value': self.toXML(value)}


class Script(DynamoElement):
    TYPE = 'Script'

    def __init__(self, code):
        DynamoElement.__init__(self)
        self.text = '\n' + code or ''


class PortInfo(DynamoElement):
    """Output node PortInfo."""

    TYPE = 'PortInfo'

    def __init__(self, index=0, default=False):
        DynamoElement.__init__(self)
        self.attr = {'index': self.toXML(index),
                     'default': self.toXML(default)}


class Connection(DynamoElement):
    """Connection object."""

    TYPE = 'Dynamo.Graph.Connectors.ConnectorModel'

    def __init__(self, srcNode, targetNode, srcIndex=0, targetIndex=0):
        DynamoElement.__init__(self)
        self.attr = {'start': self.toXML(srcNode.nodeId),
                     'start_index': self.toXML(srcIndex),
                     'end': self.toXML(targetNode.nodeId),
                     'end_index': self.toXML(targetIndex),
                     'portType': self.toXML(0)}


class Camera(DynamoElement):

    TYPE = 'Camera'

    def __init__(self, name="Background Preview", eyeX="-34.00", eyeY="-34.00",
                 eyeZ="21.19", lookX="-14.19", lookY="-43.06", lookZ="-41.65",
                 upX="-0.17", upY="0.85", upZ="-0.50"):
        DynamoElement.__init__(self)
        self.name = name
        self.eyeX = str(eyeX)
        self.eyeY = str(eyeY)
        self.eyeZ = str(eyeZ)
        self.lookX = str(lookX)
        self.lookY = str(lookY)
        self.lookZ = str(lookZ)
        self.upX = str(upX)
        self.upY = str(upY)
        self.upZ = str(upZ)

        self.attr = {'Name': self.name,
                     'eyeX': self.eyeX, 'eyeY': self.eyeX, 'eyeZ': self.eyeZ,
                     'lookX': self.lookX, 'lookY': self.lookY, 'lookZ': self.lookZ,
                     'upX': self.upX, 'upY': self.upY, 'upZ': self.upZ
                     }


class DynamoNode(DynamoElement):

    TYPE = 'Dynamo.Graph.Nodes'

    def __init__(self, name=None, x=0, y=0, nodeId=None, isVisible=True,
                 isUpstreamVisible=True, lacing="Disabled", isSelectedInput=True,
                 isFrozen=False, isPinned=False):

        super(DynamoNode, self).__init__()
        name = name or self.__class__.__name__
        self.name = self.toXML(name)
        self.x = self.toXML(x)
        self.y = self.toXML(y)
        nodeId = nodeId or uuid4()
        self.nodeId = self.toXML(nodeId)
        self.isVisible = self.toXML(isVisible)
        self.isUpstreamVisible = self.toXML(isUpstreamVisible)
        self.lacing = self.toXML(lacing)
        self.isSelectedInput = self.toXML(isSelectedInput)
        self.isFrozen = self.toXML(isFrozen)
        self.isPinned = self.toXML(isPinned)

        self.attr = {
            'guid': self.nodeId, 'type': self.TYPE, 'nickname': self.name,
            'x': self.x, 'y': self.y, 'isVisible': self.isVisible,
            'isUpstreamVisible': self.isUpstreamVisible, 'lacing': self.lacing,
            'isSelectedInput': self.isSelectedInput, 'isFrozen': self.isFrozen,
            'isPinned': self.isPinned
        }


class Output(DynamoNode):
    """Dynamo Output Node."""

    TYPE = 'Dynamo.Graph.Nodes.CustomNodes.Output'

    def __init__(self, description=None, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self.description = description

    @property
    def children(self):
        if self.description:
            desc = '\n// '.join(self.description.replace('\r\n', '\n').split('\n'))
            desc = desc.replace('\n', '&#xD;&#xA;')
            v = '// {}&#xD;&#xA;{};'.format(desc, self.name)
        else:
            v = '{};'.format(self.name)
        return (Symbol(v), PortInfo())


class Input(DynamoNode):
    """Dynamo Output Node."""

    TYPE = 'Dynamo.Graph.Nodes.CustomNodes.Symbol'

    __INPUTTYPES = {
        'double': 'double', 'int': 'int', 'string': 'string', 'bool': 'bool',
        'System.Object': 'var', 'GeometryBase': 'Autodesk.Geometry',
        'Vector3d': 'Autodesk.Vector', 'Point3d': 'Autodesk.Point', 'Interval': 'double',
        'Color': 'DSCore.Color', 'Curve': 'Autodesk.Curve'
    }

    _DEFAULTINPUTS = {'Point3d': 'Autodesk.Point.ByCoordinates',
                      'Vector3d': 'Autodesk.Vector.ByCoordinates'}

    def __init__(self, description=None, defaultValue=None, valueType=None,
                 accessType=None, *args, **kwargs):
        super(Input, self).__init__(*args, **kwargs)
        self.description = description
        self.defaultValue = defaultValue
        self.valueType = valueType
        self.accessType = accessType
        if self.name == '_run':
            # in grasshopper boolean can also be set as intger to have more
            # options to run the analysis
            self.valueType = 'bool'

    @property
    def children(self):
        if self.description:
            desc = '\n// '.join(self.description.replace('\r\n', '\n').split('\n'))
            desc = desc.replace('\n', '&#xD;&#xA;')
            v = '// {}&#xD;&#xA;{}'.format(desc, self.name)
        else:
            v = '{}'.format(self.name)

        if self.valueType:
            v = '{}: {}'.format(v, self.matchTypes(self.valueType))

        if self.accessType:
            if self.accessType == 'list' or self.valueType == 'Interval':
                v = '{}[]'.format(v)
            elif self.accessType == 'tree':
                v = '{}[]..[]'.format(v)

        if self.defaultValue is not None:
            if self.valueType == 'string':
                # add double quots
                if self.accessType != 'item':
                    self.defaultValue = \
                        ['&quot;{}&quot;'.format(vv) for vv in self.defaultValue]
                else:
                    self.defaultValue = '&quot;{}&quot;'.format(self.defaultValue)

            if self.accessType and self.accessType != 'item':
                if len(self.defaultValue) == 1:
                    dv = '{%s}' % str(self.defaultValue[0])
                else:
                    dv = str(self.defaultValue) \
                        .replace('(', '{').replace(')', '}') \
                        .replace('[', '{').replace(']', '}')

                v = '{} = {}'.format(v, dv)
            else:
                if self.valueType in self._DEFAULTINPUTS:
                    v = '{} = {}({})'.format(v, self._DEFAULTINPUTS[self.valueType],
                                             self.defaultValue)
                else:
                    v = '{} = {}'.format(v, self.defaultValue)

        elif self.name.endswith('_'):
            # put null as default value
            if self.accessType and self.accessType != 'item':
                v = '{} = {}'.format(v, '{}')
            else:
                v = '{} = {}'.format(v, 'null')

        return (Symbol(v + ';'),)

    def matchTypes(self, t):
        """Match type names from Grasshopper to Dynamo."""
        try:
            return self.__INPUTTYPES[str(t)]
        except KeyError:
            raise ValueError('{} is missing from the tyeps. '
                             'Add it to Input class.'.format(t))


class CodeBlock(DynamoNode):
    TYPE = 'Dynamo.Graph.Nodes.CodeBlockNodeModel'

    def __init__(self, code=None, *args, **kwargs):
        super(CodeBlock, self).__init__(*args, **kwargs)
        if not code:
            code = ''
        else:
            code = '&#xA;'.join('{};'.format(c) for c in code.split('\n'))
        self.attr.update({
            'ShouldFocus': self.toXML(False),
            'CodeText': self.toXML(code)})


class PythonStringNode(DynamoNode):
    TYPE = 'PythonNodeModels.PythonStringNode'

    def __init__(self, inputcount=2, *args, **kwargs):
        super(PythonStringNode, self).__init__(*args, **kwargs)
        self.inputcount = inputcount
        self.attr.update({'inputcount': self.toXML(inputcount)})

    @property
    def children(self):
        return (PortInfo(index=i) for i in range(self.inputcount))


class PythonNode(PythonStringNode):
    TYPE = 'PythonNodeModels.PythonNode'

    def __init__(self, inputcount=1, script=None, *args, **kwargs):
        super(PythonNode, self).__init__(inputcount=inputcount, *args, **kwargs)
        self.script = Script(script)

    @property
    def children(self):
        ch = [PortInfo(index=i) for i in range(self.inputcount)]
        ch.append(self.script)
        return ch


def ghToDs(text):
    """Replace Rhino, Grasshopper with Dynamo."""
    return text.replace('Rhino', 'Dynamo').replace('rhino', 'dynamo') \
        .replace('Grasshopper', 'Dynamo').replace('grasshopper', 'dynamo') \
        .replace('GH', 'DS')


def removePluginName(name):
    remove = ('Ladybug_', 'Honeybee_', 'Butterfly_')
    for r in remove:
        name = name.replace(r, '')
    return name


def nodeFromComponent(component, path, plugin=None, importcode=None, errreportcode=None):
    """Create a node from a ladybug, butterfly, hoenybee grasshopper component."""
    inputs = component.inputs
    outputs = component.outputs
    # sourceCode = component.code

    if not importcode:
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'FINDPACKAGE'))) as f:
            importcode = f.read()

    if not errreportcode:
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'ERRREPORT'))) as f:
            errreportcode = f.read()

    # TODO(): write source code to target folder

    # clean the name
    plugin = plugin or component.name.split('_')[0].replace('Plus', '')
    component.name = removePluginName(component.name)

    node = Workspace(name=component.name, description=component.description,
                     category=component.category, subcategory=component.subcategory)

    node.ZOOM = 0.5
    node.addCamera(Camera())

    # code block to import python file
    cb = CodeBlock(code='"{}"\n"{}_node.py"'.format(plugin, component.nickname.lower()),
                   name='input python script', x=-750, y=390)
    node.addElement(cb)

    # python node to read the code as a string
    importcodepnode = PythonNode(name='import and prepare py code', x=-355, y=385,
                                 script=importcode, inputcount=2)
    node.addElement(importcodepnode)

    # add core python node
    corenode = PythonStringNode(name='core', inputcount=len(inputs) + 1, x=-75,
                                y=460)
    node.addElement(corenode)

    # connect these nodes together
    node.addConnector(cb, importcodepnode)
    node.addConnector(cb, importcodepnode, srcIndex=1, targetIndex=1)
    node.addConnector(importcodepnode, corenode)

    # add inputs for this case I create two input
    for count, inp in enumerate(inputs):
        y = 475 + 95 * count
        inp.description
        inp = Input(name=inp.name, description=ghToDs(inp.description),
                    valueType=inp.valueType, defaultValue=inp.defaultValue,
                    accessType=inp.accessType, x=-750, y=y)
        node.addElement(inp)
        node.addConnector(inp, corenode, targetIndex=count + 1)

    # output separator
    ocb = CodeBlock(code='\n'.join('out[{}]'.format(i) for i in range(len(outputs))),
                    name='decompose outputs', x=150, y=515)
    node.addElement(ocb)
    node.addConnector(corenode, ocb)

    # create output nodes
    for count, out in enumerate(outputs):
        y = 475 + 95 * count
        out = Output(name=out.name, description=ghToDs(out.description), x=380,
                     y=y)
        node.addElement(out)
        node.addConnector(ocb, out, srcIndex=count)

    # add error checking python node
    errpynode = PythonNode(inputcount=2, script=errreportcode, name='Error report',
                           x=150, y=380)
    node.addElement(errpynode)
    node.addConnector(importcodepnode, errpynode, targetIndex=0)
    node.addConnector(corenode, errpynode, targetIndex=1)

    # add err report out node
    errout = Output(name='ERRReport', description='Report', x=380, y=380)
    node.addElement(errout)
    node.addConnector(errpynode, errout)
    print('Converting "{}" from Grasshopper to a Dynamo custom node.'
          .format(component.name))
    node.save(path)
