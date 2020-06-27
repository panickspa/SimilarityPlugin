# Similarity Plugin

Plugin ini dibuat untuk memeriksa kesamaan peta dengan metode GOF MapCurve (Hargove et al., 2006) yang berbentuk vektor. Plugin dibuat oleh Pandu Wicaksono dan Takdir. Tidak ada *library* eksternal yang digunakan pada plugin ini kecuali **PyQGIS**. Penghitungan skor kesamaan peta mengimplementasi metode **GOF MapCurve** (Hargrove et. al. (2006) <[doi:10.1007/s10109-006-0025-x](https://doi.org/10.1007/s10109-006-0025-x)> ). Anda dapat mendistribusikan dan memodifikasi plugin ini secara bebas tetapi anda harus mencitasi jurnal MapCurve dan plugin ini. Untuk informasi lebih lanjut dapat menghubungi Pandu pada email 16.9350@stis.ac.id atau panickspa@gmail.com. Untuk dokumentasi yang lebih lengkap dapat mengunjungi link [Wiki](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/home) di git project ini.

## Fitur plugin

Plugin ini dapat memeriksa peta dengan tipe data vektor. Plugin memiliki 3 metode pemeriksaan yaitu:
*  Squential : Membandingkan peta satu persatu
*  Nearest Neighbour : Membandingkan peta dengan menggeser peta ke peta terdekat dengan radius tertentu
*  Wilkerstat : Membandingkan peta dengan kode wilayah
  

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


## Cara penggunaan plugin

Anda dapat memilih layer pada *combo box* *Select Layer 2* dan *combo box* *Selec Layer 2* pada *input section* (Masukkan tersebut hanya mendukung layer dengan tipe vektor). Metode untuk pemeriksaan dapat dipilih pada *combo box* *method*. Jika anda memilih *Wilkerstat Method*, katak berlabel *Merge Center* akan aktif. Jika hal tersebut tercentang, proses kalkulasi akan menggeser geometri ke tengah geometri yang sesuai.
<div align="center">
![InputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/3469def04e15cc35cfa2d4b5c3b38ef5/InputSection.png)
</div>
Anda dapat mengedit ambang batas pada menu *Treshold*, radius pergeseran peta pada menu *KNN Radius* (if you useing NN Method), nama attribut skor yang didapat pada tabel attribut dan nama belakang dari *layer* hasil pemeriksaan. Harap isikan *Treshold* dalam **persentil**.

![OutputSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/0b4225586e36a12628e329b92e5b1ab8/OutputSection.png)

Setelah anda mengisikan semua opsi, anda dapat melakukan klik tombol **Calculate** ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/8809206cb30f46d730020bcfb1a934ba/image.png). Setelah pemeriksaan selesai, anda dapat menyimpan dengan mengklik tombol **Save** ![image](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/4fae88aaf29832a2d42f6fe9d1ea3d90/image.png) untuk menyimpannya pada *QGIS Project*.

![ExcecutionSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/7d11bd599f79bd00c3a0bdcbafa6d46e/ExcecutionSection.png)

Setelah pemeriksaan selesai, anda dapat melihat hasilnya pada *preview section* juga sebelum menyimpan hasilnya di *QGIS project*.

![PreviewSection](https://git.stis.ac.id/pandu1881/similarity-plugin/-/wikis/uploads/d82c3df65bb9d4937d450407167716b5/PreviewSection.png)
