# Similarity Plugin

Checking similarity between two maps with Mapcurves Method.


# Instalation

Copy/clone all fail to QGIS directory
for Windows

    %OS_DIRECTORY%\Users\%Username%\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins

or using pb_tool command
    
    pb_tool deploy
    
# Development


*  Integrating QGIS Env to Vs Code using CMD

        @echo off
        path %PATH%;%QGIS_DIRECTORY%\bin
        path %PATH%;%QGIS_DIRECTORY%\apps\grass\grass-78\lib
        path %PATH%;%QGIS_DIRECTORY%\apps\Qt5\bin
        path %PATH%;%QGIS_DIRECTORY%\apps\Python36\Scripts
        
        set PYTHONPATH=%PYTHONPATH%;%QGIS_DIRECTORY%\apps\qgis\python
        set PYTHONHOME=%QGIS_DIRECTORY%\apps\Python37  
        
        start "VisualStudioCode for QGIS" /B  "%PATH_VSCODE" %PATH_PROJECT% %*




*  Activating QGIS and OSGeoW in VS Code Terminal

        @echo off
        call "%QGIS_DIRECTORY%\bin\o4w_env.bat"
        call "%QGIS_DIRECTORY&\bin\qt5_env.bat"
        call "%QGIS_DIRECTORY&\bin\py3_env.bat"
        @echo off
        call "%OSGeo4W64%\bin\o4w_env.bat"
        call "%OSGeo4W64%\bin\qt5_env.bat"
        call "%OSGeo4W64%\bin\py3_env.bat"
        call "%OSGeo4W64%\bin\gdal-dev-env.bat"
        call "%OSGeo4W64%\bin\gdal-dev-py3-env.bat"
        call "%OSGeo4W64%\bin\proj-dev-env.bat"
        @echo on


*  How to build

        *you must activating QGIS Env in VS Code first*
        pyrcc5 -o resources.py resources.qrc
        
        *install pb_tool dengan command `pip install pb-tools`*
        `pb_tool deploy`
        
        for building with zip output, you can command `pb_tool zip`
        it will be give you an output ./zip_build directory

        
