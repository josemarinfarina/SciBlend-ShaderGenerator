import bpy
import json
from bpy.props import (
    EnumProperty,
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    FloatProperty,
    CollectionProperty
)
from bpy.types import Operator, Panel, PropertyGroup

bl_info = {
    "name": "Shader Generator",
    "author": "José Marín",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Shader Generator",
    "description": "Create materials with scientific colormaps and custom ColorRamps",
    "category": "Material",
}

# Definición de colormaps científicos
COLORMAPS = {
    'viridis': [(68, 1, 84), (72, 40, 120), (62, 74, 137), (49, 104, 142), (38, 130, 142), (31, 158, 137), (53, 183, 121), (109, 205, 89), (180, 222, 44), (253, 231, 37)],
    'plasma': [(13, 8, 135), (75, 3, 161), (125, 3, 168), (168, 4, 168), (203, 11, 157), (231, 41, 138), (251, 85, 108), (254, 136, 68), (243, 188, 40), (240, 249, 33)],
    'inferno': [(0, 0, 4), (40, 11, 84), (101, 21, 110), (159, 42, 99), (212, 72, 66), (245, 125, 21), (250, 193, 39), (252, 255, 164)],
    'magma': [(0, 0, 4), (28, 16, 68), (79, 47, 101), (129, 63, 109), (181, 82, 113), (229, 107, 97), (251, 170, 96), (253, 239, 154)],
    'cividis': [(0, 32, 76), (0, 42, 102), (0, 52, 110), (9, 64, 121), (25, 79, 127), (49, 96, 130), (77, 114, 132), (108, 133, 133), (142, 151, 136), (178, 170, 140), (217, 189, 143), (254, 212, 146)],
    'jet': [(0, 0, 143), (0, 0, 255), (0, 127, 255), (0, 255, 255), (127, 255, 127), (255, 255, 0), (255, 127, 0), (255, 0, 0), (127, 0, 0)],
    'rainbow': [(150, 0, 90), (0, 0, 200), (0, 25, 255), (0, 152, 255), (44, 255, 150), (151, 255, 0), (255, 234, 0), (255, 111, 0), (255, 0, 0)],
    'turbo': [(48, 18, 59), (86, 67, 140), (66, 110, 193), (51, 150, 211), (53, 183, 200), (80, 211, 163), (133, 231, 109), (202, 237, 56), (253, 217, 0), (249, 168, 0), (227, 112, 1), (186, 56, 0), (131, 21, 13)],
    'coolwarm': [(59, 76, 192), (124, 159, 249), (192, 212, 245), (242, 241, 239), (245, 210, 193), (245, 156, 126), (180, 37, 23)],
    'spectral': [(158, 1, 66), (213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189), (94, 79, 162)],
    'RdYlBu': [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (255, 255, 191), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180), (49, 54, 149)],
    'seismic': [(0, 0, 76), (0, 0, 253), (255, 255, 255), (253, 0, 0), (128, 0, 0)],
}

INTERPOLATION_OPTIONS = [
    ('CONSTANT', "Constant", "No interpolation"),
    ('LINEAR', "Linear", "Linear interpolation"),
    ('EASE', "Ease", "Easing interpolation"),
    ('CARDINAL', "Cardinal", "Cardinal interpolation"),
    ('B_SPLINE', "B-Spline", "B-Spline interpolation"),
]


class ColorRampColor(PropertyGroup):
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        description="Color of the ColorRamp stop"
    )
    position: FloatProperty(
        name="Position",
        default=0.5,
        min=0.0,
        max=1.0,
        description="Position of the color stop"
    )


class COLORRAMP_OT_add_color(Operator):
    bl_idname = "colorramp.add_color"
    bl_label = "Add Color"
    bl_description = "Add a new color to the custom ColorRamp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        custom_ramp = context.scene.custom_colorramp
        new_color = custom_ramp.add()
        new_color.position = len(custom_ramp) / (len(custom_ramp) + 1)
        return {'FINISHED'}


class COLORRAMP_OT_remove_color(Operator):
    bl_idname = "colorramp.remove_color"
    bl_label = "Remove Color"
    bl_description = "Remove the last color from the custom ColorRamp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        custom_ramp = context.scene.custom_colorramp
        if len(custom_ramp) > 2:
            custom_ramp.remove(len(custom_ramp) - 1)
        return {'FINISHED'}


class COLORRAMP_OT_save_custom(Operator):
    bl_idname = "colorramp.save_custom"
    bl_label = "Save Custom ColorRamp"
    bl_description = "Save the current custom ColorRamp"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        custom_ramp = context.scene.custom_colorramp
        data = [{"color": list(c.color) + [1.0], "position": c.position}
                for c in custom_ramp]
        with open(self.filepath, 'w') as f:
            json.dump(data, f)
        self.report({'INFO'}, f"ColorRamp saved to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = "custom_colorramp.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class COLORRAMP_OT_load_custom(Operator):
    bl_idname = "colorramp.load_custom"
    bl_label = "Load Custom ColorRamp"
    bl_description = "Load a custom ColorRamp"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        with open(self.filepath, 'r') as f:
            data = json.load(f)

        custom_ramp = context.scene.custom_colorramp
        custom_ramp.clear()
        for item in data:
            new_color = custom_ramp.add()
            # Solo tomamos RGB, ignoramos Alpha
            new_color.color = item['color'][:3]
            new_color.position = item['position']

        self.report({'INFO'}, f"ColorRamp loaded from {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def create_colormap_material(colormap_name, interpolation, custom_colormap=None):
    mat = bpy.data.materials.new(name=f"Shader_Generator_{colormap_name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    node_attrib = nodes.new(type='ShaderNodeAttribute')
    node_attrib.attribute_name = "Col"

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.interpolation = interpolation

    if custom_colormap:
        colors = custom_colormap
    else:
        colors = COLORMAPS[colormap_name]

    color_ramp = node_ramp.color_ramp
    color_ramp.elements.remove(color_ramp.elements[0])
    for i, color_data in enumerate(colors):
        elem = color_ramp.elements.new(
            color_data['position'] if custom_colormap else i / (len(colors) - 1))
        if custom_colormap:
            color = list(color_data['color'])
            if len(color) == 3:
                color.append(1.0)  # Añadir alpha = 1.0 si no está presente
            elem.color = color
        else:
            elem.color = [c/255 for c in color_data] + [1]

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')

    links.new(node_attrib.outputs[0], node_ramp.inputs[0])
    links.new(node_ramp.outputs[0], node_bsdf.inputs[0])
    links.new(node_bsdf.outputs[0], node_output.inputs[0])

    return mat


class MATERIAL_OT_create_shader(Operator):
    bl_idname = "material.create_shader"
    bl_label = "Create and Apply Shader"
    bl_options = {'REGISTER', 'UNDO'}

    colormap: EnumProperty(
        items=[(k, k, "") for k in COLORMAPS.keys()] +
        [('CUSTOM', "Custom", "Use custom ColorRamp")],
        name="ColorMap",
        description="Choose a scientific colormap or use custom",
        default='viridis'
    )

    interpolation: EnumProperty(
        items=INTERPOLATION_OPTIONS,
        name="Interpolation",
        description="Choose the interpolation method for the ColorRamp",
        default='LINEAR'
    )

    material_name: StringProperty(
        name="Material Name",
        default="Shader_Generator",
        description="Name of the new material"
    )

    apply_to_all: BoolProperty(
        name="Apply to All Mesh Objects",
        default=True,
        description="Apply the material to all mesh objects in the scene"
    )

    def execute(self, context):
        if self.colormap == 'CUSTOM':
            custom_colormap = [{"color": list(
                c.color), "position": c.position} for c in context.scene.custom_colorramp]
            mat = create_colormap_material(
                'Custom', self.interpolation, custom_colormap)
        else:
            mat = create_colormap_material(self.colormap, self.interpolation)

        mat.name = self.material_name

        if self.apply_to_all:
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    if obj.data.materials:
                        obj.data.materials[0] = mat
                    else:
                        obj.data.materials.append(mat)
        else:
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    if obj.data.materials:
                        obj.data.materials[0] = mat
                    else:
                        obj.data.materials.append(mat)

        self.report({'INFO'}, f"Applied {'custom' if self.colormap == 'CUSTOM' else self.colormap} shader with {self.interpolation} interpolation to {'all mesh objects' if self.apply_to_all else 'selected objects'}")
        return {'FINISHED'}


class MATERIAL_PT_shader_generator(Panel):
    bl_label = "Shader Generator"
    bl_idname = "MATERIAL_PT_shader_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Shader Generator'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Sección para la creación de shaders
        layout.label(text="Create Shader", icon='NODE_MATERIAL')
        box = layout.box()
        col = box.column(align=True)

        op = col.operator(MATERIAL_OT_create_shader.bl_idname,
                          text="Generate Shader", icon='MATERIAL')
        col.prop(op, "colormap", text="Colormap")
        col.prop(op, "interpolation", text="Interpolation")
        col.prop(op, "material_name", text="Material Name")
        col.prop(op, "apply_to_all", text="Apply to All")

        # Separador visual
        layout.separator()

        # Sección de Custom ColorRamp
        layout.label(text="Custom ColorRamp", icon='COLOR')
        box = layout.box()
        row = box.row(align=True)
        row.operator(COLORRAMP_OT_add_color.bl_idname,
                     text="Add Color", icon='ADD')
        row.operator(COLORRAMP_OT_remove_color.bl_idname,
                     text="Remove Color", icon='REMOVE')

        for i, color in enumerate(scene.custom_colorramp):
            row = box.row(align=True)
            row.prop(color, "color", text=f"Color {i+1}")
            row.prop(color, "position", text="Pos")

        # Separador visual
        layout.separator()

        # Sección de guardado/carga de ColorRamp
        layout.label(text="Save/Load ColorRamp", icon='FILE_FOLDER')
        box = layout.box()
        box.operator(COLORRAMP_OT_save_custom.bl_idname,
                     text="Save ColorRamp", icon='FILE_TICK')
        box.operator(COLORRAMP_OT_load_custom.bl_idname,
                     text="Load ColorRamp", icon='IMPORT')


def register():
    bpy.utils.register_class(ColorRampColor)
    bpy.types.Scene.custom_colorramp = CollectionProperty(type=ColorRampColor)
    bpy.utils.register_class(COLORRAMP_OT_add_color)
    bpy.utils.register_class(COLORRAMP_OT_remove_color)
    bpy.utils.register_class(COLORRAMP_OT_save_custom)
    bpy.utils.register_class(COLORRAMP_OT_load_custom)
    bpy.utils.register_class(MATERIAL_OT_create_shader)
    bpy.utils.register_class(MATERIAL_PT_shader_generator)


def unregister():
    del bpy.types.Scene.custom_colorramp
    bpy.utils.unregister_class(ColorRampColor)
    bpy.utils.unregister_class(COLORRAMP_OT_add_color)
    bpy.utils.unregister_class(COLORRAMP_OT_remove_color)
    bpy.utils.unregister_class(COLORRAMP_OT_save_custom)
    bpy.utils.unregister_class(COLORRAMP_OT_load_custom)
    bpy.utils.unregister_class(MATERIAL_OT_create_shader)
    bpy.utils.unregister_class(MATERIAL_PT_shader_generator)


if __name__ == "__main__":
    register()
