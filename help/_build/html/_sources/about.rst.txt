About Plugin
=====================

Mapcurve (Hargrove et al. 2016)
-------------------------------
    Mapcurves adalah metode untuk mengetahui persamaan peta dengan menggunakan metode GOF. Metode Mapcurves dikembangkan oleh Hargrove et al. (2006). Mapcurves dapat memberikan tingkat kesamaan peta tanpa memperhatikan resolusi gambar. Mapcurves juga dapat diaplikasikan pada peta berbentuk raster dan vektor. Berikut rumus dan konsep pada metode Mapcurves.
    
    〖GOF〗_mapcurves= ∑〖Intersection/(B)×Intersection/(A)〗
    
    Mapcurve memiliki konsep perbandingan luas irisan peta dengan peta yang dibandingkan. Irisan tersebut disebut sebagai insideness yang menunjukkan kesepakatan persamaan peta. Ketika luas irisan peta tersebut semakin tinggi maka peta perbandingan peta akan dianggap semakin mirip.

Squential
-------------------------------
    Metode squential akan menggunakan penyaringan kelompok peta pada layer dengan batas kotak pada setiap fitur peta. Kotak tersebut akan menyaring peta yang berpotongan dengan kotak tersebut. Berikut ilustrasi untuk penyaringan peta dengan metode tersebut. Algoritma akan lebih cepat dengan dari O(nC2) pada prototipe pertama menjadi O(n.m). Variabel n adalah jumlah peta yang akan dilakukan pemeriksaan pada layer pertama dan Variabel m adalah jumlah peta yang disaring dengan kotak

Nearest Neighbour
-------------------------------
    Metode Nearest Neighbour memiliki konsep penyaringan batas kotak juga tetapi metode ini menggunakan batas kotak yang ditentukan. Batas kotak tersebut akan dibuat sesuai radius yang diinginkan pada pengguna. Radius tersebut akan menunjukkan berapa jauh toleransi pergeseran data peta yang dibandingkan.

    Prinsip kotak tersebut seperti mengelompokkan data layer kedua menjadi kelompok yang terdekat pada fitur yang akan dibandingkan pada layer pertama. Kelompok tersebut akan menjadi fitur yang dibandingkan seperti pada metode squential. Selanjutnya fitur peta yang akan dibandingkan digeser ke tengah-tengah peta yang dikelompokkan untuk mencari skor tingkat kemiripannya dengan metode Mapcurves.

Wilkerstat
-------------------------------
    Metode Wilkerstat menggunakan matching primary key dalam sistem database Wilkersat yaitu provno, kabkotno, kecno, dan desano. Struktur tersebut dapat dilihat di https://sig.bps.go.id/