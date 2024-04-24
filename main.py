import Adjacency
import globals
from WaveFunctionCollapse import WaveFunctionCollapse

globals.initialize()

wfc = WaveFunctionCollapse(
    volumeGrid=globals.volumeGrid.to_tuple(),
)


def reinit():
    wfc.collapseVolumeEdgeToAir()
    wfc.collapseRandomCell()


def isValid():
    isAirOnly = set(wfc.getStructuresUsed()).issubset({*Adjacency.getAllRotations('air')})
    return not isAirOnly


attempts = wfc.collapseWithRetry(reinit=reinit)
while not isValid():
    attempts += 1 + wfc.collapseWithRetry(reinit=reinit)
print(f'WFC collapsed after {attempts} attempts')

for building in wfc.getCollapsedState(buildVolumeOffset=globals.buildVolume.offset):
    building.place()


# TODO for Builder class:
#   - can be extended by each building type
#   - has reinit() function for WFC retries
#   - has hasCriteriaMet() validation function (see: brickhouse.py building_criterion_met()
#   - has place() function
