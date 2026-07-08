#!/usr/bin/env python3
"""Generate sample GeoTIFF raster files for similarity plugin testing."""

import subprocess
import struct
import os
import sys

OUT = "test_rasters"
os.makedirs(OUT, exist_ok=True)

def check_gdal():
    """Verify GDAL utilities are available."""
    for cmd in ['gdal_translate', 'gdal_create']:
        r = subprocess.run(['which', cmd], capture_output=True)
        if r.returncode != 0:
            print(f"ERROR: {cmd} not found. Install gdal-bin.")
            sys.exit(1)
    print("GDAL tools: OK")


def create_geotiff(filename, data, ulx, uly, lrx, lry, epsg="EPSG:4326"):
    """Create a GeoTIFF from a 2D list using VRT pipeline."""
    rows = len(data)
    cols = len(data[0]) if rows > 0 else 0

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

    subprocess.run(['gdal_translate', '-of', 'GTiff', '-q', vrt_path, filename],
                   capture_output=True)
    assert os.path.exists(filename), f"Failed to create {filename}"
    os.unlink(raw_path)
    os.unlink(vrt_path)


def create_multiband_geotiff(filename, bands_data, ulx, uly, lrx, lry,
                              epsg="EPSG:4326"):
    """Create multi-band GeoTIFF from list of 2D band arrays."""
    rows = len(bands_data[0])
    cols = len(bands_data[0][0])
    nbands = len(bands_data)

    raw_path = filename + '.raw'
    with open(raw_path, 'wb') as f:
        for r in range(rows):
            for c in range(cols):
                for b in range(nbands):
                    f.write(struct.pack('B', int(bands_data[b][r][c])))

    bands_xml = ''
    for b in range(nbands):
        bands_xml += f'''  <VRTRasterBand dataType="Byte" band="{b+1}">
    <SimpleSource>
      <SourceFilename relativeToVRT="0">{raw_path}</SourceFilename>
      <SourceBand>{b+1}</SourceBand>
      <SourceProperties RasterXSize="{cols}" RasterYSize="{rows}" DataType="Byte"/>
      <SrcRect xOff="0" yOff="0" xSize="{cols}" ySize="{rows}"/>
      <DstRect xOff="0" yOff="0" xSize="{cols}" ySize="{rows}"/>
    </SimpleSource>
  </VRTRasterBand>'''

    vrt = f'''<VRTDataset rasterXSize="{cols}" rasterYSize="{rows}">
  <SRS>{epsg}</SRS>
  <GeoTransform>{ulx}, {(lrx-ulx)/cols}, 0.0, {uly}, 0.0, {(lry-uly)/rows}</GeoTransform>
{bands_xml}
</VRTDataset>'''

    vrt_path = filename + '.vrt'
    with open(vrt_path, 'w') as f:
        f.write(vrt)

    subprocess.run(['gdal_translate', '-of', 'GTiff', '-co', 'INTERLEAVE=PIXEL',
                    '-q', vrt_path, filename], capture_output=True)
    assert os.path.exists(filename), f"Failed to create {filename}"
    os.unlink(raw_path)
    os.unlink(vrt_path)


# =====================================================================
#  1. IDENTICAL — perfect match (score should be 1.0)
# =====================================================================
gdal_create = ['gdal_create', '-of', 'GTiff', '-outsize', '8', '8',
               '-bands', '1', '-burn', '42',
               '-a_srs', 'EPSG:4326',
               '-a_ullr', '106.0', '-6.0', '106.08', '-6.08',
               '-ot', 'Byte']
subprocess.run(gdal_create + [f'{OUT}/identical_a.tif'], capture_output=True)
subprocess.run(['cp', f'{OUT}/identical_a.tif', f'{OUT}/identical_b.tif'])
print("  [OK] identical_a.tif + identical_b.tif  (8×8, value=42)")
print("        → Expected score: 1.0 (perfect match)")

# =====================================================================
#  2. CATEGORICAL — land-cover-like classes
# =====================================================================
cat_a = []
for r in range(25):
    row = []
    for c in range(25):
        if r < 12 and c < 12:      row.append(100)  # forest
        elif r < 12 and c >= 12:   row.append(200)  # water
        elif r >= 12 and c < 12:   row.append(50)   # agriculture
        else:                      row.append(150)  # urban
    cat_a.append(row)

cat_b = []
for r in range(25):
    row = []
    for c in range(25):
        if r < 12 and c < 12:      row.append(100)   # same
        elif r < 12 and c >= 12:   row.append(200)   # same
        elif r >= 12 and c < 12:   row.append(200)   # CHANGED: 50→200
        else:                      row.append(150)   # same
    cat_b.append(row)

create_geotiff(f'{OUT}/categorical_a.tif', cat_a, 106.0, -6.0, 106.25, -6.25)
create_geotiff(f'{OUT}/categorical_b.tif', cat_b, 106.0, -6.0, 106.25, -6.25)
print("  [OK] categorical_a.tif + categorical_b.tif  (25×25, 4 classes)")
print("        → Expected: ~0.56 GOF (one quadrant differs)")

# =====================================================================
#  3. CONTINUOUS — DEM-like elevation with tolerance test
# =====================================================================
cont_a = []
for r in range(20):
    row = []
    for c in range(20):
        val = int(100 + 20 * r/20 + 10 * c/20)
        row.append(val)
    cont_a.append(row)

cont_b = []
for r in range(20):
    row = []
    for c in range(20):
        val = int(100 + 20 * r/20 + 10 * c/20)
        if r == 10 and c == 10:
            val = 130   # spike difference
        if r > 15:
            val += 5    # systematic offset
        row.append(val)
    cont_b.append(row)

create_geotiff(f'{OUT}/continuous_a.tif', cont_a, 106.5, -6.2, 106.7, -6.4)
create_geotiff(f'{OUT}/continuous_b.tif', cont_b, 106.5, -6.2, 106.7, -6.4)
print("  [OK] continuous_a.tif + continuous_b.tif  (20×20, DEM-like)")
print("        → Try tolerance=0 (exact) vs tolerance=5 (fuzzy)")

# =====================================================================
#  4. DIFFERENT RESOLUTION — resampling test (10×10 vs 40×40, same extent)
# =====================================================================
coarse = []
for r in range(10):
    row = []
    for c in range(10):
        row.append(100 if (r + c) % 2 == 0 else 200)
    coarse.append(row)

fine = []
for r in range(40):
    row = []
    for c in range(40):
        row.append(100 if (r//4 + c//4) % 2 == 0 else 200)
    fine.append(row)

create_geotiff(f'{OUT}/resample_coarse.tif', coarse, 107.0, -5.0, 107.2, -5.2)
create_geotiff(f'{OUT}/resample_fine.tif', fine, 107.0, -5.0, 107.2, -5.2)
print("  [OK] resample_coarse.tif (10×10) + resample_fine.tif (40×40)")
print("        → Same extent, different resolution — tests resampling")

# =====================================================================
#  5. RGB — 3-band test
# =====================================================================
r_band = [[200 if c < 5 else 40 for c in range(10)] for r in range(10)]
g_band = [[30 if c < 5 else 180 for c in range(10)] for r in range(10)]
b_band = [[40 if c < 5 else 50 for c in range(10)] for r in range(10)]

# RGB B: similar but with some changes
r_band2 = [[190 if c < 5 else 40 for c in range(10)] for r in range(10)]
g_band2 = [[30 if c < 5 else 180 for c in range(10)] for r in range(10)]
b_band2 = [[40 if c < 5 else 50 for c in range(10)] for r in range(10)]
for r in range(5, 10):
    for c in range(5, 10):
        g_band2[r][c] = 160

create_multiband_geotiff(f'{OUT}/rgb_a.tif', [r_band, g_band, b_band],
                         106.0, -6.0, 106.1, -6.1)
create_multiband_geotiff(f'{OUT}/rgb_b.tif', [r_band2, g_band2, b_band2],
                         106.0, -6.0, 106.1, -6.1)
print("  [OK] rgb_a.tif + rgb_b.tif  (10×10, 3-band RGB)")
print("        → Try with RGB Mode ON vs OFF")

# =====================================================================
#  6. PARTIAL OVERLAP
# =====================================================================
subprocess.run(gdal_create + [
    '-a_ullr', '109.0', '-5.0', '109.5', '-5.5', f'{OUT}/partial_a.tif'
], capture_output=True)
subprocess.run([
    'gdal_create', '-of', 'GTiff', '-outsize', '10', '10',
    '-bands', '1', '-burn', '200',
    '-a_srs', 'EPSG:4326',
    '-a_ullr', '109.3', '-5.3', '109.8', '-5.8',
    '-ot', 'Byte', f'{OUT}/partial_b.tif'
], capture_output=True)
print("  [OK] partial_a.tif + partial_b.tif  (partial overlap)")
print("        → Tests overlap detection")

# =====================================================================
#  7. NO OVERLAP
# =====================================================================
subprocess.run(gdal_create + [
    '-a_ullr', '110.0', '-10.0', '110.5', '-10.5', f'{OUT}/no_overlap_a.tif'
], capture_output=True)
subprocess.run(gdal_create + [
    '-a_ullr', '120.0', '-20.0', '120.5', '-20.5', f'{OUT}/no_overlap_b.tif'
], capture_output=True)
print("  [OK] no_overlap_a.tif + no_overlap_b.tif  (no overlap)")
print("        → Should trigger 'no overlapping extent' error")

# =====================================================================
#  SUMMARY
# =====================================================================
print()
print("=" * 60)
print("  ALL TEST RASTERS CREATED")
print("=" * 60)
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    if f.endswith('.tif'):
        print(f"  {f:35s} {os.path.getsize(fp):>6d} bytes")
print(f"  Location: {OUT}/")
