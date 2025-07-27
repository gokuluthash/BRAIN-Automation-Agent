import os
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from playwright.async_api import async_playwright
import json

# Load environment variables from .env file
load_dotenv()

# --- 1. Natural Language Processing Module (Gemini) ---


def configure_nlp_module():
    """Configures and returns the Gemini model instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please set it in the .env file.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    return model


def generate_automation_plan(model, user_prompt):
    """
    Sends the user prompt to Gemini and asks for a structured automation plan.
    """
    structured_prompt = f"""
    You are an expert at converting user requests into a structured series of browser automation steps.
    Based on the user's request, provide a JSON array of actions to be executed by Playwright.
    
    The available actions are: "navigate", "click", "type", "extract_text", "end".
    
    - "navigate": Needs a "url" parameter.
    - "click": Needs a "selector" parameter (a CSS selector).
    - "type": Needs a "selector" and a "text" parameter.
    - "extract_text": Needs a "selector" and a "description" for what the text is.
    - "end": Signifies the end of the task and has a "message" parameter to show the user.
    
    User Request: "{user_prompt}"
    
    Provide only the JSON array as your response.
    """

    response = model.generate_content(structured_prompt)

    plan_text = response.text.strip().replace('```json', '').replace('```', '')
    return plan_text

# --- 2. Web Automation Module (Playwright) ---


async def execute_playwright_plan(plan):
    """
    Executes the automation plan using Playwright and pauses at the end.
    """
    results = []
    playwright = None
    browser = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()

        for step in plan:
            action = step.get("action")

            if action == "navigate":
                await page.goto(step.get("url"))
                results.append(f"Navigated to {step.get('url')}")

            elif action == "type":
                await page.locator(step.get("selector")).type(step.get("text"))
                results.append(
                    f"Typed '{step.get('text')}' into '{step.get('selector')}'")

            elif action == "click":
                await page.locator(step.get("selector")).click()
                results.append(f"Clicked on '{step.get('selector')}'")

            elif action == "extract_text":
                text_content = await page.locator(step.get("selector")).inner_text()
                results.append(
                    f"Extracted Data ({step.get('description')}): {text_content}")

            elif action == "end":
                results.append(f"Task finished: {step.get('message')}")
                break

        results.append("\n✅ Automation finished. The browser is now paused.")
        results.append(
            "Close the browser window manually to run a new command.")
        await page.pause()

    except Exception as e:
        results.append(f"An error occurred: {str(e)}")
    finally:
        # This ensures everything closes properly after you manually close the browser.
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

    return "\n".join(results)

# --- Main Controller Logic ---


async def brain_orchestrator(user_prompt):
    """
    Main function to orchestrate the workflow.
    """
    model = configure_nlp_module()
    plan_json_str = generate_automation_plan(model, user_prompt)
    yield f"Generated Plan:\n{plan_json_str}\n\nExecuting..."

    try:
        plan = json.loads(plan_json_str)
        execution_result = await execute_playwright_plan(plan)
        yield execution_result
    except json.JSONDecodeError:
        yield f"Error: Could not decode the plan from the LLM. Raw response:\n{plan_json_str}"
    except Exception as e:
        yield f"An execution error occurred: {str(e)}"

# --- 3. User Interface & Interaction Module (Gradio) ---


# --- 3. User Interface & Interaction Module (Gradio) ---
def create_ui():
    """
    Creates and launches the GitHub dark mode inspired Gradio web interface.
    """
    github_css = """
    body, .gradio-container { background-color: #0d1117; color: #e6edf3; }
    #title h1 { color: #e6edf3; text-align: center; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
    #subtitle p { color: #8b949e; text-align: center; }
    #prompt_input, #output_display { background-color: #010409 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
    .gradio-textbox textarea, .gradio-textbox input { background-color: transparent !important; color: #e6edf3 !important; }
    #run_button { background: #238636 !important; color: #ffffff !important; border: 1px solid #2ea043 !important; font-weight: bold !important; }
    #run_button:hover { background: #2ea043 !important; }
    .gradio-tabs { border-bottom: 1px solid #21262d !important; }
    .gradio-tabitem { background-color: #0d1117 !important; border: none !important; }
    .gradio-tabitem.selected { background-color: #0d1117 !important; border-bottom: 2px solid #f78166 !important; color: #e6edf3 !important; }
    .gradio-accordion { background-color: #161b22 !important; border: 1px solid #30363d !important; }
    footer { display: none !important; }
    """
    theme = gr.themes.Base(font=["-apple-system", "BlinkMacSystemFont",
                           "Segoe UI", "Helvetica", "Arial", "sans-serif"])

    with gr.Blocks(theme=theme, css=github_css, title="B.R.A.I.N") as interface:
        gr.Markdown(
            "# B.R.A.I.N - Browser Retrieval and Automation Intelligent Network", elem_id="title")
        gr.Markdown(
            "An intelligent agent that transforms natural language commands into browser actions.", elem_id="subtitle")

        with gr.Tabs():
            with gr.TabItem("Run Agent"):
                with gr.Row():
                    prompt_input = gr.Textbox(
                        label="Your Command", placeholder="e.g., Go to google.com and search for 'Gemini AI'", scale=4, elem_id="prompt_input")
                    run_button = gr.Button(
                        "Run Automation", variant="primary", scale=1, elem_id="run_button")

                output_display = gr.Textbox(
                    label="Execution Log & Results", lines=15, interactive=False, elem_id="output_display")

                run_button.click(fn=brain_orchestrator,
                                 inputs=prompt_input, outputs=output_display)

                gr.Examples(
                    examples=[
                        "Go to amazon.com and search for wireless headphones",
                        # <-- This is the new command
                        "Go to amazon.com, search for 'smartwatch', and extract the title of the first result",
                        "Go to Github and search for the 'gradio' repository"
                    ],
                    inputs=prompt_input, label="Example Commands"
                )

            with gr.TabItem("Configuration"):
                gr.Markdown("### ⚙️ Agent & API Settings")
                with gr.Accordion("Advanced Options", open=False):
                    api_key_input = gr.Textbox(
                        label="Gemini API Key", placeholder="Enter your key here...", type="password")
                    model_name_input = gr.Dropdown(label="Model", choices=[
                                                   'gemini-1.5-flash-latest', 'gemini-1.0-pro-latest'], value='gemini-1.5-flash-latest')
                    max_steps_slider = gr.Slider(
                        label="Maximum Automation Steps", minimum=5, maximum=50, step=1, value=25)

    interface.launch(share=True)


# --- Entry point of the application ---
if __name__ == "__main__":
    create_ui()
