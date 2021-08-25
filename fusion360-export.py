import adsk.core, adsk.fusion, traceback
import os.path, sys

def export_body(body, output_dir, export_mgr):
    fileName = output_dir + "/" + body.name
    stlExportOptions = export_mgr.createSTLExportOptions(body, fileName)
    stlExportOptions.sendToPrintUtility = False
    export_mgr.execute(stlExportOptions)
    
def make_body_name_prefix(project_name):
    # design name 
    docName = project_name.rsplit(' ',1)[0]

    # make docName camel case
    docName = docName.lower()
    docName = docName.replace(' ', '_')
    docName = docName.replace('-', '_')

    return docName
    
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # get active design        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            ui.messageBox('No active Fusion design', 'No Design')
            return

        
        # get root component in this design
        rootComp = design.rootComponent
        
        # create a single exportManager instance
        exportMgr = design.exportManager
                    
        # get the script location
        scriptDir = os.path.dirname(os.path.realpath(__file__))  

        # export dir
        stlDir = os.path.join(scriptDir, 'stl')

        # create folder if it does not exist
        if not os.path.exists(stlDir):
            os.makedirs(stlDir)

        # make sure the timeline is at the very end
        design.timeline.moveToEnd()
        
        # turn the project name e.g. Pixel Pump v251 into pixel_pump
        name_prefix = make_body_name_prefix(rootComp.name)

        exportedFileCount = 0

        # export the body one by one in the design to a specified file
        for body in rootComp.bRepBodies:
            # check if componentName starts with docName so we only export the components we want
            if body.name.startswith(name_prefix):
                export_body(body, stlDir, exportMgr)
                exportedFileCount += 1


        # export the occurrence one by one in the root component to a specified file
        for i in range(0, rootComp.allOccurrences.count):
            occ = rootComp.allOccurrences.item(i)
            bodies = occ.component.bRepBodies
            for body in bodies:
                if body.name.startswith(name_prefix):
                    export_body(body, stlDir, exportMgr)
                    exportedFileCount += 1



        ui.messageBox('Successfully exported {} STL files'.format(exportedFileCount))
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))