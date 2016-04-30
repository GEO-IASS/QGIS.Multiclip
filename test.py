from qgis.core import *
from qgis.utils import *
import time
#input layer and over layer are hard coded for my project, but could be changed to work with other files
#If I ever make a plugin I will query the user for these values
inputLayer = None
overLayer = None
#clipLower and clipUpper are used to iterate throught shapes
clipLower = 0
clipUpper = 1
#baseFilename is also project dependant and should be input by the user if this script is fully implemented
baseFilename = "censusSuClip"
outputFilename = None
#finds two layers by name
for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == "Boundary_SUNIONS_poly":
                overLayer = lyr
                break

for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == "DEMO_BLCK2010_POLY":
                inputLayer = lyr
                break

#creates lists of feature IDs for given layers
iface.setActiveLayer(overLayer)
it = overLayer.getFeatures( QgsFeatureRequest() )
overLayerIds = [i.id() for i in it]
it = inputLayer.getFeatures( QgsFeatureRequest() )
inputLayerIds = [i.id() for i in it]

#selects all of the input feature and one feature from the clip layer
inputLayer.setSelectedFeatures( inputLayerIds )

#changes directory for file outputs (should be input by user) (should creat folder if it doesn't exist)
os.chdir('C:\Users\john.houk\Downloads\GisProject\censusSUclips')
for i in overLayerIds:
    overLayer.setSelectedFeatures( overLayerIds[clipLower:clipUpper] )
    outputFilename = (baseFilename + `clipUpper` + ".shp")
    processing.runalg("qgis:clip", inputLayer, overLayer, outputFilename)
    print i
    clipUpper += 1
    clipLower += 1
    time.sleep(2)

#Clears map canvas selection
mc = iface.mapCanvas()
for layer in mc.layers():
    if layer.type() == layer.VectorLayer:
        layer.removeSelection()
mc.refresh()