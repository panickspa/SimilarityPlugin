import re

with open("CaculationModule.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "from qgis.gui import QgsQueryBuilder" in line:
        lines[i] = ""
    elif "import datetime" in line:
        lines[i] = ""
    elif "except KeyError as identifier:" in line:
        lines[i] = line.replace("as identifier", "")
    elif "except ValueError as identifier:" in line:
        lines[i] = line.replace("as identifier", "")
    elif "except NameError as ex:" in line:
        # Check if ex is used in the next lines. On line 828 it is.
        if i not in [828]:
            lines[i] = line.replace("as ex", "")
    elif line.strip() == "except:":
        lines[i] = line.replace("except:", "except Exception:")
    elif "def getSimilarLayer(self):" in line and i > 160:
        lines[i] = ""
        lines[i+1] = ""
        lines[i+2] = ""
    elif "score = float(0)" in line and i > 325 and i < 335:
        lines[i] = ""

with open("CaculationModule.py", "w") as f:
    f.writelines(lines)
