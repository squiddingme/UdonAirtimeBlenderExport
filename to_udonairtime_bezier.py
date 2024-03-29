import sys, getopt
import os
import bpy
import math
import json
from bpy_extras.io_utils import ExportHelper

class AirtimeExport(bpy.types.Operator, ExportHelper):
    bl_idname = "me.export_udonairtime"
    bl_label = "Export Bezier Curve to UdonAirtime"

    filename_ext = '.json'
    filter_glob: bpy.props.StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        if not self.filepath:
            blend_filepath = context.blend_data.filepath

            filename = "untitled"
            if bpy.context.object != None:
                filename = bpy.context.object.name

            if context.blend_data.filepath:
                self.filepath = os.path.dirname(context.blend_data.filepath) + "/" + filename + self.filename_ext
            else:
                self.filepath = filename + self.filename_ext

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if bpy.context.object == None:
            self.report({"WARNING"}, "No object selected")
            return {'CANCELLED'}
        elif bpy.context.object.type == 'CURVE':
            curve = bpy.context.active_object.data
            beziers = []

            for subcurve in curve.splines:
                if subcurve.type == 'BEZIER':
                    beziers.append(subcurve)

            if len(beziers) > 0:
                for index, bezier in enumerate(beziers):
                    if index == 0:
                        file = open(self.filepath, "w")
                    else:
                        split = os.path.splitext(self.filepath)
                        file = open("%s.%d%s" % (split[0], index, split[1]), "w")

                    data = {
                        "version": "2.0",
                        "name": bpy.context.object.name,
                        "index": index,
                        "position": [],
                        "points": [],
                        "rolls": [],
                        "modes": [],
                        "loop": bezier.use_cyclic_u
                    }

                    data["position"].extend([-bpy.context.object.location.x, bpy.context.object.location.z, -bpy.context.object.location.y])

                    # first entry
                    first_point = bezier.bezier_points[0]
                    data["points"].extend([-first_point.co.x, first_point.co.z, -first_point.co.y, -first_point.handle_right.x, first_point.handle_right.z, -first_point.handle_right.y])
                    if (curve.twist_mode == "Z_UP" or curve.twist_mode == "MINIMUM"):
                        data["rolls"].append(-(math.degrees(first_point.tilt) - 360))
                    else:
                        data["rolls"].append(0)
                    if first_point.handle_left_type == "ALIGNED" and first_point.handle_right_type == "ALIGNED":
                        data["modes"].append("ALIGNED");
                    else:
                        data["modes"].append("FREE");

                    # loop through points skipping first and last
                    for point in bezier.bezier_points[1:-1]:
                        data["points"].extend([-point.handle_left.x, point.handle_left.z, -point.handle_left.y, -point.co.x, point.co.z, -point.co.y, -point.handle_right.x, point.handle_right.z, -point.handle_right.y])
                        if (curve.twist_mode == "Z_UP" or curve.twist_mode == "MINIMUM"):
                            data["rolls"].append(-(math.degrees(point.tilt) - 360))
                        else:
                            data["rolls"].append(0)
                        if point.handle_left_type == "ALIGNED" and point.handle_right_type == "ALIGNED":
                            data["modes"].append("ALIGNED");
                        else:
                            data["modes"].append("FREE");

                    # last entry
                    last_point = bezier.bezier_points[-1]
                    data["points"].extend([-last_point.handle_left.x, last_point.handle_left.z, -last_point.handle_left.y, -last_point.co.x, last_point.co.z, -last_point.co.y])
                    if (curve.twist_mode == "Z_UP" or curve.twist_mode == "MINIMUM"):
                        data["rolls"].append(-(math.degrees(last_point.tilt) - 360))
                    else:
                        data["rolls"].append(0)
                    if last_point.handle_left_type == "ALIGNED" and last_point.handle_right_type == "ALIGNED":
                        data["modes"].append("ALIGNED");
                    else:
                        data["modes"].append("FREE");

                    # add a few more entries to support udonairtime loops
                    if bezier.use_cyclic_u:
                        data["points"].extend([-last_point.handle_right.x, last_point.handle_right.z, -last_point.handle_right.y])
                        data["points"].extend([-first_point.handle_left.x, first_point.handle_left.z, -first_point.handle_left.y, -first_point.co.x, first_point.co.z, -first_point.co.y])
                        if (curve.twist_mode == "Z_UP" or curve.twist_mode == "MINIMUM"):
                            data["rolls"].append(-(math.degrees(first_point.tilt) - 360))
                        else:
                            data["rolls"].append(0)
                        if first_point.handle_left_type == "ALIGNED" and first_point.handle_right_type == "ALIGNED":
                            data["modes"].append("ALIGNED");
                        else:
                            data["modes"].append("FREE");

                    json.dump(data, file, ensure_ascii=False)

                    file.close()

                self.report({"INFO"}, "Exported to %s" % (self.filepath))
                return {'FINISHED'}
            else:
                self.report({"WARNING"}, "There were no subcurves in selected bezier curve")
                return {'CANCELLED'}

        else:
            self.report({"WARNING"}, "Selected object is not a bezier curve")
            return {'CANCELLED'}