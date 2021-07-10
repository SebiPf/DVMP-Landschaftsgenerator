import bpy
import random

def generate_stone(grid_loc_x, grid_loc_y, grid_spacing, size_x, size_y, size_z):
    # create cube
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(grid_loc_x * grid_spacing, grid_loc_y * grid_spacing, 0), scale=(1, 1, 1))

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

# define grid size
grid_size_x = 5
grid_size_y = 5

# define grid spacing
grid_spacing = 4

# define min and max size of stones
size_min = 0.4
size_max = 2.5

for row in range(grid_size_x):
    for column in range(grid_size_y):
        # generate random sizes
        size_x = random.uniform(size_min, size_max)
        size_y = random.uniform(size_min, size_max)
        size_z = random.uniform(size_min, size_max)

        generate_stone(row, column, grid_spacing, size_x, size_y, size_z)
