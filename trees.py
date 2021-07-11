from math import radians
import random
import typing
import bpy
from datetime import datetime

# Blender Plugin Meta-Data
bl_info = {
    "name": "Tree Generator",
    "description": "Generates Trees",
    "author": "Özkan",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "View3D > Add > My Object",
    "category": "Object"
}


class OBJECT_OT_add_trees(bpy.types.Operator):
    """Tooltip Message"""
    bl_idname = "object.add_trees"
    bl_label = "Add Trees"
    bl_options = {"REGISTER", "UNDO"}

    NUMBER_TREES: bpy.props.IntProperty(
        name="Number of Trees",
        description="Changes the Number of Trees to Display",
        default=1
    )

    def getRandom(self, min: float, max: float) -> float:
        seed = datetime.now().timestamp()
        random.seed(seed)
        return random.uniform(min, max)

    def create_leaf_material(self) -> bpy.types.Material:
        # Create Material "Tower Material"
        material: bpy.types.Material = bpy.data.materials.new(
            "Wood Material"
        )

        # Activate "Use Node" in Shading View
        material.use_nodes = True

        # Node List
        nodes_list: typing.List[bpy.types.Node] = material.node_tree.nodes

        # Nodes
        node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

        # Manipulate Nodes
        node_bsdf.inputs[0].default_value = (
            0.0164384,  # R
            0.0571095,  # G
            0.00680011,  # B
            1  # A
        )
        return material  # Return Material

    def create_wood_material(self) -> bpy.types.Material:
        # Create Material "Tower Material"
        material: bpy.types.Material = bpy.data.materials.new(
            "Wood Material"
        )

        # Activate "Use Node" in Shading View
        material.use_nodes = True

        # Node List
        nodes_list: typing.List[bpy.types.Node] = material.node_tree.nodes

        # Nodes
        node_bsdf: bpy.types.Node = nodes_list["Principled BSDF"]

        # Manipulate Nodes
        node_bsdf.inputs[0].default_value = (
            0.051215,  # R
            0.021901,  # G
            0.004866,  # B
            1  # A
        )
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

    def execute(self, context):
        self.create_trees()
        return {'FINISHED'}


def menu_layout(self, context):
    self.layout.operator(
        OBJECT_OT_add_trees.bl_idname,  # Operator
        icon="GHOST_ENABLED"  # Icon
    )


def register():
    bpy.utils.register_class(OBJECT_OT_add_trees)
    bpy.types.VIEW3D_MT_add.append(menu_layout)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_trees)
    bpy.types.VIEW3D_MT_add.remove(menu_layout)


if __name__ == "__main__":
    register()
