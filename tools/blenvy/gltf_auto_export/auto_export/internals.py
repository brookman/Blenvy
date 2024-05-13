import bpy

class SceneLink(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="") # type: ignore
    scene: bpy.props.PointerProperty(type=bpy.types.Scene) # type: ignore

class SceneLinks(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of scenes to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = SceneLink) # type: ignore

class CUSTOM_PG_sceneName(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty() # type: ignore
    display: bpy.props.BoolProperty() # type: ignore

class CollectionToExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="") # type: ignore

class BlueprintsToExport(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of collections to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = CollectionToExport) # type: ignore


