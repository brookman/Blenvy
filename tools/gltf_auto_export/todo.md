- investigate remove_blueprints_list_from_main_scene (could be a case of changes to bpy.data not being applied immediatly)
- investigate clearing of changed_objects_per_scene
- it seems bevy_components does not trigger updates
- undo redo is ignored: ie save, do something, undo it, you still get changes


- for collection instances: 
   * [ ] blueprints export should also take the split/embed mode into account: if a nested collection changes AND embed is active, its container collection should also be exported
   * [ ] level exports should do the same