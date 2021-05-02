# Similarity Plugin

Plugin ini dibuat untuk memeriksa kesamaan peta dengan metode GOF Mapcurves (Hargove et al., 2006) yang berbentuk vektor. Plugin dibuat oleh Pandu Wicaksono dan Takdir. Tidak ada *library* eksternal yang digunakan pada plugin ini kecuali **PyQGIS**. Penghitungan skor kesamaan peta mengimplementasi metode **GOF MapCurve** (Hargrove et. al. (2006) <[doi:10.1007/s10109-006-0025-x](https://doi.org/10.1007/s10109-006-0025-x)> ). Anda dapat mendistribusikan dan memodifikasi plugin ini secara bebas tetapi anda harus mencitasi jurnal Mapcurves dan plugin ini. Untuk informasi lebih lanjut dapat menghubungi Pandu pada email 16.9350@stis.ac.id atau panickspa@gmail.com. Untuk dokumentasi yang lebih lengkap dapat mengunjungi link [Wiki](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/home) di git project ini.

<div align="center">
<img src="https://latex.codecogs.com/svg.latex?GOF_{Mapcurves}=\sum{\frac{C}{C+A}\times\frac{C}{C+B}}"/>
![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/79e0483a7fa9a4ce311b13898bb876fa/image.png)
</div>

## Fitur plugin

Plugin ini dapat memeriksa peta dengan tipe data vektor. Plugin memiliki 3 metode pemeriksaan yaitu:
*  Squential : Membandingkan peta satu persatu
*  Nearest Neighbour : Membandingkan peta dengan menggeser peta ke peta terdekat dengan radius tertentu
*  Wilkerstat : Membandingkan peta dengan kode wilayah
  

## Install the plugin into QGIS directly

Minimum requirement

 - **QGIS 3.10 A Coruna LTS**

Here some steps for installing QGIS

 1. Download this link [main.zip](https://github.com/panickspa/SimilarityPlugin/archive/refs/heads/main.zip)
 2. Open your QGIS
 3. Click *Plugins* menu on Menu Bar

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/db49312a38f98846a2783260826384e2/image.png"/>
</div>

 4. Click *Manage and Install Plugins...* menu

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/91f6e0928694e806a3c1e1c6585a3296/image.png"/>
</div>

 5. Select and click the Install from Zip section

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/18c153a368b85ff528c953b41c6a40a7/image.png"/>
</div>

 6. Click the [...] <img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/7bbdff1818aa2193bc9d46cda71f3d6e/image.png"/> button

 7. Find your plugin installation on step one
 8. Click *Install Plugin* button

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/7ec6af98405d8004e370ff0aa862d36a/image.png"/>
</div>

 9. Move to Installed section by clicking it then check the box on the left of Calculate Similarity Map menu

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/1851181da2b6047918829b6b938b73f7/image.png"/>
</div>

 10. **Plugin ready to use !!!**
    

## How to use plugin
You can access this plugin on menu Vector > Calculate Similarity Map > Check Similarity

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/718c5c233c699148346fbfca67e93293/image.png"/>
</div>

Here some samples for vector based data [sample.zip](https://github.com/panickspa/SimilarityPlugin/blob/main/sample.zip). You can choose the layer on Select Layer 1 combo box and Select Layer 2 combo box in input section. Method can be chosen in method combo box. If you choose Wilkerstat Method, merge center check box will activated. If merge center checked, the calculation process will translate geometry to the center of matching geometry.

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/3469def04e15cc35cfa2d4b5c3b38ef5/InputSection.png"/>
</div>

You can edit threshold, KNN Radius (if you using NN Method), attribute name of score in attribute table of result layer, and result layer suffix name in output section. Threshold is defined in percentile.

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/0b4225586e36a12628e329b92e5b1ab8/OutputSection.png"/>
</div>

After you input all option, you can click calculation button. After calculation be done, save button will enabled. You can save your result to layer in QGIS project with clicking save button.

<div align="center">
<img src="https://github.com/panickspa/SimilarityPlugin/wiki/uploads/1073bcf7f274498a299258747905e19b/image.png"/>
</div>

After calculation excecuted you can preview the result in preview section also before save the result into project.

<div align="center">
![PreviewSection](https://github.com/panickspa/SimilarityPlugin/wiki/uploads/d82c3df65bb9d4937d450407167716b5/PreviewSection.png)
</div>

## How to build from source

This plugin is open source. You can edit and distribute it freely but cite this plugin and Mapcurve (Hargrove et al. 2006) if you are using it to develop another plugin. PyQGIS and OSGeoW environment must be integrated to your IDE if you want use or develop or build from source. Here some command to integrate that from Command Prompt in Windows.

```

    @echo off
    path %PATH%;%QGIS_PATH%\bin
    path %PATH%;%QGIS_PATH%\apps\grass\grass-78\lib
    path %PATH%;%QGIS_PATH%\apps\Qt5\bin
    path %PATH%;%QGIS_PATH%\apps\Python36\Scripts

    set PYTHONPATH=%PYTHONPATH%;%QGIS_PATH%\apps\qgis\python
    set PYTHONHOME=%QGIS_PATH%\apps\Python37  

    start "VisualStudioCode for QGIS" /B  "%VISUAL_STUDIO_CODE_PATH%\code.exe" %YOUR_PLUGIN_REPOSITORY% %*

```

Here some command for integrating terminal with PyQGIS and OSGeoW in Visual Studio Code

```

    @echo off
    call "%QGIS_PATH%\bin\o4w_env.bat"
    call "%QGIS_PATH%\qt5_env.bat"
    call "%QGIS_PATH%\py3_env.bat"
    call "%OSGeo4W64_PATH%\bin\o4w_env.bat"
    call "%OSGeo4W64_PATH%\bin\qt5_env.bat"
    call "%OSGeo4W64_PATH%\bin\py3_env.bat"
    call "%OSGeo4W64_PATH%\bin\gdal-dev-env.bat"
    call "%OSGeo4W64_PATH%\bin\gdal-dev-py3-env.bat"
    call "%OSGeo4W64_PATH%\bin\proj-dev-env.bat"

    @echo on
    pyrcc5 -o resources.py resources.qrc

```

You can deploy the plugin by copying the repository to plugins QGIS folder or you can deploy it with pb_tool with command `pb_tool build`. The new plugin can be operated by restarting the QGIS first or using extension called Plugin Reloader. Plugin Reloader available in QGIS Plugin Repository (see https://plugins.qgis.org/plugins/plugin_reloader/).
