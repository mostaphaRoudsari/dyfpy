# dyfpy
Python library to automate creating DynamoBIM custom nodes.

Here is a simple example to create a node to add two values. For an advanced example check `nodeFromComponent` method in `dynamo_custom_node.py`

```python
"""Create a simple node that dds number a and number b and returns addition."""

from dyfpy.dynamo_custom_node import Workspace, Camera, PythonNode, Input, Output

path = r'C:\Users\Administrator\AppData\Roaming\Dynamo\Dynamo Core\1.2\definitions'

component = {'name': 'Addition', 'description': 'This node adds two number.',
        'category': 'Core', 'subcategory': 'Math'}

inputs = ({'name': 'a', 'description': 'Number a.', 'defaultValue': 2.1,
           'valueType': 'double', 'accessType': 'item'},
          {'name': 'b', 'description': 'Number b.', 'defaultValue': 3.5,
           'valueType': 'double', 'accessType': 'item'})

output = {'name': 'addition', 'description': 'Addition of a + b.'}

sourceCode = 'a, b = IN\nOUT = a + b'

# initiate the node
node = Workspace(name=component['name'], description=component['description'],
                 category=component['category'], subcategory=component['subcategory'])

node.ZOOM = 0.5

# add a default camera for the background
node.addCamera(Camera())

# python node to read the code as a string
corenode = PythonNode(name=component['name'], x=-450, y=475, script=sourceCode,
                      inputcount=2)
node.addElement(corenode)

# add inputs for this case I create two input
for count, inp in enumerate(inputs):
    y = 475 + 95 * count
    inp = Input(name=inp['name'], description=inp['description'],
                valueType=inp['valueType'], defaultValue=inp['defaultValue'],
                accessType=inp['accessType'], x=-750, y=y)
    node.addElement(inp)
    # connect the input to the python node
    node.addConnector(inp, corenode, srcIndex=0, targetIndex=count)

# create the output node
out = Output(name=output['name'], description=output['description'], x=-240, y=475)
node.addElement(out)
node.addConnector(corenode, out)

print 'Saving the custom node: {}'.format(component['name'])

node.save(path)

```
