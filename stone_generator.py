import bpy
import random

bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.

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

    # define amount of stones that should be generated
    amount_of_stones: bpy.props.IntProperty(
        name="Amount Of Stones",
        description="Changes the amount of stones",
        default=1
    )

    # define grid size
    grid_size_x: bpy.props.IntProperty(
        name="Grid Size X",
        description="Changes the X Value of the Grid Size",
        default=4
    )
    
    grid_size_y: bpy.props.IntProperty(
        name="Grid Size Y",
        description="Changes the Y Value of the Grid Size",
        default=8
    )

    # define grid spacing
    grid_spacing: bpy.props.IntProperty(
        name="Grid Spacing",
        description="Changes the Grid Spacing",
        default=4
    )

    # define min and max size of stones
    size_min: bpy.props.FloatProperty(
        name="Size Min",
        description="Changes the Min Size of a Stone",
        default=0.4
    )

    size_max: bpy.props.FloatProperty(
        name="Size Max",
        description="Changes the Max Size of a Stone",
        default=2.5
    )

    # define grid locactions
    grid_loc_x: bpy.props.IntProperty(
        name="Grid Loc X",
        description="Changes the X Value of the Grid Location",
        default=0
    )

    grid_loc_y: bpy.props.IntProperty(
        name="Grid Loc Y",
        description="Changes the Y Value of the Grid Location",
        default=0
    )

    def generate_stone(self):
        size_x = 0
        size_y = 0
        size_z = 0

        for row in range(self.grid_size_x):
            for column in range(self.grid_size_y):
                # generate random sizes
                size_x = random.uniform(self.size_min, self.size_max)
                size_y = random.uniform(self.size_min, self.size_max)
                size_z = random.uniform(self.size_min, self.size_max) - 0.2

                # compute min and max values for positioning stone in grid
                min_grid_loc = min(self.grid_size_x, self.grid_size_y)
                max_grid_loc = max(self.grid_size_x, self.grid_size_y)

                # position stone randomly in the grid
                self.grid_loc_x = random.randint(min_grid_loc, max_grid_loc)
                self.grid_loc_y = random.randint(min_grid_loc, max_grid_loc)

        # create cube
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(self.grid_loc_x * self.grid_spacing, self.grid_loc_y * self.grid_spacing, 0), scale=(1, 1, 1))

        # make a base cube
        base_cube = bpy.data.objects['Cube']
        base_cube.name = 'Base_Cube'

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

    def execute(self, context):
        count = 0
        while count < self.amount_of_stones:
            self.generate_stone()
            count += 1
        

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
