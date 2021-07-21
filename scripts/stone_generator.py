from math import radians
import os
import random
import typing
import bpy
from bpy import context, data, ops
from datetime import datetime

# Blender Plugin Meta-Data
bl_info = {
    "name": "Stone Generator",
    "description": "Generate Stones",
    "author": "Justin Esposito",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "View3D > Add > Add Stone",
    "category": "Object"
}

class OBJECT_OT_add_stone(bpy.types.Operator):
    """Adds and Generate Stones in the scene"""
    bl_idname = "object.add_stone"
    bl_label = "Add Stone"
    bl_options = {"REGISTER", "UNDO"}

    # defines the amount of stones to be generated
    amount_of_stones: bpy.props.IntProperty(
        name="Amount Of Stones",
        description="Changes the amount of stones",
        default=1
    )

    # defines the minimum size of a stone
    size_min: bpy.props.FloatProperty(
        name="Minimum size of a stone",
        description="Changes the minimum size of a stone",
        default=0.4
    )

    # defines the maximum size of a stone
    size_max: bpy.props.FloatProperty(
        name="Maximum size of a stone",
        description="Changes the maximum size of a stone",
        default=1.2
    )

    def getRandom(self, min: float, max: float) -> float:
        seed = datetime.now().timestamp()
        random.seed(seed)
        return random.uniform(min, max)

    # method to generate a stone
    def generate_stone(self):
        
        # Extract Terrain from Scene
        # (!) Terrain is needed for set Stone Location
        terrain: bpy.types.Object = bpy.data.objects.get('Terrain-Plane')

        if terrain:

            # Extract Vertices from Terrain
            VERTS = [(terrain.matrix_world @ v.co)
                     for v in terrain.data.vertices]

            # create stones
            for i in range(self.amount_of_stones):
                # set default values for x-, y-, z- size
                size_x = 0
                size_y = 0
                size_z = 0

                # generate random sizes
                size_x = random.uniform(self.size_min, self.size_max)
                size_y = random.uniform(self.size_min, self.size_max)
                size_z = random.uniform(self.size_min, self.size_max) - 0.2        

                # create cube
                bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', scale=(1, 1, 1))

                # make a base cube and set name to 'stone'
                base_cube = bpy.data.objects['Cube']
                base_cube.name = 'stone'

                # increase size of cube
                bpy.context.object.scale = (size_x, size_y, size_z)

                # enter edit mode
                bpy.ops.object.editmode_toggle()

                # bevel cube
                bpy.ops.mesh.bevel(offset=0.514808, offset_pct=0, affect='EDGES')

                # set mode to object mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # add subdivision modifier
                bpy.ops.object.modifier_add(type='SUBSURF')

                # increase subdivisions
                bpy.context.object.modifiers["Subdivision"].levels = 4
                bpy.context.object.modifiers["Subdivision"].render_levels = 4

                # make texture
                bpy.data.textures.new("Voronoi", 'VORONOI')

                # make modifier
                modifier = base_cube.modifiers.new(name="Displace", type='DISPLACE')
                modifier.texture = bpy.data.textures['Voronoi']

                # increase size
                bpy.data.textures["Voronoi"].noise_scale = 0.92

                # reduce contrast of texture
                bpy.data.textures["Voronoi"].contrast = 0.61

                # add decimate modifier
                bpy.ops.object.modifier_add(type='DECIMATE')

                # reduce ratio
                bpy.context.object.modifiers["Decimate"].ratio = 0.256579
                
                
                # create new material
                mat = bpy.data.materials.new(name="New_Stone_Mat")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                
                # load image texture
                image = bpy.data.images.load(os.path.dirname(os.path.realpath(__file__)).replace(
                        'main.blend',
                        'textures\\rock.jpg'
                    ))

                # Activate "Use Node" in Shading View
                mat.use_nodes = True

                # Node List
                nodes_list: typing.List[bpy.types.Node] = mat.node_tree.nodes

                # Nodes
                node_texCoord: bpy.types.Node = nodes_list.new("ShaderNodeTexCoord")
                node_mapping: bpy.types.Node = nodes_list.new("ShaderNodeMapping")
                node_texImage: bpy.types.Node = nodes_list.new("ShaderNodeTexImage")
                node_bump: bpy.types.Node = nodes_list.new("ShaderNodeBump")
                node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

                mat.node_tree.links.new(bsdf.inputs['Base Color'], node_texImage.outputs['Color'])
                node_texImage.image = image
                
                # Connect Nodes
                mat.node_tree.links.new(
                    node_texCoord.outputs[2],
                    node_mapping.inputs[0]
                )
                mat.node_tree.links.new(
                    node_mapping.outputs[0],
                    node_texImage.inputs[0]
                )
                mat.node_tree.links.new(
                    node_texImage.outputs[0],
                    node_bsdf.inputs[0]
                )
                mat.node_tree.links.new(
                    node_texImage.outputs[0],
                    node_bump.inputs[2]
                )
                mat.node_tree.links.new(
                    node_bump.outputs[0],
                    node_bsdf.inputs[20]
                )
                
                node_bump.inputs[0].default_value = 0.592
                node_bump.inputs[1].default_value = 2.6

                node_mapping.inputs[3].default_value[0] = 7.2
                node_mapping.inputs[3].default_value[1] = 8.9

                ob = context.view_layer.objects.active

                # assign material to object
                if ob.data.materials:
                    ob.data.materials[0] = mat
                else:
                    ob.data.materials.append(mat)

                # Context for Stone
                if base_cube:
                    base_cube.name = 'stone.' + str(i)

                # Set Random Stone Location depending on Terrain
                vert = VERTS[int(self.getRandom(0, len(VERTS)))]
                base_cube.location = (vert[0], vert[1], vert[2])

                # Set Random Stone Rotation
                base_cube.rotation_euler = (0, 0, radians(self.getRandom(0, 360)))
        else:
            print('Add Terrain first.')
        
    # define execute method
    def execute(self, context):
        self.generate_stone()

        return { 'FINISHED' }


# Define the Menu Layout
def menu_layout(self, context):
    self.layout.operator(
        OBJECT_OT_add_stone.bl_idname,  # Operator
        icon="META_PLANE"  # Icon
    )

def register():
    bpy.utils.register_class(OBJECT_OT_add_stone)
    bpy.types.VIEW3D_MT_add.append(menu_layout)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_stone)
    bpy.types.VIEW3D_MT_add.remove(menu_layout)

if __name__ == "__main__":
    register()
