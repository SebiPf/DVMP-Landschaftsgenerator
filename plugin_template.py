import math
import typing
import bpy

# Blender Plugin Meta-Data
bl_info = {
    "name": "",
    "description": "",
    "author": "",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "View3D > Add > My Object",
    "category": "Object"
}


class OBJECT_OT_add_something(bpy.types.Operator):
    """Tooltip Message"""
    bl_idname = "object.add_my_object"
    bl_label = "Add My Object"
    bl_options = {"REGISTER", "UNDO"}

    # Floats
    float_property: bpy.props.FloatProperty(
        name="Float Property",
        description="Changes a Float-Property",
        default=1.5
    )
    # Integers
    integer_property: bpy.props.IntProperty(
        name="Integer Property",
        description="Changes an Integer-Property",
        default=1
    )

    # Create a Material
    def create_material(self) -> bpy.types.Material:
        # Create Material "New Material"
        material: bpy.types.Material = bpy.data.materials.new(
            "New Material"
        )
        # ...
        return material

    def execute(self, context):
        # ...
        return {'FINISHED'}


# Define the Menu Layout
def menu_layout(self, context):
    self.layout.operator(
        OBJECT_OT_add_something.bl_idname,  # Operator
        icon="GHOST_ENABLED"  # Icon
    )


def register():
    bpy.utils.register_class(OBJECT_OT_add_something)
    bpy.types.VIEW3D_MT_add.append(menu_layout)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_something)
    bpy.types.VIEW3D_MT_add.remove(menu_layout)


if __name__ == "__main__":
    register()
