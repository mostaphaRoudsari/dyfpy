"""Grasshopper component wrapper.

By: Mostapha Sadeghipour Rousari (mostapha@ladybug.tools)
"""


class Component(object):

    def __init__(self, name, nickname, description, code, category, subcategory):
        self.name = name
        self.nickname = nickname
        self.description = description
        self.code = code
        self.category = category
        self.subcategory = subcategory
        self.__inputs = []
        self.__outputs = []

    @classmethod
    def fromGHComponent(cls, component):
        cmp = cls(component.Name, component.NickName, component.Description,
                  component.Code, component.Category, component.SubCategory)

        for inp in component.Params.Input:
            cmp.addInput(Input.fromGHPort(inp))

        for out in component.Params.Output:
            if out.Name == 'out':
                continue
            cmp.addOutput(Output.fromGHPort(out))

        return cmp

    @property
    def inputs(self):
        return self.__inputs

    @property
    def outputs(self):
        return self.__outputs

    def addInput(self, inp):
        assert isinstance(inp, Input)
        self.__inputs.append(inp)

    def addOutput(self, out):
        assert isinstance(out, Output)
        self.__outputs.append(out)


class Port(object):

    def __init__(self, name, description=None, defaultValue=None, valueType=None,
                 accessType=None):
        self.name = name
        self.description = description
        self.defaultValue = defaultValue
        self.valueType = valueType
        self.accessType = str(accessType)

    @classmethod
    def fromGHPort(cls, port):
        if hasattr(port, 'TypeHint'):
            # input
            v = port.VolatileData
            if v.IsEmpty:
                value = None
            else:
                value = tuple(str(i.Value).lower() if port.TypeHint.TypeName == 'bool'
                              else i.Value for i in v.AllData(True))

            if value and str(port.Access) == 'item':
                value = value[0]

            return cls(port.Name, port.Description, value, port.TypeHint.TypeName,
                       str(port.Access))
        else:
            # output
            return cls(port.Name, port.Description, None, None, None)


class Input(Port):
    pass


class Output(Port):
    pass
