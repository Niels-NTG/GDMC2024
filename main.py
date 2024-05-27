import os

import BuilderBase
import globals

os.system('color')

globals.initialize()


BuilderBase.Builder(volume=globals.buildVolume)
