import json
import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty, IntProperty, StringProperty)

from ..constants import TEMPSCENE_PREFIX
from .internals import CollectionsToExport

class AutoExportTracker(PropertyGroup):

    changed_objects_per_scene = {}
    change_detection_enabled = True
    export_params_changed = False

    gltf_settings_backup = None
    last_operator = None
    dummy_file_path = ""

    exports_count : IntProperty(
        name='exports_count',
        description='Number of exports in progress',
        default=0
    ) # type: ignore

   

    @classmethod
    def register(cls):
        bpy.types.WindowManager.auto_export_tracker = PointerProperty(type=AutoExportTracker)
        # register list of exportable collections
        bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

        # setup handlers for updates & saving
        #bpy.app.handlers.save_post.append(cls.save_handler)
        #bpy.app.handlers.depsgraph_update_post.append(cls.deps_update_handler)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        """try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.deps_update_handler)
        except:pass
        try:
            bpy.app.handlers.save_post.remove(cls.save_handler)
        except:pass"""
        del bpy.types.WindowManager.auto_export_tracker
        del bpy.types.WindowManager.exportedCollections

    @classmethod
    def save_handler(cls, scene, depsgraph):
        print("-------------")
        print("saved", bpy.data.filepath)
        # auto_export(changes_per_scene, export_parameters_changed)
        bpy.ops.export_scenes.auto_gltf(direct_mode= True)

        # (re)set a few things after exporting
        # reset wether the gltf export paramters were changed since the last save 
        cls.export_params_changed = False
        # reset whether there have been changed objects since the last save 
        cls.changed_objects_per_scene.clear()
        # all our logic is done, mark this as done

    @classmethod
    def deps_update_handler(cls, scene, depsgraph):
        print("change detection enabled", cls.change_detection_enabled)

        ops = bpy.context.window_manager.operators
        print("last operators", ops)
        for op in ops:
            print("operator", op)
        active_operator = bpy.context.active_operator
        if active_operator:
            print("Operator", active_operator.bl_label, active_operator.bl_idname)
            if active_operator.bl_idname == "EXPORT_SCENE_OT_gltf" and active_operator.gltf_export_id == "gltf_auto_export":
                # we backup any existing gltf export settings, if there were any
                scene = bpy.context.scene
                if "glTF2ExportSettings" in scene:
                    existing_setting = scene["glTF2ExportSettings"]
                    bpy.context.window_manager.gltf_settings_backup = json.dumps(dict(existing_setting))

                # we force saving params
                active_operator.will_save_settings = True
                # we set the last operator here so we can clear the specific settings (yeah for overly complex logic)
                cls.last_operator = active_operator
                #print("active_operator", active_operator.has_active_exporter_extensions, active_operator.__annotations__.keys(), active_operator.filepath, active_operator.gltf_export_id)
            if active_operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf":
                # we force saving params
                active_operator.will_save_settings = True
                active_operator.auto_export = True

        # only deal with changes if we are NOT in the mids of saving/exporting
        if cls.change_detection_enabled:
            # ignore anything going on with temporary scenes
            if not scene.name.startswith(TEMPSCENE_PREFIX):
                print("depsgraph_update_post", scene.name)
                changed_scene = scene.name or ""

            
                #print("-------------")
                if not changed_scene in cls.changed_objects_per_scene:
                    cls.changed_objects_per_scene[changed_scene] = {}
                print("cls.changed_objects_per_scene", cls.changed_objects_per_scene)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                for obj in depsgraph.updates:
                    print("depsgraph update", obj)
                    if isinstance(obj.id, bpy.types.Object):
                        # get the actual object
                        object = bpy.data.objects[obj.id.name]
                        print("changed object", obj.id.name)
                        print("FOO","transforms", obj.is_updated_transform, "geometry", obj.is_updated_geometry)
                        cls.changed_objects_per_scene[scene.name][obj.id.name] = object
                    elif isinstance(obj.id, bpy.types.Material): # or isinstance(obj.id, bpy.types.ShaderNodeTree):
                        print("changed material", obj.id, "scene", scene.name,)
                        material = bpy.data.materials[obj.id.name]
                        #now find which objects are using the material
                        for obj in bpy.data.objects:
                            for slot in obj.material_slots:
                                if slot.material == material:
                                    cls.changed_objects_per_scene[scene.name][obj.name] = obj

                items = 0
                for scene_name in cls.changed_objects_per_scene:
                    items += len(cls.changed_objects_per_scene[scene_name].keys())
                if items == 0:
                    cls.changed_objects_per_scene.clear()
                print("changed_objects_per_scene", cls.changed_objects_per_scene)
        else:
            cls.changed_objects_per_scene.clear()
            
        """depsgraph = bpy.context.evaluated_depsgraph_get()
        for update in depsgraph.updates:
            print("update", update)"""

    def disable_change_detection(self):
        print("disable change detection")
        self.change_detection_enabled = False
        self.__class__.change_detection_enabled = False
        return None
    
    def enable_change_detection(self):
        print("enable change detection")
        self.change_detection_enabled = True
        self.__class__.change_detection_enabled = True
        #FIXME: not sure about these
        self.changed_objects_per_scene.clear()
        self.__class__.changed_objects_per_scene.clear()
        # bpy.context.window_manager.auto_export_tracker.change_detection_enabled = True
        print("bpy.context.window_manager.auto_export_tracker.change_detection_enabled", bpy.context.window_manager.auto_export_tracker.change_detection_enabled)
        return None

    def export_finished(self):
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHH export_finished")
        bpy.context.window_manager.auto_export_tracker.exports_count -= 1
        if bpy.context.window_manager.auto_export_tracker.exports_count == 0:
            #print("preparing to reset change detection")
            # bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)

            self.enable_change_detection()
        return None
