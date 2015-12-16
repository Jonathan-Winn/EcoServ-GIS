# EcoServ-GIS - This toolbox is an example adapation of the EcoServ-GIS toolkit
# The main toolkit is built in Model Builder
# This python implementation of one of the services (carbon storage) illustrates how the toolkit could also be built with Python Toolboxes
# Most of the service models are considerably more complex than the Carbon storage service, therefore this provides a template example

# Created by Jonathan Winn
# December 2015
# Created with PyScripter and intended for use within ArcGIS 10.2.2 (requires Spatial Analyst licence)

import arcpy
import os
import sys
from arcpy.sa import *
import time

# the Toolbox class should not be renamed

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "EcoServ-GIS: Carbon Storage Toolbox"
        self.alias = "CarbonToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CapacityTool, DemandTool,FlowsTool]


class CapacityTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Capacity Score"
        self.description = "Calculates capacity score "
        self.canRunInBackground = False

    def getParameterInfo(self):


        # set default cell size and extent paramaters first that generally do not change between each service toolbox
        # p0

        p0 = arcpy.Parameter(
            displayName="Cell size and extent",
            name="SAcell",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default cell size and extent" ,
            direction="Input")
        p0.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA010')

        # set default input data files (not all of these data are used by each service model)
        # p1 to p5

        p1 = arcpy.Parameter(
            displayName="BaseMap_FINAL",
            name="basemap",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p1.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'BaseMap_FINAL')

        p2 = arcpy.Parameter(
            displayName="Pop_socioec_points",
            name="popsocioec",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p2.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'Pop_socioec_points')

        p3 = arcpy.Parameter(
            displayName="Study Area",
            name="studyarea",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p3.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'StudyArea')

        p4 = arcpy.Parameter(
            displayName="DTM",
            name="DTM",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p4.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelInputs\ES0CommonFiles\Inputs.gdb', 'DTM')

        p5 = arcpy.Parameter(
            displayName="SA_buffer",
            name="SAbuffer",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p5.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA_buffer')


        # set default data locations -  used by each model
        # p6 to p9


        p6 = arcpy.Parameter(
            displayName="Outputs",
            name="Outputs",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p6.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Outputs.gdb')

        p7 = arcpy.Parameter(
            displayName="Indicators",
            name="Indicators",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p7.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Indicators.gdb')

        p8 = arcpy.Parameter(
            displayName="Scratch",
            name="Scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p8.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Scratch.gdb')

        p9 = arcpy.Parameter(
           displayName="Shapefiles",
            name="Shapefiles",
            datatype="DEFolder",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p9.value =os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Shapefiles')


        # model specific data variables

        # Service name is used as a visual reminder to the user to confirm the servive being calculated.
        # service name is also used by the model to name files

        p10 = arcpy.Parameter(
           displayName="Service Name",
            name="Service",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p10.value = "Carbon"

        p11 = arcpy.Parameter(
            displayName="Data extract area",
            name="Dextract",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        p11.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA_buffer')

        p12 = arcpy.Parameter(
           displayName="Set BaseMap field with per patch values",
            name="ValuesF",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        # Set the filter to accept only fields that are Short or Long type

        p12.value = "TotCarb"
        p12.filter.list = ['Short', 'Long', 'Float', 'Double']
        p12.parameterDependencies = [p1.name]

        p13 = arcpy.Parameter(
           displayName="Set threshold below which to ignore per patch values",
            name="SQLVal",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        p13.value = 0

        # add optional Boolean tick box to give .shp export options
        # p. last

        p14 = arcpy.Parameter(
            displayName="Export shapefiles?",
            name="export",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p14.value =  "true"

        p15 = arcpy.Parameter(
            displayName="Retain intermediate data in Scratch.gdb?",
            name="scratchretain",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p15.value =  "false"

        p16 = arcpy.Parameter(
            displayName="Open and view in ArcMap on completion?",
            name="Aview1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p16.value =  "false"


        # parameter list

        return [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16]


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # name default variables

        SAcell               = parameters[0].valueAsText
        BaseMap              = parameters[1].valueAsText
        Popsocioec           = parameters[2].valueAsText
        StudyA               = parameters[3].valueAsText
        DTM                  = parameters[4].valueAsText
        SAbuffer             = parameters[5].valueAsText

        # name default data locations

        Outputs              = parameters[6].valueAsText
        Indicators           = parameters[7].valueAsText
        Scratch              = parameters[8].valueAsText
        Shapefiles           = parameters[9].valueAsText

        #service name

        Service              = parameters[10].valueAsText

        #service specific variables

        Dextract             = parameters[11].valueAsText
        ValueF               = parameters[12].valueAsText
        SQLVal               = parameters[13].valueAsText

        # boolean tick boxes

        Export               = parameters[14].valueAsText
        DeleteS              = parameters[15].valueAsText
        Aview1               = parameters[16].valueAsText

        # set analysis environment e.g. extent, cell size, snap raster

        ext2                 = arcpy.Describe(SAcell).extent
        arcpy.env.extent     = ext2
        cell1                = parameters[0].valueAsText
        arcpy.env.cellSize   = cell1
        celltext             = arcpy.Describe(cell1).meanCellWidth
        celltext2            = arcpy.GetRasterProperties_management(cell1,property_type="CELLSIZEX")
        arcpy.env.snapRaster = parameters[0].valueAsText

        # set all default local variables used by most models

        Capacity             = (Service + "_Capacity")
        Capacityout          = os.path.join(Outputs,Capacity)
        Capacity0100         = (Service + "_Capacity_0_100")
        Capacity0100out      = os.path.join(Outputs, Capacity0100)

        # set all local variables used in this model analysis

        Study_lyr          = "Study_lyr"
        Dex_lyr            = "Dex_lyr"
        SAB_lyr            = "SAB_lyr"
        ShapeC             = Capacity + ".shp"
        ShapeCout          = os.path.join(Shapefiles, ShapeC)

        # set overwrite and scratch workspace

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = Scratch

        arcpy.CheckOutExtension('Spatial')

        # set total number of analysis steps for messages to update the user

        totalsteps = "8"


        # begin messages for user

        arcpy.AddMessage(" ")
        messages.addMessage("     1 of " + totalsteps + ": Preparing data for analysis")


        # set optional study area and settings based messages, set by model, not by user
        # set to false to speed up model testing

        Viewtests = 'false'

        if Viewtests == 'true':
            messages.addMessage("       Analysis extent set to " + str(ext2))
            messages.addMessage("       Analysis extent taken from " + cell1)
            messages.addMessage("       Analysis cell size set to  " + str(celltext2))
        else :
            messages.addMessage("     ")


        # create messages describing the analysis and study area inputs
        # set to false to speed up model testing

        if Viewtests == 'true':

            count1 = arcpy.GetCount_management(BaseMap)
            count2 = int(count1.getOutput(0))
            messages.addMessage("       BaseMap has " + str(count2) + "  polygons")
            arcpy.Statistics_analysis(BaseMap, "stats_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows = arcpy.SearchCursor("stats_CX")
            for row in rows:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")
                messages.addMessage("       BaseMap covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

            # repeat area analysis for study area

            arcpy.Statistics_analysis(StudyA, "stats2_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats2_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats2_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats2_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats2_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows2 = arcpy.SearchCursor("stats2_CX")
            for row in rows2:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")
                messages.addMessage("       Study area covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

            #repeat area analysis for SA buffer

            arcpy.Statistics_analysis(SAbuffer, "stats3_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats3_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats3_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats3_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats3_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows3 = arcpy.SearchCursor("stats3_CX")
            for row in rows3:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")
                messages.addMessage("       Study area with buffer (SA_buffer) covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )
        else :
            messages.addMessage("     ")


        # first delete existing data
        # even though data overwrite has been set ( arcpy.env.overwriteOutput = True ) models can sometimes crash by failing to overwrite existing data
        # also sometimes fragments of files can persist in the scratch.gdb, e.g. the table part of a raster file
        # therefore all existing files are first deleted

        # first delete from Outputs

        arcpy.env.workspace = Outputs

        delStringCap = "*_Capacity*"
        allCX0 = arcpy.ListRasters(delStringCap)
        for rasterCap in allCX0:
            try:
              arcpy.Delete_management(rasterCap)
            except:
              messages.addMessage ("Can't delete " + str(rasterCap))

        allCXT = arcpy.ListTables(delStringCap)
        for TableCap in allCXT:
             try:
              arcpy.Delete_management(TableCap)
             except:
              messages.addMessage ("Can't delete " + str(TableCap))


        # then delete from Scratch

        arcpy.env.workspace = Scratch
        delStringCX = "*_CX"
        allCX = arcpy.ListRasters(delStringCX)
        for rasterCX in allCX:
             try:
              arcpy.Delete_management(rasterCX)
             except:
              messages.addMessage("Can't delete " + str(rasterCX))

        allCX3 = arcpy.ListTables(delStringCX)
        for TableCX in allCX3:
             try:
              arcpy.Delete_management(TableCX)
             except:
              messages.addMessage("Can't delete " + str(TableCX))

        allCX4 = arcpy.ListFeatureClasses(delStringCX)
        for FeatCX in allCX4:
             try:
              arcpy.Delete_management(FeatCX)
             except:
              messages.addMessage("Can't delete " + str(FeatCX))

        messages.addMessage("     2 of " + totalsteps + ": Existing Capacity data deleted from Scratch.gdb and Outputs.gdb")

        # -----------------------------
        # -----------------------------
        #   begin main model analysis
        # -----------------------------
        # -----------------------------

        SQL4 = (ValueF +" >" + SQLVal)
        arcpy.Select_analysis(BaseMap, "BM_carb_CX",SQL4)
        arcpy.FeatureToRaster_conversion("BM_carb_CX", ValueF, "BM_carb_R_CX")

        if str(celltext2) == '10':
            outTimes = Times("BM_carb_R_CX", 100)
            outTimes.save(os.path.join(Indicators, "Ton_cell_IndC"))
            messages.addMessage("       Per cell Ind values based on 10 m grid cells")
        elif str(celltext2) == '50':
            outTimes = Times("BM_carb_R_CX", 4)
            outTimes.save(os.path.join(Indicators, "Ton_cell_IndC"))
            messages.addMessage("       Per cell Ind values based on 50 m grid cells")
        else :
            messages.addMessage("     Unexpected analysis cell size - check cell size is 10 or 50 m")

        arcpy.MakeFeatureLayer_management(SAbuffer, SAB_lyr)
        outExtractByMask = ExtractByMask(outTimes, SAB_lyr)
        outExtractByMask.save("Testext1_CX")

         # standardising variables

        messages.addMessage("     3 of " + totalsteps + ": Standardising data variables")
        FNvar = "Testext1_CX"
        min1            = arcpy.GetRasterProperties_management(FNvar,property_type="MINIMUM")
        max1            = arcpy.GetRasterProperties_management(FNvar,property_type="MAXIMUM")
        vmin1           = min1.getOutput(0)
        vmax1           = max1.getOutput(0)
        vmin1f          = float(vmin1)
        vmax1f          = float(vmax1)
        VR3             = vmax1f - vmin1f
        VR4              = (99 / VR3)
        VR5              = Minus(FNvar, vmax1f)
        VR6              = Times(VR5, VR4)
        VR7              = Plus(VR6, 99)
        VR7.save(os.path.join(Indicators, "FN_Raw1_100_IndC"))
        VR8 = IsNull(VR7)
        inRaster = VR8
        inTrueRaster = 0
        inFalseConstant = VR7
        whereClause = "VALUE = 1"
        outCon = Con(inRaster, inTrueRaster, inFalseConstant, whereClause)
        outCon.save(os.path.join(Indicators, "FN_Raw_1_100_all_IndC"))

        messages.addMessage("     4 of " + totalsteps + ": Indicator data created")

        arcpy.CopyRaster_management(VR7, Capacityout)
        arcpy.MakeFeatureLayer_management(Dextract, Dex_lyr)
        outExtractByMask2 = ExtractByMask(outCon, Dex_lyr)
        outExtractByMask2.save(Capacity0100out)

        messages.addMessage("     5 of " + totalsteps + ": Capacity data created")
        messages.addMessage("     6 of " + totalsteps + ": Checking data export options")

        if Export == 'true':
            arcpy.AddMessage("       Data simplified to 10 value classes, converted to .shp and exported to  " +str (Shapefiles) )
            outReclassRV2 = Reclassify(Capacityout, "Value", "0.0 0.000001 0; 0.000001 10 10; 10 20 20; 20 30 30; 30 40 40; 40 50 50; 50 60 60; 60 70 70; 70 80 80; 80 90 90; 90 100 100", "NODATA")
            outReclassRV2.save(os.path.join(Scratch, "tmp2_CX"))
            arcpy.RasterToPolygon_conversion("tmp2_CX", ShapeCout, "NO_SIMPLIFY", "VALUE")
        else:
            arcpy.AddMessage("       Shapefiles not exported")

        # -----------------------------
        # -----------------------------
        #   end main model analysis
        # -----------------------------
        # -----------------------------

        # optional delete all files within Scratch workspace

        if DeleteS == 'false':

            arcpy.AddMessage("     7 of " + totalsteps + ": Scratch data deleted")

            delStringCX = "*_CX"
            allCX = arcpy.ListRasters(delStringCX)
            for rasterCX in allCX:
                 try:
                  arcpy.Delete_management(rasterCX)
                 except:
                  messages.addMessage("Can't delete " + str(rasterCX))

            allCX3 = arcpy.ListTables(delStringCX)
            for TableCX in allCX3:
                 try:
                  arcpy.Delete_management(TableCX)
                 except:
                  messages.addMessage("Can't delete " + str(TableCX))

            allCX4 = arcpy.ListFeatureClasses(delStringCX)
            for FeatCX in allCX4:
                 try:
                  arcpy.Delete_management(FeatCX)
                 except:
                  messages.addMessage("Can't delete " + str(FeatCX))
        else:
            arcpy.AddMessage("     7 of " + totalsteps + ": Scratch data not deleted")


        #  message showing user the location of the main data ouputs

        arcpy.AddMessage("     8 of " + totalsteps + ": Completed")
        arcpy.AddMessage("       Output data created within " + str(Outputs))
        arcpy.AddMessage("       Indicator data created within " + str(Indicators))

        # set the relevant ArcMap for this model data

        if Aview1 == 'true':
            map_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),'ArcMaps2aEcosystemServicesMainV07S\ES2CarbonStorage\ES2CarbonStorageCapacity1to100.mxd')
            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Opening data in ArcMap from  " + map_file)

            # make sure the map view is on study area

            mxd = arcpy.mapping.MapDocument(map_file)
            df = arcpy.mapping.ListDataFrames(mxd, "EcoServ-GIS")[0]
            slyr = arcpy.mapping.ListLayers(mxd, "Study Area", df)[0]
            slyrextent = slyr.getExtent()
            df.extent = slyrextent
            arcpy.RefreshActiveView()
            mxd.save()

            # open the file with default application (ArcMap)

            time.sleep(10)  # sleep time in seconds...
            os.startfile(map_file)

        else:
            arcpy.AddMessage(" ")

        arcpy.AddMessage(" ")
        return






































class DemandTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Demand Score"
        self.description = "Calculates demand score"
        self.canRunInBackground = False


    def getParameterInfo(self):

        # set default cell size and extent paramaters first that generally do not change between each service toolbox
        # p0

        p0 = arcpy.Parameter(
            displayName="Cell size and extent",
            name="SAcell",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default cell size and extent" ,
            direction="Input")
        p0.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA010')

        # set default input data files - not all are used by each model
        # p1 to p5

        p1 = arcpy.Parameter(
            displayName="BaseMap_FINAL",
            name="basemap",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p1.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'BaseMap_FINAL')

        p2 = arcpy.Parameter(
            displayName="Pop_socioec_points",
            name="popsocioec",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p2.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'Pop_socioec_points')

        p3 = arcpy.Parameter(
            displayName="Study Area",
            name="studyarea",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p3.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'StudyArea')

        p4 = arcpy.Parameter(
            displayName="DTM",
            name="DTM",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p4.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelInputs\ES0CommonFiles\Inputs.gdb', 'DTM')

        p5 = arcpy.Parameter(
            displayName="SA_buffer",
            name="SAbuffer",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p5.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA_buffer')

        # set default data locations -  used by each model
        # p5 to p9

        p6 = arcpy.Parameter(
            displayName="Outputs",
            name="Outputs",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p6.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Outputs.gdb')

        p7 = arcpy.Parameter(
            displayName="Indicators",
            name="Indicators",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p7.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Indicators.gdb')

        p8 = arcpy.Parameter(
            displayName="Scratch",
            name="Scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p8.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Scratch.gdb')


        p9 = arcpy.Parameter(
           displayName="Shapefiles",
            name="Shapefiles",
            datatype="DEFolder",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p9.value =os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Shapefiles')

        # model specific data variables
        # p9 to p xxxxxx

        p10 = arcpy.Parameter(
           displayName="Service Name",
            name="Service",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p10.value = "Carbon"

        p11 = arcpy.Parameter(
            displayName="Data extract area",
            name="Dextract",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        p11.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA_buffer')

        # add optional Boolean tick box to give .shp export options
        # p. last

        p12 = arcpy.Parameter(
            displayName="Export shapefiles?",
            name="export",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p12.value =  "true"

        p13 = arcpy.Parameter(
            displayName="Retain intermediate data in Scratch.gdb ?",
            name="scratchretain",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p13.value =  "false"

        p14 = arcpy.Parameter(
            displayName="Open and view in ArcMap on completion?",
            name="Aview1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p14.value =  "false"


        # parameter list

        return [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # name default variables

        SAcell             = parameters[0].valueAsText
        BaseMap            = parameters[1].valueAsText
        Popsocioec         = parameters[2].valueAsText
        StudyA             = parameters[3].valueAsText
        DTM                = parameters[4].valueAsText
        SAbuffer           = parameters[5].valueAsText

        # name default data locations

        Outputs            = parameters[6].valueAsText
        Indicators         = parameters[7].valueAsText
        Scratch            = parameters[8].valueAsText
        Shapefiles         = parameters[9].valueAsText

        #service name

        Service           = parameters[10].valueAsText

        #service specific variables

        Dextract            = parameters[11].valueAsText

        # boolean tick boxes

        Export             = parameters[12].valueAsText
        DeleteS             = parameters[13].valueAsText
        Aview1             = parameters[14].valueAsText

        # set analysis environment e.g. extent, cell size, snap raster

        ext2                 = arcpy.Describe(SAcell).extent
        arcpy.env.extent     = ext2
        cell1                = parameters[0].valueAsText
        arcpy.env.cellSize   = cell1
        celltext             = arcpy.Describe(cell1).meanCellWidth
        celltext2            = arcpy.GetRasterProperties_management(cell1,property_type="CELLSIZEX")
        arcpy.env.snapRaster = parameters[0].valueAsText

        # set all default local variables used by most models

        Demand              = (Service + "_Demand")
        Demandout           = os.path.join(Outputs,Demand)
        Demand0100          = (Service + "_Demand_0_100")
        Demand0100out       = os.path.join(Outputs, Demand0100)

        # set all local variables used in this model analysis

        Study_lyr          = "Study_lyr"
        Dex_lyr            = "Dex_lyr"
        ShapeD             = Demand + ".shp"
        ShapeDout          = os.path.join(Shapefiles, ShapeD)

        # set overwrite and scratch workspace

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = Scratch

        arcpy.CheckOutExtension('Spatial')

        # set total number of analysis steps for messages to update the user

        totalsteps = "7"

        # begin messages for user

        messages.addMessage(" ")
        messages.addMessage("     1 of " + totalsteps + ": Preparing data for analysis")

        # set optional study area and settings based messages, set by model, not by user

        Viewtests = 'false'

        if Viewtests == 'true':
            messages.addMessage("       Analysis extent set to " + str(ext2))
            messages.addMessage("       Analysis extent taken from " + cell1)
            messages.addMessage("       Analysis cell size set to  " + str(celltext2))

        else :
            messages.addMessage("     ")


        # create messages describing the analysis and study area inputs

        if Viewtests == 'true':
            count1 = arcpy.GetCount_management(BaseMap)
            count2 = int(count1.getOutput(0))

            messages.addMessage("       BaseMap has " + str(count2) + "  polygons")

            arcpy.Statistics_analysis(BaseMap, "stats_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows = arcpy.SearchCursor("stats_CX")
            for row in rows:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")

                # message to summarise the BaseMap

                messages.addMessage("       BaseMap covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

            arcpy.Statistics_analysis(StudyA, "stats2_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats2_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats2_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats2_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats2_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows2 = arcpy.SearchCursor("stats2_CX")
            for row in rows2:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")

                #do message tp sum Stuy area

                messages.addMessage("       Study area covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )


            arcpy.Statistics_analysis(SAbuffer, "stats3_CX", [["Shape_Area", "SUM"]])
            arcpy.AddField_management("stats3_CX", "Hectares", "Long")
            arcpy.CalculateField_management("stats3_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
            arcpy.AddField_management("stats3_CX", "SqKm", "Long")
            arcpy.CalculateField_management("stats3_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
            rows3 = arcpy.SearchCursor("stats3_CX")
            for row in rows3:
                valueOfField = row.getValue("Hectares")
                valueOfField2 = row.getValue("SqKm")

                #do message to sum SA buffer

                messages.addMessage("       Study area with buffer (SA_buffer) covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

        else :
            messages.addMessage("     ")



        # first delete existing data
        # even though data overwrite has been set ( arcpy.env.overwriteOutput = True ) models can sometimes crash by failing to overwrite existing data
        # also sometimes fragment of files can persist in the scratch.gdb, e.g. the table part of a raster file
        # therefore all existing files are first deleted

        # first delete from Outputs

        arcpy.env.workspace = Outputs

        delStringD = "*_Demand*"
        allCX0 = arcpy.ListRasters(delStringD)
        for rasterCap in allCX0:
            try:
              arcpy.Delete_management(rasterCap)
            except:
              messages.addMessage( "Can't delete " + str(rasterCap))

        allCXT = arcpy.ListTables(delStringD)
        for TableCap in allCXT:
             try:
              arcpy.Delete_management(TableCap)
             except:
              messages.addMessage( "Can't delete " + str(TableCap))


        # then delete from Scratch

        arcpy.env.workspace = Scratch
        delStringDX = "*_DX"
        allDX = arcpy.ListRasters(delStringDX)
        for rasterDX in allDX:
             try:
              arcpy.Delete_management(rasterDX)
             except:
              messages.addMessage("Can't delete " + str(rasterDX))

        allDX3 = arcpy.ListTables(delStringDX)
        for TableDX in allDX3:
             try:
              arcpy.Delete_management(TableDX)
             except:
              messages.addMessage("Can't delete " + str(TableDX))

        allDX4 = arcpy.ListFeatureClasses(delStringDX)
        for FeatDX in allDX4:
             try:
              arcpy.Delete_management(FeatDX)
             except:
              messages.addMessage("Can't delete " + str(FeatDX))

        messages.addMessage("     2 of " + totalsteps + ": Existing Demand data deleted from Scratch.gdb and Outputs.gdb")


        # -----------------------------
        # -----------------------------
        #   begin main model analysis
        # -----------------------------
        # -----------------------------

        out = Plus(cell1, 100)
        arcpy.MakeFeatureLayer_management(Dextract, Dex_lyr)
        outExtractByMask = ExtractByMask(out, Dex_lyr)
        outExtractByMask.save(Demandout)
        arcpy.CopyRaster_management(outExtractByMask, Demand0100out)

        messages.addMessage("     3 of " + totalsteps + ": Demand data created")

         # standardising variables - not used in this model as all is constant

        messages.addMessage("     4 of " + totalsteps + ": Standardising data variables")


        # -----------------------------
        # -----------------------------
        #   end main model analysis
        # -----------------------------
        # -----------------------------


        # messages re data export

        messages.addMessage("     5 of " + totalsteps + ": Checking data export options")

        if Export == 'true':
            arcpy.AddMessage("       Data simplified to 10 value classes, converted to .shp and exported to  " +str (Shapefiles) )
            outReclassRV2 = Reclassify(Demandout, "Value", "0.0 0.000001 0; 0.000001 10 10; 10 20 20; 20 30 30; 30 40 40; 40 50 50; 50 60 60; 60 70 70; 70 80 80; 80 90 90; 90 100 100", "NODATA")
            outReclassRV2.save(os.path.join(Scratch, "tmp2_DX"))
            arcpy.RasterToPolygon_conversion("tmp2_DX", ShapeDout, "NO_SIMPLIFY", "VALUE")
        else:
            arcpy.AddMessage("      Shapefiles not exported")

        # optional delete all files within Scratch workspace

        if DeleteS == 'false':

            delStringDX = "*_DX"
            allDX = arcpy.ListRasters(delStringDX)
            for rasterDX in allDX:
                 try:
                  arcpy.Delete_management(rasterDX)
                 except:
                  messages.addMessage("Can't delete " + str(rasterDX))

            allDX3 = arcpy.ListTables(delStringDX)
            for TableDX in allDX3:
                 try:
                  arcpy.Delete_management(TableDX)
                 except:
                  messages.addMessage("Can't delete " + str(TableDX))

            allDX4 = arcpy.ListFeatureClasses(delStringDX)
            for FeatDX in allDX4:
                 try:
                  arcpy.Delete_management(FeatDX)
                 except:
                  messages.addMessage("Can't delete " + str(FeatDX))

            arcpy.AddMessage("     6 of " + totalsteps + ": Scratch data deleted")

        else:

            arcpy.AddMessage("     6 of " + totalsteps + ": Scratch data not deleted")


        #  message showing user the location of the main data ouputs

        arcpy.AddMessage("     7 of " + totalsteps + ": Completed")
        arcpy.AddMessage("       Output data created within " + str(Outputs))
        arcpy.AddMessage("       Indicator data created within " + str(Indicators))


        # set the relevant ArcMap for this model data - update and hard code this file to match the service in each copy of this model script

        if Aview1 == 'true':
            map_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),'ArcMaps2aEcosystemServicesMainV07S\ES2CarbonStorage\ES2CarbonStorageDemand1to100.mxd')
            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Opening data in ArcMap from  " + map_file)

            # make sure the map view is on study area

            mxd = arcpy.mapping.MapDocument(map_file)
            df = arcpy.mapping.ListDataFrames(mxd, "EcoServ-GIS")[0]
            slyr = arcpy.mapping.ListLayers(mxd, "Study Area", df)[0]
            slyrextent = slyr.getExtent()
            df.extent = slyrextent
            arcpy.RefreshActiveView()
            mxd.save()

            # open the file with default application

            time.sleep(10)  # sleep time in seconds...
            os.startfile(map_file)

        else:
            arcpy.AddMessage(" ")
        arcpy.AddMessage(" ")

        return
























class FlowsTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Flows"
        self.description = "Calculates benefit flows "
        self.canRunInBackground = False

    def getParameterInfo(self):


        # set default cell size and extent paramaters first that generally do not change between each service toolbox
        # p0


        p0 = arcpy.Parameter(
            displayName="Cell size and extent",
            name="SAcell",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default cell size and extent" ,
            direction="Input")
        p0.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA010')

        # set default input data files - not all are used by each model
        # p1 to p4

        p1 = arcpy.Parameter(
            displayName="BaseMap_FINAL",
            name="basemap",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p1.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'BaseMap_FINAL')

        p2 = arcpy.Parameter(
            displayName="Pop_socioec_points",
            name="popsocioec",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p2.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'Pop_socioec_points')

        p3 = arcpy.Parameter(
            displayName="Study Area",
            name="studyarea",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p3.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'StudyArea')

        p4 = arcpy.Parameter(
            displayName="DTM",
            name="DTM",
            datatype="DERasterDataset",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p4.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelInputs\ES0CommonFiles\Inputs.gdb', 'DTM')

        p5 = arcpy.Parameter(
            displayName="SA_buffer",
            name="SAbuffer",
            datatype="DEFeatureClass",
            parameterType="Required",
            category = "Default data inputs",
            direction="Input")
        p5.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'SA_buffer')

        # set default data locations -  used by each model
        # p5 to p8

        p6 = arcpy.Parameter(
            displayName="Outputs",
            name="Outputs",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p6.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Outputs.gdb')

        p7 = arcpy.Parameter(
            displayName="Indicators",
            name="Indicators",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p7.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Indicators.gdb')

        p8 = arcpy.Parameter(
            displayName="Scratch",
            name="Scratch",
            datatype="DEWorkspace",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p8.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Scratch.gdb')

        p9 = arcpy.Parameter(
           displayName="Shapefiles",
            name="Shapefiles",
            datatype="DEFolder",
            parameterType="Required",
            category = "Default data location",
            direction="Input")
        p9.value =os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES2Carbon_storage_regulation\Shapefiles')

        # model specific data variables
        # p9 to p xxxxxx

        p10 = arcpy.Parameter(
           displayName="Service Name",
            name="Service",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p10.value = "Carbon"

        p11 = arcpy.Parameter(
            displayName="Data extract area (flows)",
            name="Dextract",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        p11.value =  os.path.join(os.path.dirname(os.path.dirname(__file__)),'ModelOutputs\ES1BaseMap\Outputs.gdb', 'StudyArea')

        p12 = arcpy.Parameter(
           displayName="Minimum patch size (shapefile conversion)",
            name="SQLexp",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input")
        p12.value = 'Shape_area > 200'
        p12.parameterDependencies = [p1.name]

        # add optional Boolean tick box to give .shp export options
        # p. last

        p13 = arcpy.Parameter(
            displayName="Export shapefiles?",
            name="export",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p13.value =  "true"

        p14 = arcpy.Parameter(
            displayName="Retain intermediate data in Scratch.gdb ?",
            name="scratchretain",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p14.value =  "False"


        p15 = arcpy.Parameter(
            displayName="Use quintiles by Value?",
            name="QValue",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p15.value =  "true"

        p16 = arcpy.Parameter(
            displayName="Use quintiles by Area?",
            name="QArea",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p16.value =  "false"

        p17 = arcpy.Parameter(
           displayName="Value per Service to ID patches with Capacity",
            name="vSQLexp2",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input")
        p17.value = 'TotCarb > 0'
        p17.parameterDependencies = [p1.name]

        p18 = arcpy.Parameter(
            displayName="Run Mask 2?",
            name="Mask2",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p18.value =  "true"

        p19 = arcpy.Parameter(
            displayName="Run Mask 3?",
            name="Mask3",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p19.value =  "false"

        p20 = arcpy.Parameter(
           displayName="Mask 1: Identify areas with management potential (greenspaces and semi-natural habitats)",
            name="SQLMask1",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input")
        p20.value = "NOT HabClass = 'Water' AND NOT HabClass = 'Sea' AND NOT HabClass = 'Urban' AND NOT HabClass = 'Infrastructure'"

        p21 = arcpy.Parameter(
           displayName="Mask 2: Areas with potential for future management (all demand)",
            name="SQLMask2",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input")
        p21.value = "HabClass = 'Urban'"

        p22 = arcpy.Parameter(
           displayName="Mask 3: Areas potentially suitable for future management (Highest or High Demand areas only)",
            name="SQLMask3",
            datatype="GPSQLExpression",
            parameterType="Optional",
            direction="Input")
        p22.value = "HabClass = 'Infrastructure'"

        p23 = arcpy.Parameter(
            displayName="Open and view in ArcMap on completion?",
            name="Aview1",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        p23.value =  "false"

        # parameter list

        return [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23]


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return


    def execute(self, parameters, messages):
        """The source code of the tool."""

        # name default variables
        SAcell             = parameters[0].valueAsText
        BaseMap            = parameters[1].valueAsText
        Popsocioec         = parameters[2].valueAsText
        StudyA             = parameters[3].valueAsText
        DTM                = parameters[4].valueAsText
        SAbuffer           = parameters[5].valueAsText

        # name default data locations
        Outputs            = parameters[6].valueAsText
        Indicators         = parameters[7].valueAsText
        Scratch            = parameters[8].valueAsText
        Shapefiles         = parameters[9].valueAsText

        #service name
        Service            = parameters[10].valueAsText

        #service specific variables

        Dextract           = parameters[11].valueAsText
        SQLexp             = parameters[12].valueAsText

        # boolean tick boxes

        Export             = parameters[13].valueAsText
        DeleteS            = parameters[14].valueAsText
        Qv                 = parameters[15].valueAsText
        Qa                 = parameters[16].valueAsText

        vSQLexp2           = parameters[17].valueAsText

        Mask2              = parameters[18].valueAsText
        Mask3              = parameters[19].valueAsText

        SQLMask1           = parameters[20].valueAsText
        SQLMask2           = parameters[21].valueAsText
        SQLMask3           = parameters[22].valueAsText

        Aview1             = parameters[23].valueAsText

        # set analysis environment e.g. extent, cell size, snap raster

        ext2                 = arcpy.Describe(SAcell).extent
        arcpy.env.extent     = ext2
        cell1                = parameters[0].valueAsText
        arcpy.env.cellSize   = cell1
        celltext             = arcpy.Describe(cell1).meanCellWidth
        celltext2            = arcpy.GetRasterProperties_management(cell1,property_type="CELLSIZEX")
        arcpy.env.snapRaster = parameters[0].valueAsText
        spatial_ref = arcpy.Describe(StudyA).spatialReference

        # set all default local variables used by most models

        Capacity             = (Service + "_Capacity")
        Capacityout          = os.path.join(Outputs,Capacity)
        Capacity0100         = (Service + "_Capacity_0_100")
        Capacity0100out      = os.path.join(Outputs, Capacity0100)

        Demand              = (Service + "_Demand")
        Demandout           = os.path.join(Outputs,Demand)
        Demand0100          = (Service + "_Demand_0_100")
        Demand0100out       = os.path.join(Outputs, Demand0100)

        # set all local variables used in this model analysis

        Study_lyr          = "Study_lyr"
        Dex_lyr            = "Dex_lyr"
        ShapeC             = Capacity + ".shp"
        ShapeD             = Demand + ".shp"
        ShapeCout          = os.path.join(Shapefiles, ShapeC)
        ShapeDout          = os.path.join(Shapefiles, ShapeD)

        DemandAll          = os.path.join(Outputs, (Service + "_Demand_All_One"))
        DemandQArea        = os.path.join(Outputs, (Service + "_Demand_5Quintiles_by_Area"))
        DemandQVal         = os.path.join(Outputs, (Service + "_Demand_5Quintiles_by_Value"))

        CapacityQArea      = os.path.join(Outputs, (Service + "_Capacity_5Quintiles_by_Area"))
        CapacityQVal       = os.path.join(Outputs, (Service + "_Capacity_5Quintiles_by_Value"))

        DQVshapeout         = os.path.join(Shapefiles, (Service + "_shpt_Demand_Quintiles_by_value.shp"))
        DQAshapeout         = os.path.join(Shapefiles, (Service + "_shpt_Demand_Quintiles_by_area.shp"))
        CQVshapeout         = os.path.join(Shapefiles, (Service + "_shpt_Capacity_Quintiles_by_value.shp"))
        CQAshapeout         = os.path.join(Shapefiles, (Service + "_shpt_Capacity_Quintiles_by_area.shp"))

        ESBAPr              = os.path.join(Outputs, (Service + "_ESBA_and_Gaps_Prioritised"))
        ESBA                = os.path.join(Outputs, (Service + "_ESBA_and_Gaps"))
        GIAssets            = os.path.join(Outputs, (Service + "_GI_Assets"))
        MZones              = os.path.join(Outputs, (Service + "_ESBA_Management_Zones_Prioritised"))

        GIshapeout          = os.path.join(Shapefiles, (Service + "_shpt_GI_assets.shp"))
        ESBAPrshapeout      = os.path.join(Shapefiles, (Service + "_shpt_ServiceBenefitingAreas_Prioritised.shp"))
        ESBAshapeout        = os.path.join(Shapefiles, (Service + "_shpt_ServiceBenefitingAreas.shp"))
        MZshapeout          = os.path.join(Shapefiles, (Service + "_shpt_ManagementZones.shp"))

        # set overwrite and scratch workspace

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = Scratch
        arcpy.CheckOutExtension('Spatial')

        # set total number of analysis steps for messages to update the user
        totalsteps = "10"

        # begin messages for user
        arcpy.AddMessage(" ")
        messages.addMessage("     1 of " + totalsteps + ": Preparing data for analysis")

        # set optional study area and settings based messages, set within the script for testing,
        # this is not for use by the tool user

        Viewtests = 'true'

        if Viewtests == 'true':
            messages.addMessage("       Analysis extent set to " + str(ext2))
            messages.addMessage("       Analysis extent taken from " + cell1)
            messages.addMessage("       Analysis cell size set to  " + str(celltext2))
        else :
            messages.addMessage("     ")

        # create messages describing the analysis and study area inputs

        if Viewtests == 'true':
           count1 = arcpy.GetCount_management(BaseMap)
           count2 = int(count1.getOutput(0))
           messages.addMessage("       BaseMap has " + str(count2) + "  polygons")
           arcpy.Statistics_analysis(BaseMap, "stats_CX", [["Shape_Area", "SUM"]])
           arcpy.AddField_management("stats_CX", "Hectares", "Long")
           arcpy.CalculateField_management("stats_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
           arcpy.AddField_management("stats_CX", "SqKm", "Long")
           arcpy.CalculateField_management("stats_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
           rows = arcpy.SearchCursor("stats_CX")
           for row in rows:
             valueOfField = row.getValue("Hectares")
             valueOfField2 = row.getValue("SqKm")
             messages.addMessage("       BaseMap covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

           arcpy.Statistics_analysis(StudyA, "stats2_CX", [["Shape_Area", "SUM"]])
           arcpy.AddField_management("stats2_CX", "Hectares", "Long")
           arcpy.CalculateField_management("stats2_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
           arcpy.AddField_management("stats2_CX", "SqKm", "Long")
           arcpy.CalculateField_management("stats2_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
           rows2 = arcpy.SearchCursor("stats2_CX")
           for row in rows2:
              valueOfField = row.getValue("Hectares")
              valueOfField2 = row.getValue("SqKm")
              messages.addMessage("       Study area covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )

           arcpy.Statistics_analysis(SAbuffer, "stats3_CX", [["Shape_Area", "SUM"]])
           arcpy.AddField_management("stats3_CX", "Hectares", "Long")
           arcpy.CalculateField_management("stats3_CX", "Hectares", ("!SUM_Shape_Area! / 10000"), "PYTHON_9.3")
           arcpy.AddField_management("stats3_CX", "SqKm", "Long")
           arcpy.CalculateField_management("stats3_CX", "SqKm", ("!Hectares! / 100"), "PYTHON_9.3")
           rows3 = arcpy.SearchCursor("stats3_CX")
           for row in rows3:
              valueOfField = row.getValue("Hectares")
              valueOfField2 = row.getValue("SqKm")
              #do message to sum SA buffer
              messages.addMessage("       Study area with buffer (SA_buffer) covers  " + str(valueOfField) + "  hectares or " + str(valueOfField2) + "  square kilometers" )
        else :
            messages.addMessage("     ")


        # -----------------------------
        # -----------------------------
        #   start main model analysis
        # -----------------------------
        # -----------------------------

        # 0 100, capacity analysis

        C0Times = Times(Capacity0100out, 10)
        C0Times.save("Timesc00_FX")
        Cout0Int = Int(C0Times)
        Cout0Int.save("IntTC100_FX")
        arcpy.MakeFeatureLayer_management(Dextract, Dex_lyr)
        outEx00 = ExtractByMask(Cout0Int, Dex_lyr)
        outEx00.save("Ext_capty_0_100_FX")

        # capacity analysis

        CTimes = Times(Capacityout, 10)
        CTimes.save("CTimes_FX")
        CoutInt = Int(CTimes)
        CoutInt.save("CoutInt_FX")
        outExtractByMaskFC1 = ExtractByMask(CoutInt, Dex_lyr)
        outExtractByMaskFC1.save("Cm2_FX")
        attExtractFC1 = ExtractByAttributes(outExtractByMaskFC1, "Value > 0")
        attExtractFC1.save("CExt_FX")

        Cinraster = "CExt_FX"
        numberZones = 5
        baseOutputZone = 1
        slicemethod1 = "EQUAL_AREA"
        slicemethod2 = "EQUAL_INTERVAL"

        # Execute Slice - area

        outSliceC = Slice(Cinraster, numberZones, slicemethod1, baseOutputZone)
        outSliceC.save("Coutslice")
        outSliceC.save(CapacityQArea)

        # Execute Slice - value

        outSliceCv = Slice(Cinraster, numberZones, slicemethod2, baseOutputZone)
        outSliceCv.save(CapacityQVal)

        # Set table variables

        intab = CapacityQArea
        intab2 = CapacityQVal
        fieldName1 = "Category"
        fieldPrecision = ""
        fieldAlias = ""
        fieldLength = ""

        # Execute AddField for  new fields

        arcpy.AddField_management(intab, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.AddField_management(intab2, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        inTable = CapacityQArea
        inTable2 = CapacityQVal
        fieldNamex = "Category"
        expression = "Reclass ( !Category!, !Value!)"
        codeblock = """def Reclass (Category, Value):
  if (Value == 1) :
    return '1. Lowest Capacity Quintile, by Area'
  elif (Value == 2) :
   return '2. Low Capacity Quintile, by Area'
  elif (Value == 3) :
   return '3. Medium Capacity Quintile, by Area'
  elif (Value == 4) :
   return '4. High Capacity Quintile, by Area'
  elif (Value == 5) :
   return '5. Highest Capacity Quintile, by Area'"""
        codeblock2 = """def Reclass (Category, Value):
  if (Value == 1) :
    return '1. Lowest Capacity Quintile, by Value'
  elif (Value == 2) :
   return '2. Low Capacity Quintile, by Value'
  elif (Value == 3) :
   return '3. Medium Capacity Quintile, by Value'
  elif (Value == 4) :
   return '4. High Capacity Quintile, by Value'
  elif (Value == 5) :
   return '5. Highest Capacity Quintile, by Value'"""

        # Execute CalculateField

        arcpy.CalculateField_management(inTable, fieldNamex, expression, "PYTHON_9.3", codeblock)
        arcpy.CalculateField_management(inTable2, fieldNamex, expression, "PYTHON_9.3", codeblock2)

        messages.addMessage("     2 of " + totalsteps + ": Capacity quintiles created")

        # demand analysis

        DTimes = Times(Demandout, 10)
        DTimes.save("DTimes2_FX")
        DoutInt = Int(DTimes)
        DoutInt.save("DoutInt2_FX")
        outExtractByMaskFD1 = ExtractByMask(DoutInt, Dex_lyr)
        outExtractByMaskFD1.save("Dm2_FX")
        attExtractFD1 = ExtractByAttributes(outExtractByMaskFD1, "Value > 0")
        attExtractFD1.save("DExt_FX")

        # save files just for testing and checking

        outTestFD0 = Test(attExtractFD1, "Value > 0 ")
        outTestFD0.save(DemandAll)

        Dinraster = "DExt_FX"

        # Execute Slice - area
        # for those services with constant demand (eg carbon) only one zone is mapped
        # for other service models this needs to be changed to match the method used for capacity data

        outSliceD = Slice(Dinraster, 1, slicemethod1, 5)
        outSliceD.save(DemandQArea)

        # Execute Slice - value
        # for those services with constant demand (eg carbon) only one zone is mapped
        # for other service models this needs to be changed to match the method used for capacity data

        outSliceDv = Slice(Dinraster, 1, slicemethod2, 5)
        outSliceDv.save(DemandQVal)

        # Set table variables

        intabDA = DemandQArea
        intabDV = DemandQVal

        # Execute AddField for  new fields

        arcpy.AddField_management(intabDA, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.AddField_management(intabDV, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        inTableDA = DemandQArea
        inTableDV = DemandQVal
        codeblock3 = """def Reclass (Category, Value):
  if (Value == 1) :
    return '1. Lowest Demand Quintile, by Area'
  elif (Value == 2) :
   return '2. Low Demand Quintile, by Area'
  elif (Value == 3) :
   return '3. Medium Demand Quintile, by Area'
  elif (Value == 4) :
   return '4. High Demand Quintile, by Area'
  elif (Value == 5) :
   return '5. Highest Demand Quintile, by Area'"""
        codeblock4 = """def Reclass (Category, Value):
  if (Value == 1) :
    return '1. Lowest Demand Quintile, by Value'
  elif (Value == 2) :
   return '2. Low Demand Quintile, by Value'
  elif (Value == 3) :
   return '3. Medium Demand Quintile, by Value'
  elif (Value == 4) :
   return '4. High Demand Quintile, by Value'
  elif (Value == 5) :
   return '5. Highest Demand Quintile, by Value'"""


        # Execute CalculateField
        arcpy.CalculateField_management(inTableDA, fieldNamex, expression, "PYTHON_9.3", codeblock3)
        arcpy.CalculateField_management(inTableDV, fieldNamex, expression, "PYTHON_9.3", codeblock4)

        messages.addMessage("     3 of " + totalsteps + ": Demand quintiles created")

        if Qv == 'true':
          CapacityQ = CapacityQVal
          DemandQ = DemandQVal
        elif Qa == 'true':
          CapacityQ = CapacityQArea
          DemandQ = DemandQArea
        else:
           messages.addMessage("     Check that quintiles type has been selected")


          # v1 - select, reclassify variables based on both capacity and demand values

        outTestCapV1 = Test(CapacityQ, "Value = 1 ")
        outTestCapV1.save("Cap1_FX")
        outTestDemV1 = Test(DemandQ, "Value = 1 ")
        outTestDemV1.save("Dem1_FX")
        outTimC1D1 = Times(outTestCapV1, outTestDemV1)
        outTimC1D1.save("Tilowslows_FX")
        attExC1D1 = ExtractByAttributes(outTimC1D1, "Value = 1")
        attExC1D1.save("Exlowslows_FX")
        inRaster = "Exlowslows_FX"
        reclassField = "Value"
        remap = RemapValue([[1, 1000], ["NODATA", 0]])
        outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
        outReclassify.save("R_10kFFLX")

          # v2 - select, reclassify variables based on both capacity and demand values

        outTestCapV2 = Test(CapacityQ, "Value >= 4 ")
        outTestCapV2.save("Cap45_FX")
        outTestDemV2 = Test(DemandQ, "Value >= 4 ")
        outTestDemV2.save("Dem45_FX")
        outTimC2D2 = Times(outTestCapV2, outTestDemV2)
        outTimC2D2.save("TiHighHigh_FX")
        attExC2D2 = ExtractByAttributes(outTimC2D2, "Value = 1")
        attExC2D2.save("ExTiHigh_FX")
        inRaster2 = "ExTiHigh_FX"
        remap2 = RemapValue([[1, 10], ["NODATA", 0]])
        outReclassify2 = Reclassify(inRaster2, reclassField, remap2, "NODATA")
        outReclassify2.save("R_10_FFLX")

          # v3 - select, reclassify variables based on both capacity and demand values

        outTestCapV3 = Test(CapacityQ, "Value <= 2 ")
        outTestCapV3.save("Capqs12_FX")
        outTestDemV3 = Test(DemandQ, "Value = 3 OR Value = 4 ")
        outTestDemV3.save("Dem3or4_FX")
        outTimC3D3 = Times(outTestCapV3, outTestDemV3)
        outTimC3D3.save("c12d34_FX")
        attExC3D3 = ExtractByAttributes(outTimC3D3, "Value = 1")
        attExC3D3.save("exc12d34_FX")
        inRaster3 = "exc12d34_FX"
        remap3 = RemapValue([[1, 6000], ["NODATA", 0]])
        outReclassify3 = Reclassify(inRaster3, reclassField, remap3, "NODATA")
        outReclassify3.save("R_6k_FF")

          # v4 - select, reclassify variables based on both capacity and demand values

        outTestCapV4 = Test(CapacityQ, "Value > 0 ")
        outTestCapV4.save("CapAllZ_FX")
        outTimC4D4 = Times(outTestCapV4, DemandAll)
        outTimC4D4.save("AESBA_FX")
        attExC4D4 = ExtractByAttributes(outTimC4D4, "Value = 1")
        attExC4D4.save("R_1_FFLO")

          # v5 - select, reclassify variables based on both capacity and demand values

        outTestCapV5 = Test(CapacityQ, "Value >= 3 ")
        outTestCapV5.save("Cap345_FX")
        outTestDemV5 = Test(DemandQ, "Value <= 2 ")
        outTestDemV5.save("Dem12_FX")
        outTimC5D5 = Times(outTestCapV5, outTestDemV5)
        outTimC5D5.save("c345d12_FX")
        attExC5D5 = ExtractByAttributes(outTimC5D5, "Value = 1")
        attExC5D5.save("exc345d12_FX")
        inRaster5 = "exc345d12_FX"
        remap5 = RemapValue([[1, 7000], ["NODATA", 0]])
        outReclassify5 = Reclassify(inRaster5, reclassField, remap5, "NODATA")
        outReclassify5.save("R_7k_FF")

          # v6 - select, reclassify variables based on both capacity and demand values

        outTestCapV6 = Test(CapacityQ, "Value <= 2 ")
        outTestCapV6.save("CapQs12_FX")
        outTimC6D6 = Times(outTestCapV6, outTestDemV5)
        outTimC6D6.save("lowlow_FX")
        attExC6D6 = ExtractByAttributes(outTimC6D6, "Value = 1")
        attExC6D6.save("exlowlow_FX")
        inRaster6 = "exlowlow_FX"
        remap6 = RemapValue([[1, 1000], ["NODATA", 0]])
        outReclassify6 = Reclassify(inRaster6, reclassField, remap6, "NODATA")
        outReclassify6.save("R1000_FFLX")

          # v7 - select, reclassify variables based on both capacity and demand values

        outTestDemV7 = Test(DemandQ, "Value = 5 ")
        outTestDemV7.save("Dem5_FX")
        outTimC7D7 = Times(outTestCapV6, outTestDemV7)
        outTimC7D7.save("clowhgdem_FX")
        attExC7D7 = ExtractByAttributes(outTimC7D7, "Value = 1")
        attExC7D7.save("exclowhdem_FX")
        inRaster7 = "exclowhdem_FX"
        remap7 = RemapValue([[1, 5000], ["NODATA", 0]])
        outReclassify7 = Reclassify(inRaster7, reclassField, remap7, "NODATA")
        outReclassify7.save("R_5k_FF")

          # v8 - select, reclassify variables based on both capacity and demand values

        outTestCapV8 = Test(CapacityQ, "Value = 5 ")
        outTestCapV8.save("Cap5_FX")
        outTimC8D8 = Times(outTestCapV8, outTestDemV7)
        outTimC8D8.save("chghhgdem_FX")
        attExC8D8 = ExtractByAttributes(outTimC8D8, "Value = 1")
        attExC8D8.save("exchgdhgh_FX")
        inRaster8 = "exchgdhgh_FX"
        remap8 = RemapValue([[1, 100], ["NODATA", 0]])
        outReclassify8 = Reclassify(inRaster8, reclassField, remap8, "NODATA")
        outReclassify8.save("R_100_FFLX")

          # v9 - select, reclassify variables based on both capacity and demand values

        outTestCapV9 = Test(outEx00, "Value = 0 ")
        outTestCapV9.save("Capis0_FX")
        outTimC9D9 = Times(outTestCapV9, DemandAll)
        outTimC9D9.save("B_Gap_FX")
        attExC9D9 = ExtractByAttributes(outTimC9D9, "Value = 1")
        attExC9D9.save("exBgap_FX")
        inRaster9 = "exBgap_FX"
        remap9 = RemapValue([[1, 9], ["NODATA", 0]])
        outReclassify9 = Reclassify(inRaster9, reclassField, remap9, "NODATA")
        outReclassify9.save("R_2_FFLO")

          # v10 - select, reclassify variables based on both capacity and demand values

        outTestDemV10 = Test(DemandQ, "Value <= 3 ")
        outTestDemV10.save("Dem123_FX")
        outTimC10D10 = Times(outTestCapV9, outTestDemV10)
        outTimC10D10.save("Gaplowdm_FX")
        attExC10D10 = ExtractByAttributes(outTimC10D10, "Value = 1")
        attExC10D10.save("exGaplowdm_FX")
        inRaster10 = "exGaplowdm_FX"
        remap10 = RemapValue([[1, 60], ["NODATA", 0]])
        outReclassify10 = Reclassify(inRaster10, reclassField, remap10, "NODATA")
        outReclassify10.save("R_60_FFLX")

          # v11 - select, reclassify variables based on both capacity and demand values

        outTimC11D11 = Times(outTestCapV9, outTestDemV7)
        outTimC11D11.save("Gaphighdm_FX")
        attExC11D11 = ExtractByAttributes(outTimC10D10, "Value = 1")
        attExC11D11.save("exGaphighdm_FX")
        inRaster11 = "exGaphighdm_FX"
        remap11 = RemapValue([[1, 30], ["NODATA", 0]])
        outReclassify11 = Reclassify(inRaster11, reclassField, remap11, "NODATA")
        outReclassify11.save("R_30_FFLX")

        messages.addMessage("     4 of " + totalsteps + ": Overlaying Capacity and Demand Qunintiles")

        # combine the seperate raster to create on ESBA prioritised and ESBA main raster

        in1cell = arcpy.ListRasters("*FFL*")
        EScell = CellStatistics([in1cell], "SUM", "DATA")
        EScellint = Int(EScell)
        EScellint.save("temprty_FX")
        in2cell = arcpy.ListRasters("*_FFLO*")
        ES2cell = CellStatistics([in2cell], "SUM", "DATA")
        ES2cellint = Int(ES2cell)
        ES2cellint.save(ESBA)

        # Set table variables
        # note that an alternative method was required to deal with ESBPr saved to the .gdb
        # because two files have similar filenames and start with the same letter and this causes ArcGIS to crash when attempting
        # to open the table to add the fields

        intabepr = "temprty_FX"
        intabe = ESBA

        # Execute AddField for  new fields

        arcpy.AddField_management(intabepr, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        arcpy.AddField_management(intabe, fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")
        fieldNamex = "Category"
        expression = "Reclass ( !Category!, !Value!)"
        codeblockep = """def Reclass (Category, Value):
  if (Value == 1) :
    return 'A3. Intermediate'
  elif (Value == 11) :
    return 'A2. High'
  elif (Value == 111) :
    return 'A1. Highest'
  elif (Value == 1001) :
    return 'A4. Low'
  elif (Value == 11001) :
    return 'A5. Lowest'

  elif (Value == 39) :
    return 'B1. None: Highest Demand'
  elif (Value == 9) :
   return 'B2. None: High Demand'
  elif (Value == 69) :
   return 'B3. None: Int+Low Demand'

  elif (Value == 808) :
    return 'C1. Restricted: Highest Demand'
  elif (Value == 8) :
    return 'C2. Restricted: High Demand'
  elif (Value == 88) :
    return 'C3. Restricted: Int+Low Demand'"""

        codeblockes = """def Reclass (Category, Value):
  if (Value == 1) :
    return 'A. ESBA: Potential benefits'

  elif (Value == 9) :
   return 'B. No benefits: Service Gap'

  elif (Value == 8) :
   return 'C. Restricted Service'"""

        arcpy.CalculateField_management(intabepr, fieldNamex, expression, "PYTHON_9.3",codeblockep)
        arcpy.CalculateField_management(intabe, fieldNamex, expression, "PYTHON_9.3", codeblockes)
        arcpy.CopyRaster_management("temprty_FX", ESBAPr)

        messages.addMessage("     5 of " + totalsteps + ": ESBA and ESBA Prioritised data created")

        # create GI assets data

        sel1 = "HabClass NOT LIKE 'Infrastructure' AND HabClass NOT LIKE 'Unclassified' AND HabClass NOT LIKE 'Urban'"
        arcpy.MakeFeatureLayer_management(BaseMap, "B1_lyr", sel1)
        arcpy.MakeFeatureLayer_management("B1_lyr", "B2_lyr", vSQLexp2 )
        assignmentType = "MAXIMUM_COMBINED_AREA"
        priorityField = ""
        cellsize = celltext2
        arcpy.PolygonToRaster_conversion("B2_lyr", "Constant1", "NSpaces_FX", assignmentType, priorityField, cellsize)
        attExf1 = ExtractByAttributes(ESBA, "VALUE = 1")
        outExf2 = ExtractByMask(Capacityout, attExf1)
        outExf3 = ExtractByMask(outExf2, "NSpaces_FX")
        outExf3.save(GIAssets)

        messages.addMessage("     6 of " + totalsteps + ": GI_Assets data created")

        # combine the seperate raster to create the Management Zones raster

        inMcell = arcpy.ListRasters("*_FF*")
        ESMcell = CellStatistics([inMcell], "SUM", "DATA")
        ESMcellint = Int(ESMcell)
        ESMcellint.save("MZs_FX")

        # conduct the Mask analysis

        arcpy.MakeFeatureLayer_management(BaseMap, "Bmsk1_lyr", SQLMask1)
        arcpy.MakeFeatureLayer_management(BaseMap, "Bmsk2_lyr", SQLMask2)
        arcpy.MakeFeatureLayer_management(BaseMap, "Bmsk3_lyr", SQLMask3)

        arcpy.PolygonToRaster_conversion("Bmsk1_lyr", "Constant1", "B1msk_MKL_FX", assignmentType, priorityField, cellsize)
        arcpy.PolygonToRaster_conversion("Bmsk2_lyr", "Constant1", "B2msk_FX", assignmentType, priorityField, cellsize)
        arcpy.PolygonToRaster_conversion("Bmsk3_lyr", "Constant1", "B3msk_FX", assignmentType, priorityField, cellsize)

        outM2Times = Times("B2msk_FX", 2)
        outM2Times.save("B2msk_MKL_FX")
        outM3Times = Times("B3msk_FX", 3)
        outM3Times.save("B3msk_MKL_FX")

        inMSKcell = arcpy.ListRasters("*MKL*")
        ESMSKcell = CellStatistics([inMSKcell], "MAXIMUM", "DATA")
        outM4Times = Times("MZs_FX", ESMSKcell)
        outM4Times.save("MZout_FX")

        # Execute AddField for  new fields

        intabmsk = "MZout_FX"
        arcpy.AddField_management(intabmsk,fieldName1, "TEXT", fieldPrecision, "", "", fieldAlias, "NULLABLE")

        fieldNamex = "Category"
        expression = "Reclass ( !Category!, !Value!)"
        codeblockMSK = """def Reclass (Category, Value):
  if (Value == 1) :
    return 'A3. Maintain'
  elif (Value == 11) :
    return 'A2. Protect / Maintain'
  elif (Value == 111) :
    return 'A1. Protect'
  elif (Value == 1001) or (Value == 69):
    return 'A7. Assess'
  elif (Value == 5001):
    return 'A4. Improve'
  elif (Value == 39):
    return 'A8. Change habitat type: Highest Demand'

  elif (Value == 6001):
    return 'A5. Maintain / Improve'
  elif (Value == 7001) :
    return 'A6. Maintain / Assess'
  elif (Value == 9) :
    return 'A9. Change habitat type: High Demand'

  elif (Value == 222) or (Value == 333) or (Value == 10002) or (Value == 15003) or (Value == 78) or (Value == 117) :
    return 'B1. Create: Highest Demand'
  elif (Value == 22) or (Value == 33) or (Value == 12002) or (Value == 18003) or (Value == 18) or (Value == 27):
   return 'B2. Create: High Demand'
  elif (Value == 138) or (Value == 2)  or (Value == 14002):
   return 'B3. Create: Int+Low Demand'

  elif (Value == 808) :
    return 'C1. Provide access: Highest Demand'
  elif (Value == 8) :
    return 'C2. Provide access: High Demand'
  elif (Value == 88) :
    return 'C3. Provide access: Int+Low Demand'

  elif (Value == 3)  or (Value == 21003) or (Value == 2002) or (Value == 3003) or (Value == 207) :
    return 'D. No management'

  else:
    return 'D. None'"""

        arcpy.CalculateField_management("MZout_FX", fieldNamex, expression, "PYTHON_9.3", codeblockMSK)
        arcpy.CopyRaster_management("MZout_FX", MZones)

        messages.addMessage("     7 of " + totalsteps + ": Management Zones data created")

        messages.addMessage("     8 of " + totalsteps + ": Checking data export options")

        # -----------------------------
        # -----------------------------
        #   end main model analysis
        # -----------------------------
        # -----------------------------

        if Export == 'true':

            arcpy.RasterToPolygon_conversion(DemandQVal, "DemQval_FX", "NO_SIMPLIFY", "VALUE")
            arcpy.MakeFeatureLayer_management("DemQval_FX", "DemQval_lyr", SQLexp)
            arcpy.CopyFeatures_management("DemQval_lyr", DQVshapeout)

            arcpy.RasterToPolygon_conversion(DemandQArea, "DemQarea_FX", "NO_SIMPLIFY", "VALUE")
            arcpy.MakeFeatureLayer_management("DemQarea_FX", "DemQarea_lyr", SQLexp)
            arcpy.CopyFeatures_management("DemQarea_lyr", DQAshapeout)

            arcpy.RasterToPolygon_conversion(CapacityQVal, "CapQval_FX", "NO_SIMPLIFY", "VALUE")
            arcpy.MakeFeatureLayer_management("CapQval_FX", "CapQval_lyr", SQLexp)
            arcpy.CopyFeatures_management("CapQval_lyr", CQVshapeout)

            arcpy.RasterToPolygon_conversion(CapacityQArea, "CapQarea_FX", "NO_SIMPLIFY", "VALUE")
            arcpy.MakeFeatureLayer_management("CapQarea_FX", "CapQarea_lyr", SQLexp)
            arcpy.CopyFeatures_management("CapQarea_lyr", CQAshapeout)

            arcpy.AddMessage("       Quintiles data  converted to .shp and exported to  " +str (Shapefiles) )

             # then also export gi assets, esaba and man zones

            remap2 = "0.0 0.000001 0; 0.000001 10 10; 10 20 20; 20 30 30; 30 40 40; 40 50 50; 50 60 60; 60 70 70; 70 80 80; 80 90 90; 90 100 100"
            outGIRec = Reclassify(GIAssets, "Value", remap2, "NODATA")
            arcpy.RasterToPolygon_conversion(outGIRec, "Giconv_FX", "NO_SIMPLIFY", "VALUE")
            arcpy.MakeFeatureLayer_management("Giconv_FX", "Gi_lyr", SQLexp)
            arcpy.CopyFeatures_management("Gi_lyr", GIshapeout)

            arcpy.AddMessage("       GI_Assets data  converted to .shp and exported to  " +str (Shapefiles) )

            arcpy.RasterToPolygon_conversion(ESBA, "ESBAcv_FX", "NO_SIMPLIFY", "Category")
            arcpy.MakeFeatureLayer_management("ESBAcv_FX", "EScv_lyr", SQLexp)
            arcpy.CopyFeatures_management("EScv_lyr", ESBAshapeout)

            arcpy.RasterToPolygon_conversion(ESBAPr, "ESBApr_FX", "NO_SIMPLIFY", "Category")
            arcpy.MakeFeatureLayer_management("ESBApr_FX", "ESpr_lyr", SQLexp)
            arcpy.CopyFeatures_management("ESpr_lyr", ESBAPrshapeout)

            arcpy.AddMessage("       ESBA and ESBA Prioritised converted to .shp and exported to  " +str (Shapefiles) )

            arcpy.RasterToPolygon_conversion(MZones, "mz33_FX", "NO_SIMPLIFY", "Category")
            arcpy.MakeFeatureLayer_management("mz33_FX", "mz_lyr", SQLexp)
            arcpy.CopyFeatures_management("mz_lyr", MZshapeout)

            arcpy.AddMessage("       Management Zones converted to .shp and exported to  " +str (Shapefiles) )

        else:
            arcpy.AddMessage("       Shapefiles not exported")


        # optional delete all files within Scratch workspace

        if DeleteS == 'false':
            arcpy.AddMessage("    9 of " + totalsteps + ": Scratch data deleted")

            delString = "*_FX"
            allFcSet = set(arcpy.ListRasters(delString))
            for raster in allFcSet:
             try:
              arcpy.Delete_management(raster)
             except:
              print "Can't delete " + str(raster)

        else:
            arcpy.AddMessage("      9 of " + totalsteps + ": Scratch data not deleted")


        # final message showing user the location of the main data ouputs

        arcpy.AddMessage("     10 of " + totalsteps + "Completed")
        arcpy.AddMessage("       Output data created within " + str(Outputs))
        arcpy.AddMessage("       Indicator data created within " + str(Indicators))
        arcpy.AddMessage(" ")

        # set the relevant ArcMap for this model data - update and hard code this file to match the service in each copy of this model script

        if Aview1 == 'true':
            map_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),'ArcMaps2aEcosystemServicesMainV07S\ES2CarbonStorage\ES2CarbonStorageESBAManagementZones.mxd')
            arcpy.AddMessage(" ")
            arcpy.AddMessage("    Opening data in ArcMap from  " + map_file)

            # make sure the map view is on study area

            mxd = arcpy.mapping.MapDocument(map_file)
            df = arcpy.mapping.ListDataFrames(mxd, "EcoServ-GIS")[0]
            slyr = arcpy.mapping.ListLayers(mxd, "Study Area", df)[0]
            slyrextent = slyr.getExtent()
            df.extent = slyrextent
            arcpy.RefreshActiveView()
            mxd.save()

            # open the file with default application (ArcMap)

            time.sleep(10)  # sleep time in seconds...
            os.startfile(map_file)

        else:
            arcpy.AddMessage(" ")
        arcpy.AddMessage(" ")

        return



