import os
import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty)
from blenvy.settings import load_settings, upsert_settings, generate_complete_settings_dict
from .propGroups.prop_groups import generate_propertyGroups_for_components
from .components.metadata import ensure_metadata_for_all_items

# list of settings we do NOT want to save
settings_black_list = ['settings_save_enabled', 'watcher_active']

def save_settings(settings, context):
    if settings.settings_save_enabled:
        settings_dict = generate_complete_settings_dict(settings, ComponentsSettings, [])
        print("save settings", settings, context,settings_dict)
        upsert_settings(settings.settings_save_path, {key: settings_dict[key] for key in settings_dict.keys() if key not in settings_black_list}, overwrite=True)

# helper function to deal with timer
def toggle_watcher(self, context):
    #print("toggling watcher", self.watcher_enabled, watch_schema, self, bpy.app.timers)
    if not self.watcher_enabled:
        try:
            bpy.app.timers.unregister(watch_schema)
        except Exception as error:
            pass
    else:
        self.watcher_active = True
        bpy.app.timers.register(watch_schema)
    save_settings(self, context)

def watch_schema():
    blenvy = bpy.context.window_manager.blenvy
    component_settings = blenvy.components
    #print("watching schema file for changes")
    try:
        stamp = os.stat(component_settings.schema_path_full).st_mtime
        stamp = str(stamp)
        if stamp != component_settings.schemaTimeStamp and component_settings.schemaTimeStamp != "":
            print("FILE CHANGED !!", stamp,  component_settings.schemaTimeStamp)
            # see here for better ways : https://stackoverflow.com/questions/11114492/check-if-a-file-is-not-open-nor-being-used-by-another-process
            """try:
                os.rename(path, path)
                #return False
            except OSError:    # file is in use
                print("in use")
                #return True"""
            #bpy.ops.object.reload_registry()
            # we need to add an additional delay as the file might not have loaded yet
            bpy.app.timers.register(lambda: bpy.ops.object.reload_registry(), first_interval=1)
            component_settings.schemaTimeStamp = stamp
    except Exception as error:
        pass
    return component_settings.watcher_poll_frequency if component_settings.watcher_enabled else None


class ComponentsSettings(PropertyGroup):

    settings_save_path = ".blenvy_components_settings" # where to store data in bpy.texts
    settings_save_enabled: BoolProperty(name="settings save enabled", default=True)# type: ignore

    schema_path: StringProperty(
        name="schema path",
        description="path to the registry schema file",
        default="registry.json",
        update=save_settings
    )# type: ignore

    schema_path_full: StringProperty(
        name="schema full path",
        description="path to the registry schema file",
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.schema_path))
    ) # type: ignore

    watcher_enabled: BoolProperty(name="Watcher_enabled", default=True, update=toggle_watcher)# type: ignore
    watcher_active: BoolProperty(name = "Flag for watcher status", default = False)# type: ignore

    watcher_poll_frequency: IntProperty(
        name="watcher poll frequency",
        description="frequency (s) at wich to poll for changes to the registry file",
        min=1,
        max=10,
        default=1,
        update=save_settings
    )# type: ignore
    
    schemaTimeStamp: StringProperty(
        name="last timestamp of schema file",
        description="",
        default="",
        update=save_settings
    )# type: ignore


    @classmethod
    def register(cls):
        pass
        #bpy.context.window_manager.blenvy.components.watcher_active = False
  
    @classmethod
    def unregister(cls):
        bpy.context.window_manager.blenvy.components.watcher_active = False
        try:
            bpy.app.timers.unregister(watch_schema)
        except Exception as error:
            pass

    def start_schema_watcher(self):
         # start timer
        if not self.watcher_active and self.watcher_enabled:
            self.watcher_active = True
            print("registering function", watch_schema)
            bpy.app.timers.register(watch_schema)

    def load_settings(self):
        settings = load_settings(self.settings_save_path)
        print("component settings", settings)
        if settings is not None:
            self.settings_save_enabled = False # we disable auto_saving of our settings
            try:
                for setting in settings:
                    print("setting", setting, settings[setting])
                    setattr(self, setting, settings[setting])
            except:pass
            try:
                registry = bpy.context.components_registry
                registry.load_schema()
                generate_propertyGroups_for_components()
                ensure_metadata_for_all_items()
            except:pass

        self.settings_save_enabled = True