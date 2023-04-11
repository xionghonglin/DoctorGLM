import gradio as gr
from load_quantization import load_int

import numpy

tokenizer, model = load_int('/home/leosher/models/DoctorGLM/DoctorGLM-6B-INT4-6merge.pt',4)
def f(question:str):
    response, _ = model.chat(tokenizer,
                               question,
                               history=[],
                               max_length=2048,
                               repetition_penalty=10.0)
    return(response)

question=gr.inputs.Textbox(label='Your healthy question')

answer=gr.outputs.Textbox(label='DoctorGLM suggestion')


gui=gr.Interface(fn=f,inputs=question,outputs=answer).launch(share=True)