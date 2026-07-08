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
    for file in files_to_zip:
        if os.path.exists(file):
            # Put the files inside a folder named 'similarity_plugin' inside the zip
            zip_path = os.path.join('similarity_plugin', file)
            zipf.write(file, zip_path)
            print(f"Added {file}")
        else:
            print(f"Warning: {file} not found")

print("Created similarity_plugin.zip successfully!")
