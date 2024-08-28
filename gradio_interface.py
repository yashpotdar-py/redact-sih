import gradio as gr
import os
from pii_transform.api.e2e import PiiTextProcessor
from pii_extract.defs import FMT_CONFIG_PLUGIN

examples = []
with open("example.txt", "r") as f:
    examples = f.readlines()
examples_truncated = [example[:50] + "..." for example in examples]
language_choices = {
    "English": "en",
    "Italian": "it",
    "Spanish": "es",
    "Portuguese": "pt",
    "German": "de",
    "French": "fr",
}
language_code = "en"
cache_dir = "app/cache"
os.makedirs(cache_dir, exist_ok=True)
if os.path.isdir(cache_dir):
    gr.Info("Cache directory created at "+cache_dir)
else:
    gr.Warning("Cache directory creation error")

header_string = """## **ReDactify**"""


def change_language(language_selection):
    global language_code
    language_code = language_choices[language_selection]
    gr.Info(f"{language_selection} selected")


def process(text, policy):
    # Create the object, defining the language to use and the policy
    # Further customization is possible by providing a config
    policy = policy.lower()
    if text == "":
        print("Empty text field")
        gr.Warning("No text present")
        return ""

    # Custom config to prevent loading of the Presidio plugin
    proc = PiiTextProcessor(
        lang=language_code, default_policy=policy, config="config.json"
    )

    # Process a text buffer and get the transformed buffer
    outbuf = proc(text)
    return outbuf


def get_full_example(idx):
    return examples[idx]


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown(value=header_string)
        with gr.Column(scale=0, min_width=100):
            pass
        with gr.Column(scale=0, min_width=100):
            logo = gr.Image(
                "image.jpeg",
                height=100,
                width=100,
                show_label=False,
                show_download_button=False,
                show_share_button=False,
                # mask_opacity=1.0,
            )
    with gr.Row():
        with gr.Column(scale=2, min_width=400):
            text_original = gr.Textbox(
                label="Original Text",
                lines=13,
                placeholder="Enter the text you would like to analyze, or select from one of the examples below",
            )
        with gr.Column(scale=0, min_width=25):
            pass
        with gr.Column(scale=0, min_width=150):
            gr.Markdown(
                value="""<p style="text-align: center;">Select Language</p>""")
            lang_picker = gr.Dropdown(
                choices=list(language_choices.keys()),
                label="",
                value=list(language_choices.keys())[0],
                type="value",
                container=False,
            )
            lang_picker.select(
                change_language, inputs=lang_picker, outputs=None)
            gr.Markdown(
                value="""<p style="text-align: center;">Select Policy</p>""")
            annotate_btn = gr.Button(
                value="Annotate", variant="primary", size="sm")
            redact_btn = gr.Button(
                value="Redact", variant="primary", size="sm")
            anonymize_btn = gr.Button(
                value="Synthetic", variant="primary", size="sm")
            placeholder_btn = gr.Button(
                value="Placeholder", variant="primary", size="sm"
            )

        with gr.Column(scale=0, min_width=25):
            pass
        with gr.Column(
            scale=2,
            min_width=400,
        ):
            text_modified = gr.TextArea(
                label="Transformed Text",
                lines=13,
                show_copy_button=True,
                interactive=False,
            )
        annotate_btn.click(
            fn=process, inputs=[text_original,
                                annotate_btn], outputs=text_modified
        )
        redact_btn.click(
            fn=process,
            inputs=[
                text_original,
                gr.Text(value="redact", visible=False),
            ],
            outputs=text_modified,
        )
        anonymize_btn.click(
            fn=process,
            inputs=[
                text_original,
                gr.Text(value="synthetic", visible=False),
            ],
            outputs=text_modified,
        )
        placeholder_btn.click(
            fn=process,
            inputs=[
                text_original,
                gr.Text(value="placeholder", visible=False),
            ],
            outputs=text_modified,
        )
    with gr.Row():
        example_selector = gr.Dropdown(
            examples_truncated, type="index", label="Examples"
        )
        example_selector.select(
            get_full_example, inputs=example_selector, outputs=[text_original]
        )
demo.queue().launch()
