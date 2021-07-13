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


class Add_Sky(bpy.types.Operator):
    """Tooltip Message"""
    bl_idname = "object.add_my_object"
    bl_label = "Sun"
    bl_options = {"REGISTER", "UNDO"}

    # Floats
    pos_x: bpy.props.FloatProperty(
        name="Pos_x",
        description="Pos_x",
        default=1
    )
    pos_y: bpy.props.FloatProperty(
        name="Pos_y",
        description="Pos_y",
        default=1
    )
    pos_z: bpy.props.FloatProperty(
        name="Pos_y",
        description="Pos_y",
        default=1
    )
    strength: bpy.props.FloatProperty(
        name="strength",
        description="strength",
        default=1
    )
    temperatur: bpy.props.IntProperty(
        name="temperatur",
        description="temperatur",
        #default= 70,
        min = 10,
        max= 120
    )
    daynightcycle: bpy.props.BoolProperty(
        name="daynightcycle",
        description="daynightcycle",
        default = True    
    )
    temperatur = 1
    

    # Create a Material
    def create_material(self) -> bpy.types.Material:
        # Create Material "New Material"
        material: bpy.types.Material = bpy.data.materials.new(
            "New Material"
        )
        # ...
        return material

    

    def execute(self, context):

        # Parameter für Lichtfarbe

        temp = self.temperatur *100
        redSun: int = 0
        greenSun: int = 0
        blueSun: int = 0
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(self.pos_x  ,self.pos_y  ,self.pos_z)  ,scale=(1,1,1))
        bpy.context.object.data.energy = self.strength
        

        # Erstellung aller shader um umschalten von tag zu nacht zu ermöglichen

        nodes = bpy.data.worlds["World"].node_tree.nodes
        my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
        my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
        my_node: bpy.types.Node = nodes.new("ShaderNodeTexNoise")
        my_node: bpy.types.Node = nodes.new("ShaderNodeTexVoronoi")
        bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = (0.8)

        # Erstellung der Day Skybox Node Struktur

        if (self.daynightcycle==True):

            # Löschen der Nodes des Nachts Shaders

            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["ColorRamp"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Map Range"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Noise Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"])
            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,0)

            # Erstellung und verbinden der Nodes

            nodes = bpy.data.worlds["World"].node_tree.nodes

            my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = (0.8)
            links =  bpy.data.worlds["World"].node_tree.links
            links.new(my_node.outputs[0], nodes["Background"].inputs[0])

            my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
            links.new(my_node.outputs[0], nodes["ColorRamp"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[2].default_value = 0
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[1].default_value = 0.6

            my_node: bpy.types.Node = nodes.new("ShaderNodeTexVoronoi")
            links.new(my_node.outputs[0], nodes["Map Range"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"].inputs[2].default_value = 40
        
        # Erstellung der Night Skybox Node Struktur

        elif (self.daynightcycle==False):

            # Löschen der Nodes des Tags Shaders

            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Voronoi Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Noise Texture"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["ColorRamp"])
            bpy.data.worlds["World"].node_tree.nodes.remove(bpy.data.worlds["World"].node_tree.nodes["Map Range"])
            

            # Erstellung und verbinden der Nodes

            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,0)

            nodes = bpy.data.worlds["World"].node_tree.nodes

            my_node: bpy.types.Node = nodes.new("ShaderNodeValToRGB")
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].position = (0.7)
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = (0.18,0.45,1,1)
            bpy.data.worlds["World"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].color = (1,1,1,1)
            links =  bpy.data.worlds["World"].node_tree.links
            links.new(my_node.outputs[0], nodes["Background"].inputs[0])

            my_node: bpy.types.Node = nodes.new("ShaderNodeMapRange")
            links.new(my_node.outputs[0], nodes["ColorRamp"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[2].default_value = 1
            bpy.data.worlds["World"].node_tree.nodes["Map Range"].inputs[1].default_value = 0.1

            my_node: bpy.types.Node = nodes.new("ShaderNodeTexNoise")
            links.new(my_node.outputs[0], nodes["Map Range"].inputs[0])
            bpy.data.worlds["World"].node_tree.nodes["Noise Texture"].inputs[2].default_value = 2.4
            bpy.data.worlds["World"].node_tree.nodes["Noise Texture"].inputs[3].default_value = 2

        
        # daten für Umwandlung von Farbtemperatur zu RGB

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
            blueSun =255
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

        bpy.context.object.data.color = (redSun,greenSun,blueSun)
        return {'FINISHED'}


# Define the Menu Layout
def menu_layout(self, context):
    self.layout.operator(
        Add_Sky.bl_idname,  # Operator
        icon="GHOST_ENABLED"  # Icon
    )


def register():
    bpy.utils.register_class(Add_Sky)
    bpy.types.VIEW3D_MT_add.append(menu_layout)


def unregister():
    bpy.utils.unregister_class(Add_Sky)
    bpy.types.VIEW3D_MT_add.remove(menu_layout)


if __name__ == "__main__":
    
    register()
