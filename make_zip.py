import zipfile
import os
import glob

# Files needed for the plugin
files_to_zip = [
    '__init__.py', 'similarity_plugin.py', 'similarity_plugin_dialog.py', 
    'CaculationModule.py', 'CalculationRasterModule.py', 'wilkerstat_pk_selector.py',
    'warning_plugin_dialog_base.ui', 'simple_warning_dialog.ui', 'wilkerstat_pk_selector.ui',
    'warn_plugin_dialog.py', 'simple_warning_dialog.py',
    'resources.py',
    'metadata.txt', 'icon.png', 'icon-24.png', 'LICENSE'
]

# Create the zip file
with zipfile.ZipFile('similarity_plugin.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
# Add individual files
    for file in files_to_zip:
        if os.path.exists(file):
            zip_path = os.path.join('similarity_plugin', file)
            zipf.write(file, zip_path)
            print(f"Added {file}")
        else:
            print(f"Warning: {file} not found")

    # Recursively add the help directory (excluding .buildinfo)
    if os.path.exists('help'):
        for root, dirs, files in os.walk('help'):
            for file in files:
                # Exclude hidden files (starts with .) and batch files (.bat) to avoid security scan false positives
                if file.startswith('.') or file.endswith('.bat') or file.endswith('.pyc') or 'Makefile' in file:
                    continue
                file_path = os.path.join(root, file)
                zip_path = os.path.join('similarity_plugin', file_path)
                zipf.write(file_path, zip_path)
        print("Added help/ directory (excluding .buildinfo)")

print("Created similarity_plugin.zip successfully!")
