import Adjacency
import globals
from WaveFunctionCollapse import WaveFunctionCollapse

globals.initialize()


wfc = WaveFunctionCollapse(
    volumeGrid=globals.volumeGrid.to_tuple(),
)


def reinit():
    wfc.collapseVolumeEdgeToAir()


def isValid(wfcInstance: WaveFunctionCollapse) -> bool:
    structuresUsed = set(wfcInstance.getStructuresUsed())
    isAirOnly = structuresUsed.issubset({*Adjacency.getAllRotations('air')})
    if isAirOnly:
        print('Invalid WFC result! Volume has only air!')
        return False
    return True


wfc.collapseWithRetry(reinit=reinit, validationFunction=isValid)

for building in wfc.getCollapsedState(buildVolumeOffset=globals.buildVolume.offset):
    building.place()


# TODO for Builder class:
#   - can be extended by each building type
#   - has reinit() function for WFC retries
#   - has hasCriteriaMet() validation function (see: brickhouse.py building_criterion_met()
#   - has place() function
