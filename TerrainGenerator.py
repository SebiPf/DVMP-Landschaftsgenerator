bl_info = {
    "name": "TerrainGenerator",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from random import randint


class CreateMesh(bpy.types.Operator):
    """Creating a simple Terrain-Mesh"""    
    bl_idname = "object.create_terrain"        
    bl_label = "Create a simple Terrain-Mesh"        
    bl_options = {'REGISTER', 'UNDO'}  

    def execute(self, context):        

        # 1. Create plane
        bpy.ops.mesh.primitive_plane_add()
        obj = bpy.data.objects['Plane']
        obj.scale[0] = 3
        obj.scale[1] = 3
        obj.scale[2] = 3

        # 2. Add a particle system
        psys = obj.modifiers.new("hair", 'PARTICLE_SYSTEM').particle_system
        psys.settings.type = 'HAIR'
        psys.settings.count = 10000
        psys.settings.hair_length = 0.3

        return {'FINISHED'}

#Registration
def add_object_button(self, context):
    self.layout.operator(
        CreateMesh.bl_idname,
        text="Simple Terrain-Mesh",
         icon="GHOST_ENABLED")

def register():
    bpy.utils.register_class(CreateMesh)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(CreateMesh)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()