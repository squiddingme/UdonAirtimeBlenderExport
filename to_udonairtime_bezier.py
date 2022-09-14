bl_info = {
    "name": "Export Bezier Curve to UdonAirtime",
    "blender": (2, 80, 0),
    "author": "@squiddingme",
    "location": "File > Export > Bezier Curve to UdonAirtime (.csv)",
    "category": "Import-Export",
}

# references:
# https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html
# https://github.com/qerrant/BezierBlenderToUE/blob/main/ExportBezierToUE.py

import sys, getopt
import os
import bpy
from bpy_extras.io_utils import ExportHelper

class AirtimeExport(bpy.types.Operator, ExportHelper):
    bl_idname = "me.export_udonairtime"
    bl_label = "Export Bezier Curve to UdonAirtime"

    filename_ext = '.csv'
    filter_glob: bpy.props.StringProperty(
        default='*.csv',
        options={'HIDDEN'}
    )

    def execute(self, context):
        if bpy.context.object.type == 'CURVE':
            beziers = []

            for subcurve in bpy.context.active_object.data.splines:
                if subcurve.type == 'BEZIER':
                    beziers.append(subcurve)

            if len(beziers) > 0:
                file = open(self.filepath, "w")

                format_first_str = '%f, %f, %f, %f, %f, %f'
                format_str = ', %f, %f, %f, %f, %f, %f, %f, %f, %f\n'
                format_last_str = ', %f, %f, %f, %f, %f, %f'

                for bezier in beziers:
                    # first entry
                    first_point = bezier.bezier_points[0]
                    line_first = format_first_str % (first_point.co.x, first_point.co.z, first_point.co.y, \
                            first_point.handle_right.x, first_point.handle_right.z, first_point.handle_right.y)
                    file.write(line_first)

                    # loop through points skipping first and last
                    for point in bezier.bezier_points[1:-1]:
                        line = format_str % (point.handle_left.x, point.handle_left.z, point.handle_left.y, \
                            point.co.x, point.co.z, point.co.y, \
                            point.handle_right.x, point.handle_right.z, point.handle_right.y)
                        file.write(line)

                    # last entry
                    last_point = bezier.bezier_points[-1]
                    line_last = format_last_str % (last_point.handle_left.x, last_point.handle_left.z, last_point.handle_left.y, \
                            last_point.co.x, last_point.co.z, last_point.co.y)
                    file.write(line_last)

                file.close()
                self.report({"INFO"}, "Exported to %s" % (self.filepath))
                return {'FINISHED'}
            else:
                self.report({"WARNING"}, "Valid UdonAirtime bezier needs at least two points")
                return {'CANCELLED'}

        else:
            self.report({"WARNING"}, "Selected object is not a bezier curve")
            return {'CANCELLED'}

def menu_func(self, context):
    self.layout.operator(AirtimeExport.bl_idname, text = "Export Bezier Curve to UdonAirtime (.csv)")

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