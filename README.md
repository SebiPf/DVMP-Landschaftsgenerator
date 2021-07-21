# DVMPLandschaftsgenerator
## Quick start guide
  1. Open ``main.blend`` in root directory 
  2. Important: You need to activate an essential Plugin! 
     1. Go unter ``Edit -> Preferences -> Add-ons``
     2. Search "Add Curve: Sapling Tree Gen" and make sure the checkbox is checked
  3. Now go to Script-View and link the ``main.py`` File in root
  4. Start the Script
  5. Now "Generate Landscape" is available under "Add"

## Why not an installable Plugin?
We can install the Plugin under ``Edit -> Preferences -> Add-ons`` but there is a catch. The Textures we depend on can't be accessed with this variant. The relative path can't be resolved.