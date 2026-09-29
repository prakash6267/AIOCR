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
        print("[1/2] Installing required packages (streamlit, PyMuPDF, pillow, scikit-learn)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "PyMuPDF", "pillow", "scikit-learn"], check=True)


def main():
    print_banner()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(root_dir, "app.py")

    ensure_dependencies()

    try:
        import create_aiml_docx
        create_aiml_docx.build_all_docx()
        print("📄 Generated benchmark files: AIML_Master_Answer_Key.docx & AIML_Student_Answer_Sheet.docx")
    except Exception as e:
        print(f"Warning building benchmark docx: {e}")

    print("[2/2] Launching Streamlit Web App on http://localhost:8501 ...")
    
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

