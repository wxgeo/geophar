import encodings
import os
import sys
import warnings
import zipimport

#paths = os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep)
paths = os.environ.get("PATH", "").split(";")
if DIR_NAME not in paths or os.path.join(DIR_NAME, 'dll') not in paths:
    paths.insert(0, DIR_NAME)
    paths.insert(0, os.path.join(DIR_NAME, 'dll'))
    #os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(paths)
    os.environ["PATH"] = ";".join(paths)
    os.execv(sys.executable, sys.argv)


sys.frozen = True
sys.path = sys.path[:4]

sys.path.append('dll')
sys.path.append(os.path.join(DIR_NAME, 'dll'))
sys.path.append(os.path.join(DIR_NAME, 'wxgeometrie'))
#print(sys.path)
#print(os.environ["PATH"])

os.environ["TCL_LIBRARY"] = os.path.join(DIR_NAME, "tcl")
os.environ["TK_LIBRARY"] = os.path.join(DIR_NAME, "tk")

m = __import__("__main__")
importer = zipimport.zipimporter(INITSCRIPT_ZIP_FILE_NAME)

# The following if/else is copied from ConsoleSetLibPath.py
if INITSCRIPT_ZIP_FILE_NAME != SHARED_ZIP_FILE_NAME:
    moduleName = m.__name__
else:
    name, ext = os.path.splitext(os.path.basename(os.path.normcase(FILE_NAME)))
    moduleName = "%s__main__" % name

code = importer.get_code(moduleName)
exec code in m.__dict__

versionInfo = sys.version_info[:3]
if versionInfo >= (2, 5, 0) and versionInfo <= (2, 6, 4):
    module = sys.modules.get("threading")
    if module is not None:
        module._shutdown()
