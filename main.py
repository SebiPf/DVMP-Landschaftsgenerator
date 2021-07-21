from math import radians
import bpy
import bmesh
import random
import typing
import os
from datetime import datetime

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

    TREES: bpy.props.BoolProperty(
        name="Create Trees",
        description="",
        default=False
    )
    NUMBER_TREES: bpy.props.IntProperty(
        name="Number of Trees",
        description="Changes the Number of Trees to Display",
        default=1
    )

    STONES: bpy.props.BoolProperty(
        name="Create Stones",
        description="",
        default=False
    )
    NUMBER_STONES: bpy.props.IntProperty(
        name="Number of Stones",
        description="Changes the Number of Stones to Display",
        default=1
    )

    # defines the amount of stones to be generated
    NUMBER_STONES: bpy.props.IntProperty(
        name="Amount Of Stones",
        description="Changes the amount of stones",
        default=1
    )

    # defines the minimum size of a stone
    STONE_MIN: bpy.props.FloatProperty(
        name="Minimum size of a stone",
        description="Changes the minimum size of a stone",
        default=0.4
    )

    # defines the maximum size of a stone
    STONE_MAX: bpy.props.FloatProperty(
        name="Maximum size of a stone",
        description="Changes the maximum size of a stone",
        default=0.8
    )

    SKY: bpy.props.BoolProperty(
        name="Create Sky",
        description="",
        default=False
    )
    # Floats
    POS_X: bpy.props.FloatProperty(
        name="Sun X-Position",
        description="",
        default=0
    )
    POS_Y: bpy.props.FloatProperty(
        name="Sun Y-Position",
        description="",
        default=0
    )
    POS_Z: bpy.props.FloatProperty(
        name="Sun Height",
        description="Choose height of the Sun",
        default=3
    )
    STRENGTH: bpy.props.FloatProperty(
        name="Illumination strength",
        description="Choose strength of the Sun Illumuniation",
        default=2.5
    )
    TEMP: bpy.props.IntProperty(
        name="Color-Temperature",
        description="",
        default=70,
        min=10,
        max=120
    )
    CYCLE: bpy.props.BoolProperty(
        name="Day / Night Toggle",
        description="Switch between day and night clycles",
        default=True
    )

    # Landscape

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
        """
            bpy.data.collections.new("Entities")
            bpy.context.scene.collection.children.link(bpy.data.collections["Entities"])

            # Count Amount of Vertices
            sce = bpy.context.scene
            me = obj.to_mesh()
            countVerts = len(me.vertices)

            # (Create) Object to place on Terrain
            bpy.ops.mesh.primitive_cube_add(location=(0.0, 8.0, 0.0), size=0.5)
            basic_cube = bpy.data.objects['Cube']

            # Select Verts
            bpy.ops.object.mode_set(mode = 'EDIT') 
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

            ObjectsToSpawn = 5

            for i in range(0, ObjectsToSpawn):
                x = randint(0, countVerts-1)
                obj.data.vertices[x].select = True 

            selected = [(obj.matrix_world @ v.co) for v in obj.data.vertices if v.select]
            for vertex in selected:
                name = f'basic_cube {vertex}'
                new_cube = bpy.data.objects.new(name=name, object_data=basic_cube.data)
                new_cube.location = (vertex[0], vertex[1], vertex[2])   #TODO Offset berücksichtigen
                bpy.data.collections["Entities"].objects.link(new_cube) 
            """

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

        color_ramp = terrain_material.node_tree.nodes.new("ShaderNodeValToRGB")
        color_ramp.location = (-300, 300)

        color_ramp.color_ramp.elements.new(0.0)
        color_ramp.color_ramp.elements[0].color = (0.035, 0.666, 0.022, 1)

        color_ramp.color_ramp.elements[1].position = (1.0)
        color_ramp.color_ramp.elements[1].color = (0.662, 0.904, 0.098, 1)

        principled_bsdf = nodes.get("Principled BSDF")
        terrain_material.node_tree.links.new(
            principled_bsdf.inputs["Base Color"], color_ramp.outputs["Color"])

        # TEMP  -   Removing Start-Cube-Object
        """
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['Cube'].select_set(True)

            #TODO Ecken werden immer mit ausgewählt beim Setzen der Würfel/ Entities
            bpy.data.objects['basic_cube <Vector (-3.0000, -3.0000, 0.0000)>'].select_set(True)
            bpy.data.objects['basic_cube <Vector (-3.0000, 3.0000, 0.0000)>'].select_set(True)
            bpy.data.objects['basic_cube <Vector (3.0000, -3.0000, 0.0000)>'].select_set(True)
            bpy.data.objects['basic_cube <Vector (3.0000, 3.0000, 0.0000)>'].select_set(True)
            bpy.ops.object.delete()
            """

    # Trees

    def getRandom(self, min: float, max: float) -> float:
        seed = datetime.now().timestamp()
        random.seed(seed)
        return random.uniform(min, max)

    def create_leaf_material(self) -> bpy.types.Material:
        material: bpy.types.Material = bpy.data.materials.new(
            "Leaf Material"
        )

        # Activate "Use Node" in Shading View
        material.use_nodes = True

        # Node List
        nodes_list: typing.List[bpy.types.Node] = material.node_tree.nodes

        # Nodes
        node_texCoord: bpy.types.Node = nodes_list.new("ShaderNodeTexCoord")
        node_mapping: bpy.types.Node = nodes_list.new("ShaderNodeMapping")
        node_texImage: bpy.types.Node = nodes_list.new("ShaderNodeTexImage")
        node_bump: bpy.types.Node = nodes_list.new("ShaderNodeBump")
        node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

        # Connect Nodes
        material.node_tree.links.new(
            node_texCoord.outputs[2],
            node_mapping.inputs[0]
        )
        material.node_tree.links.new(
            node_mapping.outputs[0],
            node_texImage.inputs[0]
        )
        material.node_tree.links.new(
            node_texImage.outputs[0],
            node_bsdf.inputs[0]
        )
        material.node_tree.links.new(
            node_texImage.outputs[0],
            node_bump.inputs[2]
        )
        material.node_tree.links.new(
            node_bump.outputs[0],
            node_bsdf.inputs[20]
        )

        # Manipulate Nodes
        print(node_texImage.inputs)
        node_mapping.inputs[3].default_value[0] = 3.9
        node_mapping.inputs[3].default_value[1] = 1.7
        node_bump.inputs[0].default_value = 0.8
        node_bump.inputs[1].default_value = 1.0

        # Add Texture
        image: bpy.types.Image = bpy.data.images.load(
            os.path.dirname(os.path.realpath(__file__)).replace(
                'main.blend',
                'textures\\leaf.jpg'
            )
        )
        node_texImage.image = image

        return material  # Return Material

    def create_wood_material(self) -> bpy.types.Material:
        material: bpy.types.Material = bpy.data.materials.new(
            "Tree Material"
        )

        # Activate "Use Node" in Shading View
        material.use_nodes = True

        # Node List
        nodes_list: typing.List[bpy.types.Node] = material.node_tree.nodes

        # Nodes
        node_texCoord: bpy.types.Node = nodes_list.new("ShaderNodeTexCoord")
        node_mapping: bpy.types.Node = nodes_list.new("ShaderNodeMapping")
        node_texImage: bpy.types.Node = nodes_list.new("ShaderNodeTexImage")
        node_bump: bpy.types.Node = nodes_list.new("ShaderNodeBump")
        node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

        # Connect Nodes
        material.node_tree.links.new(
            node_texCoord.outputs[2],
            node_mapping.inputs[0]
        )
        material.node_tree.links.new(
            node_mapping.outputs[0],
            node_texImage.inputs[0]
        )
        material.node_tree.links.new(
            node_texImage.outputs[0],
            node_bsdf.inputs[0]
        )
        material.node_tree.links.new(
            node_texImage.outputs[0],
            node_bump.inputs[2]
        )
        material.node_tree.links.new(
            node_bump.outputs[0],
            node_bsdf.inputs[20]
        )

        # Manipulate Nodes
        print(node_texImage.inputs)
        node_mapping.inputs[3].default_value[0] = 3.9
        node_mapping.inputs[3].default_value[1] = 1.7
        node_bump.inputs[0].default_value = 0.45

        # Add Texture
        image: bpy.types.Image = bpy.data.images.load(
            os.path.dirname(os.path.realpath(__file__)).replace(
                'main.blend',
                'textures\\tree.jpg'
            )
        )
        node_texImage.image = image

        return material  # Return Material

    def create_trees(self):
        # Extract Terrain from Scene
        # (!) Terrain is needed for set Tree Location
        terrain: bpy.types.Object = bpy.data.objects.get('Terrain-Plane')

        if terrain:
            # Prepare Materials
            WOOD_MAT = self.create_wood_material()
            LEAF_MAT = self.create_leaf_material()

            # Extract Vertices from Terrain
            VERTS = [(terrain.matrix_world @ v.co)
                     for v in terrain.data.vertices]

            # Create Trees
            for i in range(self.NUMBER_TREES):
                # Randomized Tree Variables
                length = (
                    self.getRandom(0.45, 0.55),
                    self.getRandom(0.25, 0.35),
                    0.0,
                    0.0
                )
                splitHeight = self.getRandom(0.2, 1.0)

                # Create Tree based on "Sapling Tree Gen"
                bpy.ops.curve.tree_add(
                    splitHeight=splitHeight,
                    length=length,
                    do_update=True, chooseSet='0', bevel=True, prune=False, showLeaves=True, useArm=False, seed=0, handleType='0', levels=2, lengthV=(0, 0, 0, 0), taperCrown=0, branches=(0, 25, 0, 0), curveRes=(16, 5, 3, 1), curve=(0, -20, -20, 0), curveV=(400, 150, 100, 0), curveBack=(0, 0, 0, 0), baseSplits=0, segSplits=(0.25, 3, 0, 0), splitByLen=True, rMode='rotate', splitAngle=(15, 20, 25, 0), splitAngleV=(5, 5, 0, 0), scale=6, scaleV=2, attractUp=(0, -0.35, -0.2, 0), attractOut=(0, 0.75, 0.25, 0), shape='8', shapeS='10', customShape=(0.7, 1, 0.2, 0.8), branchDist=1, nrings=0, baseSize=0.4, baseSize_s=0.25, splitBias=0, ratio=0.02, minRadius=0.0015, closeTip=False, rootFlare=1, autoTaper=True, taper=(
                        1, 1, 1, 1), radiusTweak=(1, 1, 1, 1), ratioPower=1.25, downAngle=(90, 90, 30, 30), downAngleV=(0, 90, 15, 10), useOldDownAngle=False, useParentAngle=False, rotate=(99.5, 137.5, 137.5, 137.5), rotateV=(15, 0, 0, 0), scale0=1, scaleV0=0.1, pruneWidth=0.4, pruneBase=0.3, pruneWidthPeak=0.6, prunePowerHigh=0.5, prunePowerLow=0.001, pruneRatio=1, leaves=-5, leafDownAngle=45, leafDownAngleV=10, leafRotate=137.5, leafRotateV=0, leafScale=0.17, leafScaleX=0.2, leafScaleT=-0.5, leafScaleV=0, leafShape='hex', bend=0, leafangle=-10, horzLeaves=True, leafDist='6', bevelRes=0, resU=1, armAnim=False, previewArm=False, leafAnim=False, frameRate=1, loopFrames=0, wind=1, gust=1, gustF=0.075, af1=1, af2=1, af3=4, makeMesh=False, armLevels=2, boneStep=(1, 1, 1, 1))

                # Context for Tree & Leaf
                tree: bpy.types.Object
                tree = bpy.data.objects.get('tree')
                if tree:
                    tree.name = 'tree.' + str(i)

                leaf = tree.children[0]

                # Add Materials
                tree.data.materials.append(WOOD_MAT)
                leaf.data.materials.append(LEAF_MAT)

                # Set Random Tree Location depending on Terrain
                vert = VERTS[int(self.getRandom(0, len(VERTS)))]
                tree.location = (vert[0], vert[1], vert[2])

                # Set Random Tree Rotation
                tree.rotation_euler = (0, 0, radians(self.getRandom(0, 360)))
        else:
            print('Add Terrain first')

    # Stones

    def create_stones(self, context):

        # Extract Terrain from Scene
        # (!) Terrain is needed for set Stone Location
        terrain: bpy.types.Object = bpy.data.objects.get('Terrain-Plane')

        if terrain:

            # Extract Vertices from Terrain
            VERTS = [(terrain.matrix_world @ v.co)
                     for v in terrain.data.vertices]

            # create stones
            for i in range(self.NUMBER_STONES):
                # set default values for x-, y-, z- size
                size_x = 0
                size_y = 0
                size_z = 0

                # generate random sizes
                size_x = random.uniform(self.STONE_MIN, self.STONE_MAX)
                size_y = random.uniform(self.STONE_MIN, self.STONE_MAX)
                size_z = random.uniform(self.STONE_MIN, self.STONE_MAX) - 0.2

                # create cube
                bpy.ops.mesh.primitive_cube_add(
                    enter_editmode=False, align='WORLD', scale=(1, 1, 1))

                # make a base cube and set name to 'stone'
                base_cube = bpy.data.objects['Cube']
                base_cube.name = 'stone'

                # increase size of cube
                bpy.context.object.scale = (size_x, size_y, size_z)

                # enter edit mode
                bpy.ops.object.editmode_toggle()

                # bevel cube
                bpy.ops.mesh.bevel(
                    offset=0.514808, offset_pct=0, affect='EDGES')

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
                modifier = base_cube.modifiers.new(
                    name="Displace", type='DISPLACE')
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
                node_texCoord: bpy.types.Node = nodes_list.new(
                    "ShaderNodeTexCoord")
                node_mapping: bpy.types.Node = nodes_list.new(
                    "ShaderNodeMapping")
                node_texImage: bpy.types.Node = nodes_list.new(
                    "ShaderNodeTexImage")
                node_bump: bpy.types.Node = nodes_list.new("ShaderNodeBump")
                node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

                mat.node_tree.links.new(
                    bsdf.inputs['Base Color'], node_texImage.outputs['Color'])
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
                base_cube.rotation_euler = (
                    0, 0, radians(self.getRandom(0, 360)))
        else:
            print('Add Terrain first.')

    def create_sky(self):
        # Parameter für Lichtfarbe

        temp = self.TEMP * 100
        redSun: int = 0
        greenSun: int = 0
        blueSun: int = 0
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(
            self.POS_X, self.POS_Y, self.POS_Z), scale=(1, 1, 1))
        bpy.context.object.data.energy = self.STRENGTH

        # Erstellung aller shader um umschalten von tag zu nacht zu ermöglichen

        nodes = bpy.data.worlds["World"].node_tree.nodes
        my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
        my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
        my_node: bpy.types.Node = nodes.new("ShaderNodeTexNoise")
        my_node: bpy.types.Node = nodes.new("ShaderNodeTexVoronoi")
        bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = (
            0.8)

        # Erstellung der Day Skybox Node Struktur

        if (self.CYCLE == True):

            # Löschen der Nodes des Nachts Shaders

            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["ColorRamp"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Map Range"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Noise Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"])
            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (
                0, 0, 0, 0)

            # Erstellung und verbinden der Nodes

            nodes = bpy.data.worlds["World"].node_tree.nodes

            my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = (
                0.8)
            links = bpy.data.worlds["World"].node_tree.links
            links.new(my_node.outputs[0], nodes["Background"].inputs[0])

            my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
            links.new(my_node.outputs[0], nodes["ColorRamp"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[2].default_value = 0
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[1].default_value = 0.6

            my_node: bpy.types.Node = nodes.new("ShaderNodeTexVoronoi")
            links.new(my_node.outputs[0], nodes["Map Range"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"].inputs[2].default_value = 40

        # Erstellung der Night Skybox Node Struktur

        elif (self.CYCLE == False):

            # Löschen der Nodes des Tags Shaders

            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Noise Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["ColorRamp"])
            bpy.data.worlds["World"].node_tree.nodes.remove(
                bpy.data.worlds["World"].node_tree.nodes["Map Range"])

            # Erstellung und verbinden der Nodes

            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (
                0, 0, 0, 0)

            nodes = bpy.data.worlds["World"].node_tree.nodes

            my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].position = (
                0.7)
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = (
                0.18, 0.45, 1, 1)
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].color = (
                1, 1, 1, 1)
            links = bpy.data.worlds["World"].node_tree.links
            links.new(my_node.outputs[0], nodes["Background"].inputs[0])

            my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
            links.new(my_node.outputs[0], nodes["ColorRamp"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[2].default_value = 1
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[1].default_value = 0.1

            my_node: bpy.types.Node = nodes.new("ShaderNodeTexNoise")
            links.new(my_node.outputs[0], nodes["Map Range"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Noise Texture"].inputs[2].default_value = 2.4
            bpy.data.worlds["World"].node_tree.nodes["Noise Texture"].inputs[3].default_value = 2

        # daten für Umwandlung von FarbTEMP zu RGB

        if temp == 1000:
            redSun = 255
            greenSun = 56
            blueSun = 0
        elif temp == 1100:
            redSun = 255
            greenSun = 71
            blueSun = 0
        elif temp == 1200:
            redSun = 255
            greenSun = 83
            blueSun = 0
        elif temp == 1300:
            redSun = 255
            greenSun = 93
            blueSun = 0
        elif temp == 1400:
            redSun = 255
            greenSun = 101
            blueSun = 0
        elif temp == 1500:
            redSun = 255
            greenSun = 109
            blueSun = 0
        elif temp == 1600:
            redSun = 255
            greenSun = 115
            blueSun = 0
        elif temp == 1700:
            redSun = 255
            greenSun = 121
            blueSun = 0
        elif temp == 1800:
            redSun = 255
            greenSun = 126
            blueSun = 0
        elif temp == 1900:
            redSun = 255
            greenSun = 131
            blueSun = 0
        elif temp == 2000:
            redSun = 255
            greenSun = 138
            blueSun = 18
        elif temp == 2100:
            redSun = 255
            greenSun = 142
            blueSun = 33
        elif temp == 2200:
            redSun = 255
            greenSun = 147
            blueSun = 44
        elif temp == 2300:
            redSun = 255
            greenSun = 152
            blueSun = 54
        elif temp == 2400:
            redSun = 255
            greenSun = 157
            blueSun = 63
        elif temp == 2500:
            redSun = 255
            greenSun = 161
            blueSun = 72
        elif temp == 2600:
            redSun = 255
            greenSun = 165
            blueSun = 79
        elif temp == 2700:
            redSun = 255
            greenSun = 169
            blueSun = 87
        elif temp == 2800:
            redSun = 255
            greenSun = 173
            blueSun = 97
        elif temp == 2900:
            redSun = 255
            greenSun = 177
            blueSun = 101
        elif temp == 3000:
            redSun = 255
            greenSun = 180
            blueSun = 107
        elif temp == 3100:
            redSun = 255
            greenSun = 184
            blueSun = 114
        elif temp == 3200:
            redSun = 255
            greenSun = 187
            blueSun = 120
        elif temp == 3300:
            redSun = 255
            greenSun = 190
            blueSun = 126
        elif temp == 3400:
            redSun = 255
            greenSun = 193
            blueSun = 132
        elif temp == 3500:
            redSun = 255
            greenSun = 196
            blueSun = 437
        elif temp == 3600:
            redSun = 255
            greenSun = 199
            blueSun = 143
        elif temp == 3700:
            redSun = 255
            greenSun = 71
            blueSun = 201
        elif temp == 3800:
            redSun = 255
            greenSun = 204
            blueSun = 153
        elif temp == 3900:
            redSun = 255
            greenSun = 206
            blueSun = 159
        elif temp == 4000:
            redSun = 255
            greenSun = 209
            blueSun = 163
        elif temp == 4100:
            redSun = 255
            greenSun = 211
            blueSun = 168
        elif temp == 4200:
            redSun = 255
            greenSun = 213
            blueSun = 173
        elif temp == 4300:
            redSun = 255
            greenSun = 215
            blueSun = 177
        elif temp == 4400:
            redSun = 255
            greenSun = 219
            blueSun = 217
        elif temp == 4500:
            redSun = 255
            greenSun = 221
            blueSun = 186
        elif temp == 4600:
            redSun = 255
            greenSun = 223
            blueSun = 190
        elif temp == 4700:
            redSun = 255
            greenSun = 225
            blueSun = 194
        elif temp == 4800:
            redSun = 255
            greenSun = 227
            blueSun = 198
        elif temp == 4900:
            redSun = 255
            greenSun = 228
            blueSun = 202
        elif temp == 5000:
            redSun = 255
            greenSun = 230
            blueSun = 206
        elif temp == 5100:
            redSun = 255
            greenSun = 232
            blueSun = 210
        elif temp == 5200:
            redSun = 255
            greenSun = 233
            blueSun = 213
        elif temp == 5300:
            redSun = 255
            greenSun = 235
            blueSun = 217
        elif temp == 5400:
            redSun = 255
            greenSun = 236
            blueSun = 220
        elif temp == 5500:
            redSun = 255
            greenSun = 238
            blueSun = 224
        elif temp == 5600:
            redSun = 255
            greenSun = 239
            blueSun = 227
        elif temp == 5700:
            redSun = 255
            greenSun = 71
            blueSun = 230
        elif temp == 5800:
            redSun = 255
            greenSun = 240
            blueSun = 233
        elif temp == 5900:
            redSun = 255
            greenSun = 242
            blueSun = 236
        elif temp == 6000:
            redSun = 255
            greenSun = 243
            blueSun = 239
        elif temp == 6100:
            redSun = 255
            greenSun = 244
            blueSun = 242
        elif temp == 6200:
            redSun = 255
            greenSun = 245
            blueSun = 245
        elif temp == 6300:
            redSun = 255
            greenSun = 246
            blueSun = 247
        elif temp == 6400:
            redSun = 255
            greenSun = 248
            blueSun = 251
        elif temp == 6500:
            redSun = 254
            greenSun = 249
            blueSun = 253
        elif temp == 6600:
            redSun = 252
            greenSun = 249
            blueSun = 255
        elif temp == 6700:
            redSun = 249
            greenSun = 247
            blueSun = 255
        elif temp == 6800:
            redSun = 247
            greenSun = 246
            blueSun = 255
        elif temp == 6900:
            redSun = 245
            greenSun = 245
            blueSun = 255
        elif temp == 7000:
            redSun = 243
            greenSun = 243
            blueSun = 255
        elif temp == 7100:
            redSun = 240
            greenSun = 242
            blueSun = 255
        elif temp == 7200:
            redSun = 239
            greenSun = 241
            blueSun = 255
        elif temp == 7300:
            redSun = 237
            greenSun = 240
            blueSun = 255
        elif temp == 7400:
            redSun = 235
            greenSun = 239
            blueSun = 255
        elif temp == 7500:
            redSun = 233
            greenSun = 238
            blueSun = 255
        elif temp == 7600:
            redSun = 231
            greenSun = 237
            blueSun = 255
        elif temp == 7700:
            redSun = 230
            greenSun = 236
            blueSun = 255
        elif temp == 7800:
            redSun = 228
            greenSun = 235
            blueSun = 255
        elif temp == 7900:
            redSun = 227
            greenSun = 234
            blueSun = 255
        elif temp == 8000:
            redSun = 225
            greenSun = 233
            blueSun = 255
        elif temp == 8100:
            redSun = 224
            greenSun = 232
            blueSun = 255
        elif temp == 8200:
            redSun = 222
            greenSun = 231
            blueSun = 255
        elif temp == 8300:
            redSun = 221
            greenSun = 230
            blueSun = 255
        elif temp == 8400:
            redSun = 220
            greenSun = 230
            blueSun = 255
        elif temp == 8500:
            redSun = 218
            greenSun = 229
            blueSun = 255
        elif temp == 8600:
            redSun = 217
            greenSun = 229
            blueSun = 255
        elif temp == 8700:
            redSun = 226
            greenSun = 227
            blueSun = 255
        elif temp == 8800:
            redSun = 215
            greenSun = 227
            blueSun = 255
        elif temp == 8900:
            redSun = 214
            greenSun = 226
            blueSun = 255
        elif temp == 9000:
            redSun = 212
            greenSun = 225
            blueSun = 255
        elif temp == 9100:
            redSun = 211
            greenSun = 225
            blueSun = 255
        elif temp == 9200:
            redSun = 210
            greenSun = 224
            blueSun = 255
        elif temp == 9300:
            redSun = 209
            greenSun = 223
            blueSun = 255
        elif temp == 9400:
            redSun = 208
            greenSun = 223
            blueSun = 255
        elif temp == 9500:
            redSun = 207
            greenSun = 222
            blueSun = 255
        elif temp == 9600:
            redSun = 207
            greenSun = 221
            blueSun = 255
        elif temp == 9700:
            redSun = 206
            greenSun = 221
            blueSun = 255
        elif temp == 9800:
            redSun = 205
            greenSun = 220
            blueSun = 255
        elif temp == 9900:
            redSun = 207
            greenSun = 220
            blueSun = 255
        elif temp == 10000:
            redSun = 207
            greenSun = 218
            blueSun = 255
        elif temp == 10100:
            redSun = 206
            greenSun = 218
            blueSun = 255
        elif temp == 10200:
            redSun = 205
            greenSun = 217
            blueSun = 255
        elif temp == 10300:
            redSun = 204
            greenSun = 217
            blueSun = 255
        elif temp == 10400:
            redSun = 204
            greenSun = 216
            blueSun = 255
        elif temp == 10500:
            redSun = 203
            greenSun = 216
            blueSun = 255
        elif temp == 10600:
            redSun = 202
            greenSun = 215
            blueSun = 255
        elif temp == 10700:
            redSun = 202
            greenSun = 215
            blueSun = 255
        elif temp == 10800:
            redSun = 201
            greenSun = 214
            blueSun = 255
        elif temp == 10900:
            redSun = 200
            greenSun = 214
            blueSun = 255
        elif temp == 11000:
            redSun = 200
            greenSun = 213
            blueSun = 255
        elif temp == 11100:
            redSun = 199
            greenSun = 213
            blueSun = 255
        elif temp == 11200:
            redSun = 198
            greenSun = 212
            blueSun = 255
        elif temp == 11300:
            redSun = 198
            greenSun = 212
            blueSun = 255
        elif temp == 11400:
            redSun = 197
            greenSun = 212
            blueSun = 255
        elif temp == 11500:
            redSun = 197
            greenSun = 211
            blueSun = 255
        elif temp == 11600:
            redSun = 197
            greenSun = 211
            blueSun = 255
        elif temp == 11700:
            redSun = 196
            greenSun = 210
            blueSun = 255
        elif temp == 11800:
            redSun = 195
            greenSun = 210
            blueSun = 255
        elif temp == 11900:
            redSun = 195
            greenSun = 210
            blueSun = 255
        elif temp == 12000:
            redSun = 195
            greenSun = 209
            blueSun = 255

        # Finale Farbe der Sonne

        bpy.context.object.data.color = (redSun, greenSun, blueSun)

    def execute(self, context):
        self.create_landscape(context)
        if self.TREES:
            self.create_trees()
        if self.STONES:
            self.create_stones(context)
        if self.SKY:
            self.create_sky()
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
