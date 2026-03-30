"""Build script to create Windows .exe using PyInstaller."""
import subprocess
import sys


def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "TelegramMessageSaver",
        "--add-data", "app;app",
        "--hidden-import", "customtkinter",
        "--hidden-import", "telethon",
        "--hidden-import", "openpyxl",
        "--hidden-import", "fpdf",
        "--hidden-import", "jinja2",
        "--collect-all", "customtkinter",
        "main.py",
    ]
    print("Building executable...")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Check dist/TelegramMessageSaver.exe")


if __name__ == "__main__":
    build()
