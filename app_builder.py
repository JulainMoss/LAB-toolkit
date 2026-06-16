import PyInstaller.__main__
import subprocess
import argparse

parser = argparse.ArgumentParser(description="LAB Toolkit App compiler")
parser.add_argument('--onefile', action='store_true', help='One-file mode (single .exe file)')
parser.add_argument('--noconsole', action='store_true', help='Hide console (Windows only)')
parser.add_argument('--icon', type=str, help='Path to icon file (.ico)')
parser.add_argument('--bump', type=str, help='Bump version' , choices=['patch', 'minor', 'major'], default=None)
args = parser.parse_args()

pyinstaller_args = ['main.py']
if args.onefile:
    pyinstaller_args.append('--onefile')
if args.noconsole:
    pyinstaller_args.append('--noconsole')
if args.icon:
    pyinstaller_args.append(f'--icon={args.icon}')

PyInstaller.__main__.run(pyinstaller_args)

uv_args = ["uv", "version", "--bump", args.bump] if args.bump else ["uv", "version"]


subprocess.run(uv_args, capture_output=True, text=True)

print("Compilation finished!")