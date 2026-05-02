import os
import pandas as pd
import gradio as gr
import json
from groq import Groq
from rag_setup import vectorstore
from safety_checker import check_safety

# Initialize Groq Client
client = Groq(api_key=os.environ.get("SUPPORT_AGENT_KEY"))

# --- ULTRA-MODERN PINK NEON CSS ---
custom_css = """
#main-container {
    background: radial-gradient(circle at top, #2d1b2d 0%, #0f0a0f 100%);
}
.header-text {
    text-align: center;
    background: linear-gradient(to right, #ff007f, #ff71ce, #b967ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.2em;
    font-weight: 900;
    text-shadow: 0px 5px 20px rgba(255, 0, 127, 0.4);
    margin-bottom: 5px;
}
.action-btn {
    background: linear-gradient(45deg, #ff007f, #b967ff) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(255, 0, 127, 0.5) !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
    height: 50px !important;
}
.action-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(255, 0, 127, 0.8) !important;
    filter: brightness(1.2);
}
.status-box {
    background: rgba(255, 0, 127, 0.08) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 0, 127, 0.3) !important;
    border-radius: 15px !important;
}
.input-group {
    border-radius: 15px !important;
    border: 1px solid #4a2a4a !important;
    background: #1a101a !important;
}
footer {visibility: hidden}
"""

def process_single_ticket(issue, subject, company):
    if not issue or not subject:
        return "⚠️ Error", "N/A", "Please fill all fields", "N/A", "N/A", "0%", "N/A"

    try:
        # Check safety using BOTH subject and issue
        status, justification = check_safety(f"{subject} {issue}")
        
        context = ""
        if vectorstore:
            docs = vectorstore.similarity_search(issue, k=2)
            context = "\n".join([d.page_content for d in docs])

        prompt = f"""
        Analyze this ticket as a Senior Support Agent:
        Subject: {subject} | Issue: {issue} | Company: {company}
        Knowledge Context: {context}

        Respond ONLY in JSON format:
        {{
            "product_area": "Precise Area",
            "response": "Detailed draft",
            "request_type": "Bug/Query/Emergency",
            "confidence": "99%",
            "priority": "🔴 HIGH"
        }}
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(chat_completion.choices[0].message.content)
        
        return (
            status, 
            res.get("product_area"), 
            res.get("response"), 
            justification,
            res.get("request_type"),
            res.get("confidence"),
            res.get("priority")
        )
    except Exception as e:
        return "❌ Error", "Error", str(e), "Check logs", "Error", "0%", "N/A"

def process_csv(file_obj):
    try:
        df = pd.read_csv(file_obj.name)
        results = []
        for _, row in df.iterrows():
            out = process_single_ticket(row.get('issue', ''), row.get('subject', ''), 'None')
            results.append(out)
        
        result_df = pd.DataFrame(results, columns=["Status", "Area", "Response", "Justification", "Type", "Confidence", "Priority"])
        output_path = "vortex_bulk_results.csv"
        result_df.to_csv(output_path, index=False)
        return output_path, f"✅ Processed {len(df)} tickets successfully!"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# --- GRADIO INTERFACE ---
with gr.Blocks(css=custom_css) as app:
    with gr.Column(elem_id="main-container"):
        gr.Markdown("# VORTEX MAGENTA", elem_classes=["header-text"])
        gr.Markdown("<p style='text-align:center; color: #ffb3d9;'>Premium Cyber-Pink Support Automation</p>")
        
        with gr.Tabs():
            with gr.Tab("🎯 AI Analyzer"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📥 Ticket Input")
                        issue_input = gr.Textbox(label="Issue Description", lines=7, elem_classes=["input-group"], placeholder="Describe the problem...")
                        subject_input = gr.Textbox(label="Subject Line", elem_classes=["input-group"], placeholder="Ticket heading")
                        company_input = gr.Dropdown(choices=["HackerRank", "Claude", "Visa", "None"], label="Target Company", value="None")
                        submit_btn = gr.Button("💖 ANALYZE TICKET", elem_classes=["action-btn"])
                    
                    with gr.Column():
                        gr.Markdown("### 📊 AI Insights")
                        with gr.Row():
                            status_out = gr.Textbox(label="Safety Status", elem_classes=["status-box"])
                            priority_out = gr.Textbox(label="System Priority", elem_classes=["status-box"])
                        
                        area_out = gr.Textbox(label="Product Area", elem_classes=["status-box"])
                        response_out = gr.TextArea(label="Suggested AI Draft", lines=8, elem_classes=["status-box"])
                        
                        with gr.Accordion("🛠 Meta Details", open=False):
                            just_out = gr.Textbox(label="Escalation Reasoning")
                            type_out = gr.Textbox(label="Request Category")
                            conf_out = gr.Textbox(label="AI Confidence Score")

            with gr.Tab("📂 Bulk Mode"):
                gr.Markdown("### 📁 Batch CSV Processing")
                gr.Markdown("Upload a CSV with 'subject' and 'issue' columns.")
                file_input = gr.File(label="Upload CSV File")
                process_btn = gr.Button("🔥 RUN BATCH ANALYSIS", elem_classes=["action-btn"])
                output_file = gr.File(label="Download Processed Results")
                summary_out = gr.Textbox(label="Execution Summary")

        # Fixed: All 7 outputs mapped correctly
        submit_btn.click(
            fn=process_single_ticket, 
            inputs=[issue_input, subject_input, company_input],
            outputs=[status_out, area_out, response_out, just_out, type_out, conf_out, priority_out]
        )
        
        process_btn.click(fn=process_csv, inputs=[file_input], outputs=[output_file, summary_out])

if __name__ == "__main__":
    app.launch(theme=gr.themes.Default(primary_hue="pink", secondary_hue="purple"))