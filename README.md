# Similarity Plugin

Pengecekan kesamaan peta dengan Metode Mapcurves

Instalasi bisa dengan mennyalin seluruh fail pada direktori plugin QGIS terinstall
dengan direktori baru
untuk Windows 
    `
    C:\User\%Username%\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
    `
    
Development

Mengintegrasikan QGIS Environtment ke VS Code menggunakan commanline
`
@echo off
path %PATH%;C:\Program Files\QGIS 3.10\bin
path %PATH%;C:\Program Files\QGIS 3.10\apps\grass\grass-78\lib
path %PATH%;C:\Program Files\QGIS 3.10\apps\Qt5\bin
path %PATH%;C:\Program Files\QGIS 3.10\apps\Python36\Scripts

set PYTHONPATH=%PYTHONPATH%;C:\Program Files\QGIS 3.10\apps\qgis\python
set PYTHONHOME=C:\Program Files\QGIS 3.10\apps\Python37  

start "VisualStudioCode for QGIS" /B  "%PATH_PROJECT% %*

`

Mengaktifkan environment QGIS dan OSGeoW di VS Code menggunakan terminal

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

Cara untuk building code di terminal
    `
    *harus mengaktifkan environment QGIS atau OSGeoW di Vs Code*
    pyrcc5 -o resources.py resources.qrc
    `
