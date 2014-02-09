bl_info = {
    "name": "Import/Export Minecraft JSON Model",
    "category": "Import-Export"
}

import bpy
import json

class ImportMinecraftJsonModel(bpy.types.Operator):
    bl_idname = "import_mesh.minecraftjson"
    bl_label = "Import Minecraft Json Model (.json)"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".json"
    check_extension = True
    
    def execute(self, context):
        file = open(self.filepath,'r')
        model = json.load(file)
        file.close()
        mesh = bpy.data.meshes.new(model['name'])
        object = bpy.data.objects.new(model['name'], mesh)
        
        bpy.context.scene.objects.link(object)
        verts = []
        faces = []
        iterateIndex = 0
        for face in model['faces']:
            faceVerts = []
            for vertex in face['vertices']:
                index = -1
                iterateIndex = 0
                for foundvert in verts:
                    if vertex['position'][0] == foundvert[0] and vertex['position'][1] == -foundvert[2] and vertex['position'][2] == foundvert[1]:
                        index = iterateIndex
                    iterateIndex += 1
                if index == -1:
                    index = len(verts)
                    verts.append([vertex['position'][0],-vertex['position'][2],vertex['position'][1]])
                faceVerts.append(index)
            faces.append(faceVerts)
        mesh.from_pydata(verts,[],faces)    
        #if mesh.tessfaces:
        uvLayer = mesh.uv_textures.new('UVMap')
        uvLoop = mesh.uv_layers[0]
        i = 0
        for face in model['faces']:
            meshFace = mesh.polygons[i]
            j = 0
            
            for loopIndex in range(meshFace.loop_start, meshFace.loop_start + meshFace.loop_total):
                uvcoords = [face['vertices'][j]['texcoord'][0]/16.0,1-(face['vertices'][j]['texcoord'][1]/16.0)]
                uvLoop.data[loopIndex].uv = uvcoords
                print (str(mesh.vertices[meshFace.vertices[j]].co))
                print(str(face['vertices'][j]['texcoord'][0]) + ',' + str(face['vertices'][j]['texcoord'][1]))
                j += 1
            # Materials!
            theMaterial = None
            for material in bpy.data.materials:
                shouldUseMaterial = True
                if bool(face.get('cullFacing',None)) and bool(material.get('cullFacing',None)):
                    if face['cullFacing'] != material['cullFacing']:
                        shouldUseMaterial = False
                elif bool(face.get('cullFacing',None)) or bool(material.get('cullFacing',None)):
                    shouldUseMaterial = False
                
                if bool(face.get('textureFacing',None)) and bool(material.get('textureFacing',None)):
                    if face['textureFacing'] != material['textureFacing']:
                        shouldUseMaterial = False
                elif bool(face.get('textureFacing',None)) or bool(material.get('textureFacing',None)):
                    shouldUseMaterial = False
                    
                if bool(face.get('shade',None)) and bool(material.get('shade',None)):
                    if face['shade'] != material['shade']:
                        shouldUseMaterial = False
                elif bool(face.get('shade',None)) or bool(material.get('shade',None)):
                    shouldUseMaterial = False
                    
                if bool(face.get('tint',None)) and bool(material.get('tint',None)):
                    if face['tint'] != material['tint']:
                        shouldUseMaterial = False
                elif bool(face.get('tint',None)) or bool(material.get('tint',None)):
                    shouldUseMaterial = False
                
                if bool(face.get('overlay',None)) and bool(material.get('overlay',None)):
                    if face['overlay'] != material['overlay']:
                        shouldUseMaterial = False
                elif bool(face.get('overlay',None)) or bool(material.get('overlay',None)):
                    shouldUseMaterial = False
                
                if shouldUseMaterial:
                    theMaterial = material
                    break
            else:
                matName = 'mcmat'
                if face.get('cullFacing',None):
                    matName = matName + '_cf' + face['cullFacing']
                if face.get('textureFacing',None):
                    matName = matName + '_tf' + face['textureFacing']
                if face.get('shade',None):
                    matName = matName + '_s' + str(face['shade'])
                if face.get('tint',None):
                    matName = matName + '_tint'
                if face.get('overlay',None):
                    matName = matName + '_overlay'
                
                theMaterial = bpy.data.materials.new(matName)
                if face.get('cullFacing',None):
                    theMaterial['cullFacing'] = face['cullFacing']
                if face.get('textureFacing',None):
                    theMaterial['textureFacing'] = face['textureFacing']
                if face.get('shade',None):
                    theMaterial['shade'] = face['shade']
                if face.get('tint',None):
                    theMaterial['tint'] = face['tint']
                if face.get('overlay',None):
                    theMaterial['overlay'] = face['overlay']
                    
                
            materialIndex = -1
            i = 0
            for material in mesh.materials:
                if material == theMaterial:
                    materialIndex = i
                    break
                i = i + 1
            else:
                materialIndex = i
                mesh.materials.append(theMaterial)
            meshFace.material_index = materialIndex
                
            i += 1
        uvLayer.active = True
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ExportMinecraftJsonModel(bpy.types.Operator):
    bl_idname = "export_mesh.minecraftjson"
    bl_label = "Export Minecraft Json Model (.json)"
    bl_options = {'REGISTER'}
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".json"
    check_extention = True
    
    @classmethod
    def poll(cls, context):
        return context.object is not None and isinstance(context.object.data, bpy.types.Mesh)
    
    def execute(self, context):
        object = context.object # bpy.context.scene.object.active
        mesh = object.data
        model = {'__comment':'Fair warning, this format is highly likely to change in the future!','name':object.name,'faces':[]}
        
        if mesh.get('useAmbientOcclusion',None) is not None:
            model['useAmbientOcclusion'] = mesh['useAmbientOcclusion']
            
        if mesh.get('inventoryRender3D',None) is not None:
            model['inventoryRender3D'] = mesh['inventoryRender3D']
        
        faces = model['faces']
        
        uvLoop = mesh.uv_layers[0]
        
        for polygon in mesh.polygons:
            face = {'vertices':[]}
            
            material = mesh.materials[polygon.material_index]
            if material.get('cullFacing',None) is not None:
                face['cullFacing'] = material['cullFacing']
            if material.get('textureFacing',None) is not None:
                face['textureFacing'] = material['textureFacing']
            if material.get('shade',None) is not None:
                face['shade'] = material['shade']
            if material.get('tint',None) is not None:
                face['tint'] = material['tint']
            if material.get('overlay',None) is not None:
                face['overlay'] = material['overlay']
            
            i = 0
            for index in polygon.vertices:
                uvData = uvLoop.data[i + polygon.loop_start]
                vert = mesh.vertices[index]
                face['vertices'].append({'position':[vert.co.x,vert.co.z,-vert.co.y],'texcoord':[int(uvData.uv[0]*16),int((1-uvData.uv[1])*16)]})
                i += 1
            faces.append(face)
        
        file = open(self.filepath,'w')
        json.dump(model,file, indent=4, separators=(',', ': '))
        file.close()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportMinecraftJsonModel.bl_idname)
def menu_func_export(self, context):
    self.layout.operator(ExportMinecraftJsonModel.bl_idname)

def register():
    bpy.utils.register_class(ImportMinecraftJsonModel)
    bpy.utils.register_class(ExportMinecraftJsonModel)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_import.append(menu_func_export)
    
def unregister():
    bpy.utils.unregister_class(ImportMinecraftJsonModel)
    bpy.utils.unregister_class(ExportMinecraftJsonModel)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_import.remove(menu_func_export)
