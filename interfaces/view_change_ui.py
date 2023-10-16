import gradio as gr
    
def move_to_next_view():
    return (
        gr.update(visible=False),
        gr.update(visible=True),
    )
    
def back_to_previous_view():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
    )

# pre_phase: False, background_setup_phase: True
pre_to_setup_js = """
function pre_to_setup() {
    document.querySelector("#pre_phase").style.display = "none"
    document.querySelector("#background_setup_phase").style.display = "flex"
}
"""

# pre_phase: True, background_setup_phase: False
back_to_pre_js = """
function back_to_pre() {
    document.querySelector("#pre_phase").style.display = "flex"
    document.querySelector("#background_setup_phase").style.display = "none"
}
"""

# background_setup_phase: False, character_setup_phase: True
world_setup_confirm_js = """
function world_setup_confirm() {
    document.querySelector("#background_setup_phase").style.display = "none"
    document.querySelector("#character_setup_phase").style.display = "flex"
}
"""

# background_setup_phase: True, character_setup_phase: False
back_to_background_setup_js = """
function back_to_background_setup() {
    document.querySelector("#background_setup_phase").style.display = "flex"
    document.querySelector("#character_setup_phase").style.display = "none"
}
"""

# pre_phase: False, writing_phase: True
restart_from_story_generation_js = """
function restart_from_story_generation() {
    document.querySelector("#pre_phase").style.display = "none"
    document.querySelector("#writing_phase").style.display = "flex"
}
"""

# writing_phase: False, export_phase: True
story_writing_done_js = """
function story_writing_done() {
    document.querySelector("#writing_phase").style.display = "none"
    document.querySelector("#export_phase").style.display = "flex"
}
"""

# export_phase: False, export_view_phase: True
export_done_js = """
function export_done() {
    document.querySelector("#export_phase").style.display = "none"
    document.querySelector("#export_view_phase").style.display = "flex"
}
"""

# writing_phase: True, export_phase: False
back_to_story_writing_js = """
function back_to_story_writing() {
    document.querySelector("#writing_phase").style.display = "flex"
    document.querySelector("#export_phase").style.display = "none"
}
"""

# pre_phase: True, export_view_phase: False
pre_to_setup_js = """
function pre_to_setup() {
    document.querySelector("#pre_phase").style.display = "flex"
    document.querySelector("#export_view_phase").style.display = "none"
}
"""

# pre_phase: True, export_phase: False
restart_from_export_js = """
function restart_from_export() {
    document.querySelector("#pre_phase").style.display = "flex"
    document.querySelector("#export_phase").style.display = "none"
}
"""

# character_setup_phase: False, writing_phase: True
character_setup_confirm_js = """
function character_setup_confirm() {
    document.querySelector("#character_setup_phase").style.display = "none"
    document.querySelector("#writing_phase").style.display = "flex"
}
"""

# pre_phase: True, export_view_phase: False
restart_from_export_view_js = """
function restart_from_export_view() {
    document.querySelector("#pre_phase").style.display = "flex"
    document.querySelector("#export_view_phase").style.display = "none"
}
"""