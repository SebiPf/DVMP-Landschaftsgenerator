import math
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
        # Extract Data from Terrain
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
                # Variables
                length = (
                    self.getRandom(0.6, 1.1),
                    self.getRandom(0.6, 0.9),
                    0.5,
                    0.1
                )
                downAngle = (
                    0,
                    self.getRandom(25, 35),
                    55,
                    30
                )
                leaves = self.getRandom(100, 200)
                branches = (
                    0,
                    int(self.getRandom(50, 70)),
                    10,
                    1
                )
                segSplits = (0.1, self.getRandom(0.5, 0.7), 0.2, 0)

                # Create Tree based on "Sapling Tree Gen"
                bpy.ops.curve.tree_add(
                    length=length,
                    downAngle=downAngle,
                    leaves=leaves,
                    branches=branches,
                    segSplits=segSplits,
                    do_update=True, bevel=True, prune=False, showLeaves=True, useArm=False, seed=0, handleType='0', levels=2, lengthV=(0, 0.1, 0, 0), taperCrown=0.5, curveRes=(8, 5, 3, 1), curve=(0, -15, 0, 0), curveV=(20, 50, 75, 0), curveBack=(0, 0, 0, 0), baseSplits=3, splitByLen=True, rMode='rotate', splitAngle=(18, 18, 22, 0), splitAngleV=(5, 5, 5, 0), scale=5, scaleV=2, attractUp=(3.5, -1.89984, 0, 0), attractOut=(0, 0.8, 0, 0), shape='7', shapeS='10', customShape=(0.5, 1, 0.3, 0.5), branchDist=1.5, nrings=0, baseSize=0.3, baseSize_s=0.16, splitHeight=0.2, splitBias=0.55, ratio=0.015, minRadius=0.0015, closeTip=False, rootFlare=1, autoTaper=True, taper=(
                        1, 1, 1, 1), radiusTweak=(1, 1, 1, 1), ratioPower=1.2, downAngleV=(0, 10, 10, 10), useOldDownAngle=True, useParentAngle=True, rotate=(99.5, 137.5, 137.5, 137.5), rotateV=(15, 0, 0, 0), scale0=1, scaleV0=0.1, pruneWidth=0.34, pruneBase=0.12, pruneWidthPeak=0.5, prunePowerHigh=0.5, prunePowerLow=0.001, pruneRatio=0.75, leafDownAngle=30, leafDownAngleV=-10, leafRotate=137.5, leafRotateV=15, leafScale=0.3, leafScaleX=0.2, leafScaleT=0.1, leafScaleV=1.0, leafShape='hex', bend=0, leafangle=-12, horzLeaves=True, leafDist='6', bevelRes=1, resU=4, armAnim=False, previewArm=False, leafAnim=False, frameRate=1, loopFrames=0, wind=1, gust=1, gustF=0.075, af1=1, af2=1, af3=4, makeMesh=False, armLevels=2, boneStep=(1, 1, 1, 1))

                # Context for Tree & Leaf
                tree: bpy.types.Object
                tree = bpy.data.objects.get('tree')
                if tree:
                    tree.name = 'tree.' + str(i)

                leaf = tree.children[0]

                # Add Materials
                tree.data.materials.append(WOOD_MAT)
                leaf.data.materials.append(LEAF_MAT)

                # Set Location
                vert = VERTS[int(self.getRandom(0, len(VERTS)))]
                tree.location = (vert[0], vert[1], vert[2])
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
