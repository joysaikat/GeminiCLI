import gradio as gr
import requests
import os
import shutil

# Configuration
API_URL = "http://127.0.0.1:8000"
DOCS_DIR = "docs"

def query_api(message, history):
    """Sends a question to the FastAPI backend and formats the response."""
    try:
        response = requests.post(f"{API_URL}/query", json={"question": message})
        if response.status_code == 200:
            data = response.json()
            answer = data["answer"]
            sources = data["sources"]
            
            # Format output with sources
            full_response = answer
            if sources:
                full_response += "\n\n**Sources:**\n" + "\n".join([f"- {s}" for s in sources])
            return full_response
        else:
            return f"❌ Error: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Connection Error: Ensure the API server is running at {API_URL}"

def upload_file(files):
    """Saves uploaded files to the docs directory."""
    if not files:
        return "No files selected."
    
    os.makedirs(DOCS_DIR, exist_ok=True)
    saved_files = []
    
    if files:
        for file in files:
            file_name = os.path.basename(file.name)
            dest_path = os.path.join(DOCS_DIR, file_name)
            shutil.copy(file.name, dest_path)
            saved_files.append(file_name)
    
    return f"✅ Successfully uploaded: {', '.join(saved_files)}"

def refresh_knowledge():
    """Triggers the /ingest endpoint on the API."""
    try:
        response = requests.post(f"{API_URL}/ingest")
        if response.status_code == 200:
            return "✅ Knowledge base updated successfully!"
        else:
            return f"❌ Error: {response.json().get('detail', 'Update failed')}"
    except Exception as e:
        return "❌ Connection Error: Ensure the API server is running."

def check_health():
    """Checks the health of the backend API."""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            status = "🟢 Online" if data["status"] == "healthy" else "🔴 Unhealthy"
            db_status = "📦 Database: Found" if data["database_found"] else "❓ Database: Missing"
            return f"{status} | {db_status}"
        return "🔴 Offline"
    except:
        return "🔴 Offline"

# --- UI Layout ---
# In Gradio 6.0, theme and title move to launch()
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Local RAG Assistant")
    gr.Markdown("Query your private documents securely on your M1 Pro.")

    with gr.Row():
        # Left Column: Chat
        with gr.Column(scale=3):
            # In Gradio 6.0, 'type="messages"' is removed as it's the default
            chatbot = gr.Chatbot(height=500, show_label=False)
            msg = gr.Textbox(placeholder="Ask a question about your documents...", show_label=False)
            clear = gr.Button("Clear Chat")

        # Right Column: Management
        with gr.Column(scale=1):
            gr.Markdown("### 🛠️ Management")
            health_display = gr.Label(value=check_health(), label="System Status")
            refresh_btn = gr.Button("🔄 Refresh Knowledge", variant="primary")
            status_msg = gr.Markdown("")
            
            gr.Markdown("---")
            gr.Markdown("### 📂 Upload Documents")
            file_output = gr.File(file_count="multiple", label="Select PDF or TXT")
            upload_btn = gr.Button("📤 Upload to docs/")
            upload_status = gr.Markdown("")

    # --- Event Handlers ---
    def respond(message, chat_history):
        bot_message = query_api(message, chat_history)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    
    refresh_btn.click(
        refresh_knowledge, 
        outputs=[status_msg]
    ).then(
        check_health,
        outputs=[health_display]
    )
    
    upload_btn.click(
        upload_file,
        inputs=[file_output],
        outputs=[upload_status]
    )
    
    clear.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    # Theme and title move here in Gradio 6.0
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        theme=gr.themes.Soft()
    )
