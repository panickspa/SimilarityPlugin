#!/usr/bin/env python3
"""Generate RGB test rasters using band-by-band approach."""

import subprocess
import struct
import os

OUT = "test_rasters"

def create_geotiff(filename, data, ulx, uly, lrx, lry, epsg="EPSG:4326"):
    rows = len(data)
    cols = len(data[0])
    raw_path = filename + '.raw'
    with open(raw_path, 'wb') as f:
        for row in data:
            for val in row:
                f.write(struct.pack('B', int(val)))
    vrt = f'''<VRTDataset rasterXSize="{cols}" rasterYSize="{rows}">
  <SRS>{epsg}</SRS>
  <GeoTransform>{ulx}, {(lrx-ulx)/cols}, 0.0, {uly}, 0.0, {(lry-uly)/rows}</GeoTransform>
  <VRTRasterBand dataType="Byte" band="1" subClass="VRTRawRasterBand">
    <SourceFilename relativeToVRT="1">{os.path.basename(raw_path)}</SourceFilename>
    <ImageOffset>0</ImageOffset>
    <PixelOffset>1</PixelOffset>
    <LineOffset>{cols}</LineOffset>
    <ByteOrder>MSB</ByteOrder>
  </VRTRasterBand>
</VRTDataset>'''
    vrt_path = filename + '.vrt'
    with open(vrt_path, 'w') as f:
        f.write(vrt)
    r = subprocess.run(['gdal_translate', '-of', 'GTiff', '-q', vrt_path, filename],
                       capture_output=True)
    if not os.path.exists(filename):
        print(f"FAILED: {filename}")
        print(r.stderr.decode())
        return False
    os.unlink(raw_path)
    os.unlink(vrt_path)
    return True

# ===== RGB A: Left red (200,30,40), right green (40,180,50) =====
# Create 3 separate single-band GeoTIFFs
r_a = [[200 if c < 5 else 40 for c in range(10)] for r in range(10)]
g_a = [[30 if c < 5 else 180 for c in range(10)] for r in range(10)]
b_a = [[40 if c < 5 else 50 for c in range(10)] for r in range(10)]

create_geotiff(f'{OUT}/rgb_a_b1.tif', r_a, 106.0, -6.0, 106.1, -6.1)
create_geotiff(f'{OUT}/rgb_a_b2.tif', g_a, 106.0, -6.0, 106.1, -6.1)
create_geotiff(f'{OUT}/rgb_a_b3.tif', b_a, 106.0, -6.0, 106.1, -6.1)

# Merge into 3-band, then cleanup singles
r = subprocess.run([
    'gdal_merge.py', '-separate', '-of', 'GTiff', '-q',
    '-o', f'{OUT}/rgb_a.tif',
    f'{OUT}/rgb_a_b1.tif', f'{OUT}/rgb_a_b2.tif', f'{OUT}/rgb_a_b3.tif'
], capture_output=True)
if os.path.exists(f'{OUT}/rgb_a.tif'):
    os.unlink(f'{OUT}/rgb_a_b1.tif')
    os.unlink(f'{OUT}/rgb_a_b2.tif')
    os.unlink(f'{OUT}/rgb_a_b3.tif')
    print("  [OK] rgb_a.tif  (3-band RGB, left=red, right=green)")
else:
    print(f"FAILED merge: {r.stderr.decode()}")

# ===== RGB B: slightly different =====
r_b = [[190 if c < 5 else 40 for c in range(10)] for r in range(10)]
g_b = [[30 if c < 5 else 180 for c in range(10)] for r in range(10)]
b_b = [[40 if c < 5 else 50 for c in range(10)] for r in range(10)]
for r in range(5, 10):
    for c in range(5, 10):
        g_b[r][c] = 160

create_geotiff(f'{OUT}/rgb_b_b1.tif', r_b, 106.0, -6.0, 106.1, -6.1)
create_geotiff(f'{OUT}/rgb_b_b2.tif', g_b, 106.0, -6.0, 106.1, -6.1)
create_geotiff(f'{OUT}/rgb_b_b3.tif', b_b, 106.0, -6.0, 106.1, -6.1)

r = subprocess.run([
    'gdal_merge.py', '-separate', '-of', 'GTiff', '-q',
    '-o', f'{OUT}/rgb_b.tif',
    f'{OUT}/rgb_b_b1.tif', f'{OUT}/rgb_b_b2.tif', f'{OUT}/rgb_b_b3.tif'
], capture_output=True)
if os.path.exists(f'{OUT}/rgb_b.tif'):
    os.unlink(f'{OUT}/rgb_b_b1.tif')
    os.unlink(f'{OUT}/rgb_b_b2.tif')
    os.unlink(f'{OUT}/rgb_b_b3.tif')
    print("  [OK] rgb_b.tif  (3-band RGB, slight diff in lower-right)")
else:
    print(f"FAILED merge: {r.stderr.decode()}")

# ===== Check all files =====
print()
print("=" * 60)
print("  FINAL TEST RASTER FILES")
print("=" * 60)
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    if f.endswith('.tif'):
        bands = 1
        r2 = subprocess.run(['gdalinfo', '-json', fp], capture_output=True)
        if r2.returncode == 0:
            import json
            try:
                info = json.loads(r2.stdout)
                bands = info.get('size', {}).get('bands', 1)
            except:
                pass
        print(f"  {f:35s} {os.path.getsize(fp):>6d} bytes  ({bands} band{'s' if bands > 1 else ''})")
print(f"  Location: {OUT}/")
