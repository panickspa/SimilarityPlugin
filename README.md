# Similarity Plugin

Plugin ini dibuat untuk memeriksa kesamaan peta dengan metode GOF MapCurve (Hargove et al., 2006) yang berbentuk vektor. Plugin dibuat oleh Pandu Wicaksono dan Takdir. Tidak ada *library* eksternal yang digunakan pada plugin ini kecuali **PyQGIS**. Penghitungan skor kesamaan peta mengimplementasi metode **GOF MapCurve** (Hargrove et. al. (2006) <doi:10.1007/s10109-006-0025-x> ). Anda dapat mendistribusikan dan memodifikasi plugin ini secara bebas tetapi anda harus mencitasi jurnal MapCurve dan plugin ini. Untuk informasi lebih lanjut dapat menghubungi Pandu pada email 16.9350@stis.ac.id atau panickspa@gmail.com.

## Instalasi plugin pada QGIS secara langsung

Batas minimum sistem

  - **QGIS 3.10 A Coruna LTR**

Berikut langkah-langkah untuk menginstal plugin di QGIS

1. *Extract* fail plugin.zip pada sebuat *directory*
2. Buka aplikasi QGIS
3. Klik Menu *Plugins* pada menu bar

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/db49312a38f98846a2783260826384e2/image.png)

4. Klik menu *Manage and Install Plugins...*

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/be7220e560ed1b167fbba5ca4a523b60/image.png)

5. Pilih dan klik *Install from Zip section*

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/18c153a368b85ff528c953b41c6a40a7/image.png)

6. Klik tombol ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/7bbdff1818aa2193bc9d46cda71f3d6e/image.png)
7. Cari fail instalasi plugin pada step pertama.
8. Klik tombol *Install Plugin*

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/b2606bcad2e8f7a8a8dc270aea03896b/image.png)

9. Pindah pada *Installed Section* dengan mengkliknya lalu mencentang kotak yang berada disebelah kiri *Calculate Similarity Map*

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/d9116e47554603ebf9cf186b29d57c58/image.png)

10. **Plugin siap digunakan !!!**


## Instalasi plugin dari kode sumber

Plugin ini *open source*. Anda dapat mengedit dan mendistribusikan ini tetapi harus mencitasi aplikasi *plugin* ini dan Mapcurve (Hargrove et al. 2006) jika anda mengembangkan ini untuk mengembangkan *plugin* yang lain. PyQGIS dan OSGeoW *environment* harus terintegrasi pada IDE yang anda gunakan jika anda ingin menggunakan, mengembangkan, atau *build* dari kode sumber. Berikut beberapa perintah untuk mengintegrasikan dari Command Prompt di Windows.


```

    @echo off
    path %PATH%;%QGIS_PATH%\bin
    path %PATH%;%QGIS_PATH%\apps\grass\grass-78\lib
    path %PATH%;%QGIS_PATH%\apps\Qt5\bin
    path %PATH%;%QGIS_PATH%\apps\Python36\Scripts

    set PYTHONPATH=%PYTHONPATH%;%QGIS_PATH%\apps\qgis\python
    set PYTHONHOME=%QGIS_PATH%\apps\Python37  

    start "VisualStudioCode for QGIS" /B  "%VISUAL_STUDIO_CODE_PATH%\code.exe" %YOUR_PLUGIN_DIRECTORY% %*

```

Berikut beberapa perintah untuk mengintegrasikan *terminal* dengan PyQGIS dan OSGeoW di *Visual Studio Code*

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

Anda dapat memmasang plugin dengan mennyalin fail repositorinya ke folder plugin-plugin QGIS berada atau anda dapat memasangnya dengan perintah `pb_tool build`. Plugin baru tersebut dapat dioperasikan dengan merestart QGIS terlebih dahulu atau menggunakan plugin eksternal yaitu Plugin Reloader. Plugin Reloader tersedia di QGIS Plugin Repository (lihat <https://plugins.qgis.org/plugins/plugin_reloader/>).

## Cara penggunaan plugin

Anda dapat memilih layer pada *combo box* *Select Layer 2* dan *combo box* *Selec Layer 2* pada *input section* (Masukkan tersebut hanya disupport dengan layer bertipe vektor). Metode untuk pemeriksaan dapat dipilih pada *combo box* *method*. Jika anda memilih *Wilkerstat Method*, katak berlabel *Merge Center* akan aktif. Jika hal tersebut tercentang, proses kalkulasi akan menggeser geometri ke tengah geometri yang sesuai.

![InputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/3469def04e15cc35cfa2d4b5c3b38ef5/InputSection.png)

Anda dapat mengedit ambang batas pada menu *Treshold*, radius pergeseran peta pada menu *KNN Radius* (if you useing NN Method), nama attribut skor yang didapat pada tabel attribut dan nama belakang dari *layer* hasil pemeriksaan. Harap isikan *Treshold* dalam **persentil**.

![OutputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/0b4225586e36a12628e329b92e5b1ab8/OutputSection.png)

Setelah anda mengisikan semua opsi, anda dapat melakukan klik tombol **Calculate** ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/8809206cb30f46d730020bcfb1a934ba/image.png). Setelah pemeriksaan selesai, anda dapat menyimpan dengan mengklik tombol **Save** ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/4fae88aaf29832a2d42f6fe9d1ea3d90/image.png) untuk menyimpannya pada *QGIS Project*.

![ExcecutionSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/7d11bd599f79bd00c3a0bdcbafa6d46e/ExcecutionSection.png)

Setelah pemeriksaan selesai, anda dapat melihat hasilnya pada *preview section* juga sebelum menyimpan hasilnya di *QGIS project*.

![PreviewSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/d82c3df65bb9d4937d450407167716b5/PreviewSection.png)

# About Plugin

This plugin is used for checking similarity between two maps vector with MapCurve ( Hargrove et al., 2016 ). Plugin created by Pandu Wicaksono and Takdir. There is no external library included in this plugin except **PyQGIS**. Similarity score implementing **GOF MapCurve** method (Hargrove et. al. (2006) <doi:10.1007/s10109-006-0025-x> ). You can distribute or modifying this plugin freely but you must cite MapCurve journals and this plugin. Further information you can contact Pandu at email 16.9350@stis.ac.id atau panickspa@gmail.com.


## Install the plugin into QGIS directly

Minimum requirement

- **QGIS 3.10 A Coruna LTS**

Here some steps for installing QGIS

1. Extract the plugin.zip fail to an directory
2. Open your QGIS
3. Click *Plugins* menu on Menu Bar

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/db49312a38f98846a2783260826384e2/image.png)

4. Click *Manage and Install Plugins...* menu

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/be7220e560ed1b167fbba5ca4a523b60/image.png)

5. Select and click the Install from Zip section

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/18c153a368b85ff528c953b41c6a40a7/image.png)

6. Click the ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/7bbdff1818aa2193bc9d46cda71f3d6e/image.png) button
7. Find your plugin installation on step one
8. Click *Install Plugin* button

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/b2606bcad2e8f7a8a8dc270aea03896b/image.png)

9. Move to Installed section by clicking it then check the box on the left of Calculate Similarity Map menu

![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/d9116e47554603ebf9cf186b29d57c58/image.png)

10. **Plugin ready to use !!!**
    

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

    start "VisualStudioCode for QGIS" /B  "%VISUAL_STUDIO_CODE_PATH%\code.exe" %YOUR_PLUGIN_DIRECTORY% %*

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

You can deploy the plugin by copying the repository to plugins QGIS folder or you can deploy it with pb_tool with command `pb_tool build`. The new plugin can be operated by restarting the QGIS first or using extension called Plugin Reloader. Plugin Reloader available in QGIS Plugin Repository (see <https://plugins.qgis.org/plugins/plugin_reloader/>). 

## How to use plugin

You can choose the layer on Select Layer 1 combo box and Select Layer 2 combo box in input section (Layer inputation only support vector data type). Method can be chosen in method combo box. If you choose Wilkerstat Method, merge center check box will activated. If merge center checked, the calculation process will translate geometry to the center of matching geometry.

![InputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/3469def04e15cc35cfa2d4b5c3b38ef5/InputSection.png)

You can edit threshold, KNN Radius (if you using NN Method), attribute name of score in attribute table of result layer, and result layer prefix name in output section. Threshold is defined in percentile.

![OutputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/0b4225586e36a12628e329b92e5b1ab8/OutputSection.png)

After you input all option, you can click calculation button ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/8809206cb30f46d730020bcfb1a934ba/image.png). After calculation be done, save button will enabled. You can save your result to layer in QGIS project with clicking save button ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/4fae88aaf29832a2d42f6fe9d1ea3d90/image.png).

![ExcecutionSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/7d11bd599f79bd00c3a0bdcbafa6d46e/ExcecutionSection.png)

After calculation excecuted you can preview the result in preview section also before save the result into project.

![PreviewSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/d82c3df65bb9d4937d450407167716b5/PreviewSection.png)