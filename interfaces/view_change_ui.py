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