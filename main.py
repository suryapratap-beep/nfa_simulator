import sys
import subprocess
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    print("=" * 60)
    print("🔀 NFA Studio — Interactive Automaton Simulator & Visualizer")
    print("=" * 60)
    print("Starting modern interactive Web UI via Streamlit...")
    print(f"Target app: {app_path}\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path] + sys.argv[1:])
    except KeyboardInterrupt:
        print("\nNFA Studio stopped.")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
