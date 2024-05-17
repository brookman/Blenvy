def draw_settings_ui(layout, auto_export_settings):
    controls_enabled = auto_export_settings.auto_export
        
    layout.prop(auto_export_settings, "auto_export")
    layout.separator()

    header, panel = layout.panel("General", default_closed=False)
    header.label(text="General")
    if panel:
        section = panel.box()
        section.enabled = controls_enabled

        op = section.operator("EXPORT_SCENE_OT_gltf", text="Gltf Settings (KEEP 'REMEMBER EXPORT SETTINGS' TOGGLED)")#'glTF 2.0 (.glb/.gltf)')
        #op.export_format = 'GLTF_SEPARATE'
        op.use_selection=True
        op.will_save_settings=True
        op.use_visible=True # Export visible and hidden objects. See Object/Batch Export to skip.
        op.use_renderable=True
        op.use_active_collection = True
        op.use_active_collection_with_nested=True
        op.use_active_scene = True
        op.filepath="____dummy____"
        op.gltf_export_id = "gltf_auto_export" # we specify that we are in a special case

        section.prop(auto_export_settings, "export_scene_settings")    

    header, panel = layout.panel("Change Detection", default_closed=False)
    header.label(text="Change Detection")
    if panel:
        section = panel.box()
        section.enabled = controls_enabled
        section.prop(auto_export_settings, "change_detection", text="Use change detection")

    header, panel = layout.panel("Blueprints", default_closed=False)
    header.label(text="Blueprints")
    if panel:
        section = layout.box()
        section.enabled = controls_enabled
        section.prop(auto_export_settings, "export_blueprints")

        section = section.box()
        section.enabled = controls_enabled and auto_export_settings.export_blueprints

        # collections/blueprints 
        section.prop(auto_export_settings, "collection_instances_combine_mode")
        section.prop(auto_export_settings, "export_marked_assets")
        section.separator()

        section.prop(auto_export_settings, "export_separate_dynamic_and_static_objects")
        section.separator()

        # materials
        section.prop(auto_export_settings, "export_materials_library")
        section = section.box()
        section.enabled = controls_enabled and auto_export_settings.export_materials_library
        #section.prop(auto_export_settings, "materials_path")










    