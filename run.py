import os
import sys
import time
import subprocess
import webbrowser

def print_banner():
    print(r"""
================================================================================
    ___    ____        ____  _____ __  ___
   /   |  /  _/       / __ \/ ___//  |/  /
  / /| |  / /  ______/ / / /\__ \/ /|_/ / 
 / ___ |_/ /  /_____/ /_/ /___/ / /  / /  
/_/  |_/___/         \____//____/_/  /_/   

   Student Answer Sheet Evaluator & Reviewer (Streamlit App)
================================================================================
""")

def ensure_dependencies():
    """Ensure streamlit, PyMuPDF, and required Python packages are installed."""
    missing = False
    try:
        import streamlit
        import fitz
    except ImportError:
        missing = True

    if missing:
        print("[1/3] Installing required packages (streamlit, PyMuPDF, pillow, scikit-learn)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "PyMuPDF", "pillow", "scikit-learn"], check=True)

def check_or_start_ollama():
    """Check if Ollama is running, and automatically start it in the background if installed."""
    import urllib.request
    import shutil
    import json

    # 1. Check if Ollama is already active on port 11434
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            if models:
                print(f"[Ollama] Service is RUNNING with models: {', '.join(models[:3])}")
            else:
                print("[Ollama] Service is RUNNING on http://localhost:11434.")
                print("         (Tip: Run 'ollama pull phi3' or 'llama3' for LLM inference, or use built-in NLP fallback)")
            return True
    except Exception:
        pass

    # 2. If not running, attempt to start 'ollama serve' in background if installed
    ollama_path = shutil.which("ollama")
    if ollama_path:
        try:
            print("[Ollama] Starting local Ollama service in the background...")
            subprocess.Popen(
                [ollama_path, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            time.sleep(2)
            print("[Ollama] Service started successfully on http://localhost:11434.")
            return True
        except Exception as e:
            print(f"[Ollama] Notice: Could not auto-launch Ollama ({e}). Built-in NLP fallback will be active.")
            return False
    else:
        print("[Ollama] Notice: Ollama not installed. Built-in resilient Semantic NLP fallback will be active.")
        return False

def main():
    print_banner()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(root_dir, "app.py")

    ensure_dependencies()
    check_or_start_ollama()

    try:
        import create_aiml_docx
        create_aiml_docx.build_all_docx()
        print("Generated benchmark files: AIML_Master_Answer_Key.docx & AIML_Student_Answer_Sheet.docx")
    except Exception as e:
        print(f"Warning building benchmark docx: {e}")

    print("[Launch] Starting Streamlit Web App on http://localhost:8501 ...")
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", app_file,
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]

    print("\n================================================================================")
    print("  Student Answer Sheet Evaluator App is RUNNING!")
    print("  App URL: http://localhost:8501")
    print("================================================================================")
    print("Opening browser automatically...")

    proc = subprocess.Popen(streamlit_cmd, cwd=root_dir)

    time.sleep(2.5)
    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping Streamlit App...")
        proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()

