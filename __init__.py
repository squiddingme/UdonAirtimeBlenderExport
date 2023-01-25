bl_info = {
    "name": "Export Bezier Curve to UdonAirtime",
    "blender": (2, 80, 0),
    "author": "@squiddingme",
    "location": "File > Export > Bezier Curve to UdonAirtime (.json)",
    "category": "Import-Export",
}

# references:
# https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html
# https://github.com/qerrant/BezierBlenderToUE/blob/main/ExportBezierToUE.py

if "bpy" in locals():
    from importlib import reload
    if "to_udonairtime_bezier" in locals():
        reload(to_udonairtime_bezier)
else:
    from .to_udonairtime_bezier import *

import bpy

def menu_func(self, context):
    self.layout.operator(AirtimeExport.bl_idname, text = "Bezier Curve to UdonAirtime (.json)", icon = "CURVE_BEZCURVE")

def register():
    bpy.utils.register_class(AirtimeExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(AirtimeExport)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()