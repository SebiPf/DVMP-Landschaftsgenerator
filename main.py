from random import randint
import bpy
import bmesh

# Blender Plugin Meta-Data
bl_info = {
    "name": "Landscape Generator",
    "description": "Generate a Landscape",
    "author": "X",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "View3D > Add > My Object",
    "category": "Object"
}


class OBJECT_OT_gen_landscape(bpy.types.Operator):
    """Tooltip Message"""
    bl_idname = "object.gen_landscape"
    bl_label = "Generate Landscape"
    bl_options = {"REGISTER", "UNDO"}

    NUMBER_TREES: bpy.props.IntProperty(
        name="Number of Trees",
        description="Changes the Number of Trees to Display",
        default=1
    )

    TREES: bpy.props.BoolProperty(
        name="Create Trees",
        description="",
        default=False
    )

    def create_landscape(self, context):
        # 1. Create plane
        bpy.ops.mesh.primitive_plane_add()

        object = bpy.data.objects.get('Plane')
        if object:
            object.name = 'Terrain-Plane'

        obj = bpy.data.objects['Terrain-Plane']
        obj.scale[0] = 3
        obj.scale[1] = 3
        obj.scale[2] = 3

        # 2. Add Subdivision Surface Modifier
        context = bpy.context
        ob = context.object
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)

        # subdivide
        bmesh.ops.subdivide_edges(bm,
                                  edges=bm.edges,
                                  cuts=100,
                                  use_grid_fill=True,
                                  )

        bm.to_mesh(me)
        me.update()

        # 3. Add Displacement Modifier
        dispMod = obj.modifiers.new("Displace", type='DISPLACE')

        tex = bpy.data.textures.new('CloudNoise', type='CLOUDS')
        tex.noise_scale = 1.00
        tex.noise_basis = 'ORIGINAL_PERLIN'
        tex.cloud_type = 'COLOR'
        tex.contrast = 1.050
        tex.saturation = 0.97
        tex.intensity = 1.00

        dispMod.texture = tex

        # Apply Modifier
        # TODO Apply erst am Ende?
        bpy.ops.object.modifier_apply(modifier=dispMod.name)

        # 4. Place Object on Terrain
        bpy.data.collections.new("Entities")
        bpy.context.scene.collection.children.link(
            bpy.data.collections["Entities"])

        # Count Amount of Vertices
        sce = bpy.context.scene
        me = obj.to_mesh()
        countVerts = len(me.vertices)

        # (Create) Object to place on Terrain
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 8.0, 0.0), size=0.5)
        basic_cube = bpy.data.objects['Cube']

        # Select Verts
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        ObjectsToSpawn = 5

        for i in range(0, ObjectsToSpawn):
            x = randint(0, countVerts-1)
            obj.data.vertices[x].select = True

        selected = [(obj.matrix_world @ v.co)
                    for v in obj.data.vertices if v.select]
        for vertex in selected:
            name = f'basic_cube {vertex}'
            new_cube = bpy.data.objects.new(
                name=name, object_data=basic_cube.data)
            # TODO Offset berücksichtigen
            new_cube.location = (vertex[0], vertex[1], vertex[2])
            bpy.data.collections["Entities"].objects.link(new_cube)

        # 5. Add a particle system ("Grass")
        psys = obj.modifiers.new("hair", 'PARTICLE_SYSTEM').particle_system
        psys.settings.type = 'HAIR'
        psys.settings.count = 15000
        psys.settings.hair_length = 0.20
        psys.settings.child_type = 'INTERPOLATED'

        # 6. Create (Node-) Material for Terrain-Plane
        terrain_material = bpy.data.materials.new(name="TerrainMaterial")
        terrain_material.use_nodes = True
        obj.active_material = terrain_material

        nodes = terrain_material.node_tree.nodes

        color_ramp = terrain_material.node_tree.nodes.new(
            "ShaderNodeValToRGB")
        color_ramp.location = (-300, 300)

        color_ramp.color_ramp.elements.new(0.0)
        color_ramp.color_ramp.elements[0].color = (0.035, 0.666, 0.022, 1)

        color_ramp.color_ramp.elements[1].position = (1.0)
        color_ramp.color_ramp.elements[1].color = (0.662, 0.904, 0.098, 1)

        principled_bsdf = nodes.get("Principled BSDF")
        terrain_material.node_tree.links.new(
            principled_bsdf.inputs["Base Color"], color_ramp.outputs["Color"])

        # TEMP  -   Removing Start-Cube-Object
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Cube'].select_set(True)

        # TODO Ecken werden immer mit ausgewählt beim Setzen der Würfel/ Entities
        bpy.data.objects['basic_cube <Vector (-3.0000, -3.0000, 0.0000)>'].select_set(
            True)
        bpy.data.objects['basic_cube <Vector (-3.0000, 3.0000, 0.0000)>'].select_set(
            True)
        bpy.data.objects['basic_cube <Vector (3.0000, -3.0000, 0.0000)>'].select_set(
            True)
        bpy.data.objects['basic_cube <Vector (3.0000, 3.0000, 0.0000)>'].select_set(
            True)
        bpy.ops.object.delete()

    def create_trees():
        return

    def execute(self, context):
        self.create_landscape(context)
        if self.TREES:
            self.create_trees()
        return {'FINISHED'}


def menu_layout(self, context):
    self.layout.operator(
        OBJECT_OT_gen_landscape.bl_idname,  # Operator
        icon="VIEW_PERSPECTIVE"  # Icon
    )


def register():
    bpy.utils.register_class(OBJECT_OT_gen_landscape)
    bpy.types.VIEW3D_MT_add.append(menu_layout)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_gen_landscape)
    bpy.types.VIEW3D_MT_add.remove(menu_layout)


if __name__ == "__main__":
    register()
