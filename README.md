# Similarity Plugin

Pengecekan kesamaan peta dengan Metode Mapcurves


# Instalasi

Instalasi bisa dengan mennyalin seluruh fail pada direktori plugin QGIS terinstall
dengan direktori baru
untuk Windows 
   
    %OS_DIRECTORY%\Users\%Username%\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
    
# Development


*  Mengintegrasikan QGIS Environtment ke VS Code menggunakan commanline

        @echo off
        path %PATH%;%QGIS_DIRECTORY%\bin
        path %PATH%;%QGIS_DIRECTORY%\apps\grass\grass-78\lib
        path %PATH%;%QGIS_DIRECTORY%\apps\Qt5\bin
        path %PATH%;%QGIS_DIRECTORY%\apps\Python36\Scripts
        
        set PYTHONPATH=%PYTHONPATH%;%QGIS_DIRECTORY%\apps\qgis\python
        set PYTHONHOME=%QGIS_DIRECTORY%\apps\Python37  
        
        start "VisualStudioCode for QGIS" /B  "%PATH_PROJECT% %*




*  Mengaktifkan environment QGIS dan OSGeoW di VS Code menggunakan terminal

        @echo off
        call "%QGIS_DIRECTORY%\bin\o4w_env.bat"
        call "%QGIS_DIRECTORY&\bin\qt5_env.bat"
        call "%QGIS_DIRECTORY&\bin\py3_env.bat"
        @echo on
        
        optional
        
            @echo off
            call "%OSGeo4W64%\bin\o4w_env.bat"
            call "%OSGeo4W64%\bin\qt5_env.bat"
            call "%OSGeo4W64%\bin\py3_env.bat"
            call "%OSGeo4W64%\bin\gdal-dev-env.bat"
            call "%OSGeo4W64%\bin\gdal-dev-py3-env.bat"
            call "%OSGeo4W64%\bin\proj-dev-env.bat"
            @echo on


*  Cara untuk building code di terminal

        *harus mengaktifkan environment QGIS atau OSGeoW di Vs Code*
        pyrcc5 -o resources.py resources.qrc
        
        *install pb_tool dengan command `pip install pb-tools`*
        `pb_tool deploy`
        
        untuk building dengan output instalasi plugin zip, berikan perintah `pb_tool zip`
        instalasi akan menghasilkan output di direktory .\zip_build
        
# SELAMAT MENCOBA
