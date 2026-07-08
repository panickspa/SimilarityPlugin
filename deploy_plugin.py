import os
import shutil

# Files needed for the plugin
files_to_copy = [
    '__init__.py', 'similarity_plugin.py', 'similarity_plugin_dialog.py', 
    'CaculationModule.py', 'CalculationRasterModule.py', 'wilkerstat_pk_selector.py',
    'warning_plugin_dialog_base.ui', 'simple_warning_dialog.ui', 'wilkerstat_pk_selector.ui',
    'warn_plugin_dialog.py', 'simple_warning_dialog.py',
    'resources.py',
    'metadata.txt', 'icon.png', 'icon-24.png', 'LICENSE'
]

# Target plugin directory
target_dir = ""
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('TARGET_DIR='):
                target_dir = line.split('=', 1)[1].strip()

if not target_dir:
    print("Error: TARGET_DIR not found in .env file.")
    exit(1)

# Create the directory if it doesn't exist
os.makedirs(target_dir, exist_ok=True)

# Copy files
for file in files_to_copy:
    if os.path.exists(file):
        shutil.copy2(file, target_dir)
        print(f"Copied {file}")
    else:
        print(f"Warning: {file} not found")

print(f"\nPlugin successfully deployed to:\n{target_dir}")
