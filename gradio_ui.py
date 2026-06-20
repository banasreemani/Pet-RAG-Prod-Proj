import os
import gradio as gr
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

#API_URL = "http://127.0.0.1:8000/ask" # default to local development
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/ask") # docker development
FEEDBACK_URL = os.getenv(
    "FEEDBACK_URL",
    "http://127.0.0.1:8000/feedback"
)


# def format_context(context):
#     result = "<h2 style='color: #ff7800;'>Relevant Context</h2>\n\n"
#     for doc in context:
#         result += f"<span style='color: #ff7800;'>Source: {doc.metadata['source']}</span>\n\n"
#         result += doc.page_content + "\n\n"
#     print("format_context: ", result)
#     return result

def format_context(sources, contexts):
    result = "<h2 style='color: #ff7800;'>Relevant Context</h2>\n\n"

    if not contexts:
        return result + "*No retrieved context returned*"

    for source, context in zip(sources, contexts):
        result += f"<span style='color: #ff7800;'>Source: {source}</span><br><br>"
        result += context + "<br><br>"

    return result


# def call_pet_api(question):
#     response = requests.post(
#         API_URL,
#         json={"question": question},
#         timeout=120
#     )

#     response.raise_for_status()
#     return response.json()

#---------increase timeout to 300 seconds---------
def call_pet_api(question):
    response = requests.post(
        API_URL,
        json={"question": question},
        timeout=300
    )

    response.raise_for_status()
    return response.json()


def chat(history):
    last_message = history[-1]["content"]

    data = call_pet_api(last_message)

    answer = data["answer"]
    sources = data.get("sources", [])
    contexts = data.get("contexts", [])
    trace_id = data.get("trace_id")

    history.append({"role": "assistant", "content": answer})
    #return history, format_context(sources, contexts)
    state = {
    "question": last_message,
    "answer": answer,
     "trace_id": trace_id
    }

    return history, format_context(sources, contexts), state

   ## history.append({"role": "assistant", "content": answer})
   # return history, format_context(sources)

def send_feedback(state, rating, comment):

    payload = {
        "question": state["question"],
        "answer": state["answer"],
        "rating": rating,
        "comment": comment or "",
        "trace_id": state.get("trace_id")
    }

    # response = requests.post(
    #     "http://pet-rag-api:8000/feedback",
    #     json=payload,
    #     timeout=30
    # )
    response = requests.post(
        FEEDBACK_URL,
        json=payload,
        timeout=30
        )

    response.raise_for_status()

    return f"Feedback saved: {rating}"    


def main():
    def put_message_in_chatbot(message, history):
        return "", history + [{"role": "user", "content": message}]

    theme = gr.themes.Soft(font=["Inter", "system-ui", "sans-serif"])

    with gr.Blocks(title="Pet Care Expert Assistant", theme=theme) as ui:
        gr.Markdown("# 🏢 Pet Care Expert Assistant\nAsk me anything about Pet care!")

        with gr.Row():
            with gr.Column(scale=1):
                chatbot = gr.Chatbot(
                    label="💬 Conversation",
                    height=600,
                    type="messages",
                    show_copy_button=True
                )

                feedback_state = gr.State({})
                feedback_status = gr.Markdown("")

                #---add comment section------------
                feedback_comment = gr.Textbox(
                    label="Feedback comment",
                    placeholder="Optional: tell us what was good or wrong...",
                    lines=2
                )

                
                with gr.Row():
                    thumbs_up = gr.Button("👍 Helpful")
                    thumbs_down = gr.Button("👎 Not Helpful")  

             

                feedback_status = gr.Markdown("")    

                message = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask anything about Pet care...",
                    show_label=False,
                )

               

            with gr.Column(scale=1):
                context_markdown = gr.Markdown(
                    label="📚 Retrieved Context",
                    value="*Retrieved context will appear here*",
                    container=True,
                    height=600,
                )
                

        message.submit(
            put_message_in_chatbot,
            inputs=[message, chatbot],
            outputs=[message, chatbot]
        ).then(
            chat,
            inputs=chatbot,
           # outputs=[chatbot, context_markdown]
            outputs=[chatbot, context_markdown, feedback_state]
        )

        # thumbs_up.click(
        # fn=lambda state: send_feedback(state, "thumbs_up"),
        # inputs=[feedback_state],
        # outputs=[feedback_status]
        # )

        thumbs_up.click(
        fn=lambda state, comment: send_feedback(state, "thumbs_up", comment),
        inputs=[feedback_state, feedback_comment],
        outputs=feedback_status
        )

        # thumbs_down.click(
        #     fn=lambda state: send_feedback(state, "thumbs_down"),
        #     inputs=[feedback_state],
        #     outputs=[feedback_status]
        # )

        thumbs_down.click(
        fn=lambda state, comment: send_feedback(state, "thumbs_down", comment),
        inputs=[feedback_state, feedback_comment],
        outputs=feedback_status
        )

   # ui.launch(inbrowser=True)
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860
        )
print(f"UI available at http://localhost:7860")


if __name__ == "__main__":
    main()