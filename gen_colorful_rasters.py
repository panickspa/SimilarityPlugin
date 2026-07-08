#!/usr/bin/env python3
"""Generate colorful test rasters for similarity plugin testing."""
import subprocess, struct, os

OUT = "colorful_rasters"
os.makedirs(OUT, exist_ok=True)

def create_geotiff(filename, data, ulx, uly, lrx, lry, epsg="EPSG:4326"):
    rows = len(data); cols = len(data[0])
    raw = filename+'.raw'
    with open(raw, 'wb') as f:
        for row in data:
            for v in row: f.write(struct.pack('B', int(v)))
    vrt = f'''<VRTDataset rasterXSize="{cols}" rasterYSize="{rows}">
  <SRS>{epsg}</SRS>
  <GeoTransform>{ulx}, {(lrx-ulx)/cols}, 0.0, {uly}, 0.0, {(lry-uly)/rows}</GeoTransform>
  <VRTRasterBand dataType="Byte" band="1" subClass="VRTRawRasterBand">
    <SourceFilename relativeToVRT="1">{os.path.basename(raw)}</SourceFilename>
    <ImageOffset>0</ImageOffset>
    <PixelOffset>1</PixelOffset>
    <LineOffset>{cols}</LineOffset>
    <ByteOrder>MSB</ByteOrder>
  </VRTRasterBand>
</VRTDataset>'''
    with open(filename+'.vrt','w') as f: f.write(vrt)
    subprocess.run(['gdal_translate','-of','GTiff','-q',filename+'.vrt',filename],capture_output=True)
    os.unlink(raw); os.unlink(filename+'.vrt')

def create_multiband(filename, bands_data, ulx, uly, lrx, lry, epsg="EPSG:4326"):
    rows = len(bands_data[0]); cols = len(bands_data[0][0]); n = len(bands_data)
    raw = filename+'.raw'
    with open(raw, 'wb') as f:
        for r in range(rows):
            for c in range(cols):
                for b in range(n): f.write(struct.pack('B', int(bands_data[b][r][c])))
    bx = ''
    for b in range(n):
        bx += f'''  <VRTRasterBand dataType="Byte" band="{b+1}" subClass="VRTRawRasterBand">
    <SourceFilename relativeToVRT="1">{os.path.basename(raw)}</SourceFilename>
    <ImageOffset>{b}</ImageOffset>
    <PixelOffset>{n}</PixelOffset>
    <LineOffset>{cols * n}</LineOffset>
    <ByteOrder>MSB</ByteOrder>
  </VRTRasterBand>'''
    vrt = f'''<VRTDataset rasterXSize="{cols}" rasterYSize="{rows}">
  <SRS>{epsg}</SRS>
  <GeoTransform>{ulx}, {(lrx-ulx)/cols}, 0.0, {uly}, 0.0, {(lry-uly)/rows}</GeoTransform>
{bx}
</VRTDataset>'''
    with open(filename+'.vrt','w') as f: f.write(vrt)
    subprocess.run(['gdal_translate','-of','GTiff','-co','INTERLEAVE=PIXEL','-q',filename+'.vrt',filename],capture_output=True)
    os.unlink(raw); os.unlink(filename+'.vrt')

# =====================================================================
# 1. COLORFUL CATEGORICAL (32x32, 6 classes with actual colors)
# =====================================================================
# 6 land cover classes with meaningful values
# 10=Water(blue), 20=Forest(green), 30=Agriculture(yellow), 
# 40=Urban(red), 50=Barren(brown), 60=Wetland(purple)
classes = {10:'water',20:'forest',30:'agri',40:'urban',50:'barren',60:'wetland'}

cat_c = []
for r in range(32):
    row = []
    for c in range(32):
        if r < 12 and c < 16:       row.append(10)  # Water - top left
        elif r < 12 and c >= 16:    row.append(20)  # Forest - top right
        elif r < 22 and c < 8:      row.append(30)  # Agri
        elif r < 22 and c < 16:     row.append(40)  # Urban
        elif r < 22 and c >= 16:    row.append(50)  # Barren
        elif r < 22 and c >= 24:    row.append(60)  # Wetland
        elif r >= 22 and c < 16:    row.append(10)  # Water
        else:                       row.append(20)  # Forest
    cat_c.append(row)

cat_d = []
for r in range(32):
    row = []
    for c in range(32):
        if r < 12 and c < 16:       row.append(10)  # Water - same
        elif r < 12 and c >= 16:    row.append(20)  # Forest - same
        elif r < 22 and c < 8:      row.append(30)  # Agri - same
        elif r < 22 and c < 16:     row.append(10)  # DIFFERENT: Urban → Water 
        elif r < 22 and c >= 16:    row.append(50)  # same
        elif r < 22 and c >= 24:    row.append(60)  # same
        elif r >= 22 and c < 16:    row.append(40)  # DIFFERENT: Water → Urban
        else:                       row.append(20)  # same
    cat_d.append(row)

create_geotiff(f'{OUT}/landcover_a.tif', cat_c, 106.0, -6.0, 106.32, -6.32)
create_geotiff(f'{OUT}/landcover_b.tif', cat_d, 106.0, -6.0, 106.32, -6.32)
print("[OK] landcover_a + _b  (32x32, 6 classes, colorful)")

# =====================================================================
# 2. GRADIENT (continuous, smooth color ramp)
# =====================================================================
grad_a = []
for r in range(30):
    row = []
    for c in range(30):
        val = int((r/29)*200 + (c/29)*55)  # gradient from 0-255
        row.append(min(255, val))
    grad_a.append(row)

grad_b = []
for r in range(30):
    row = []
    for c in range(30):
        val = int((r/29)*200 + (c/29)*55)
        if 10 <= r <= 15 and 10 <= c <= 15: val = 200  # hotspot diff
        row.append(min(255, val + 3))  # slight offset
    grad_b.append(row)

create_geotiff(f'{OUT}/gradient_a.tif', grad_a, 106.5, -6.0, 106.8, -6.3)
create_geotiff(f'{OUT}/gradient_b.tif', grad_b, 106.5, -6.0, 106.8, -6.3)
print("[OK] gradient_a + _b  (30x30, smooth gradient)")

# =====================================================================
# 3. NDVI-like (continuous, -1 to 1 range scaled to 0-255)
# =====================================================================
ndvi_a = []
for r in range(25):
    row = []
    for c in range(25):
        # Simulate NDVI pattern: water low, forest high
        dist = ((r-12)**2 + (c-12)**2) ** 0.5
        val = int(200 * (1 - dist/18))  # center high, edges low
        row.append(max(20, min(220, val)))
    ndvi_a.append(row)

ndvi_b = []
for r in range(25):
    row = []
    for c in range(25):
        dist = ((r-12)**2 + (c-12)**2) ** 0.5
        val = int(200 * (1 - dist/18))
        val += 10 if r > 15 else 0  # systematic difference in south
        row.append(max(20, min(220, val)))
    ndvi_b.append(row)

create_geotiff(f'{OUT}/ndvi_a.tif', ndvi_a, 107.0, -6.0, 107.25, -6.25)
create_geotiff(f'{OUT}/ndvi_b.tif', ndvi_b, 107.0, -6.0, 107.25, -6.25)
print("[OK] ndvi_a + _b  (25x25, NDVI-like pattern)")

# =====================================================================
# 4. RAINBOW RGB (32x32 3-band, full color)
# =====================================================================
r_b = [[0]*32 for _ in range(32)]
g_b = [[0]*32 for _ in range(32)]
b_b = [[0]*32 for _ in range(32)]
for row in range(32):
    for col in range(32):
        # Red quadrant
        if row < 16 and col < 16:   r_b[row][col], g_b[row][col], b_b[row][col] = 220, 40, 50
        # Green quadrant
        elif row < 16 and col >= 16: r_b[row][col], g_b[row][col], b_b[row][col] = 40, 200, 60
        # Blue quadrant
        elif row >= 16 and col < 16: r_b[row][col], g_b[row][col], b_b[row][col] = 50, 60, 210
        # Yellow quadrant
        else: r_b[row][col], g_b[row][col], b_b[row][col] = 220, 200, 40

create_multiband(f'{OUT}/rainbow_a.tif', [r_b, g_b, b_b], 108.0, -5.0, 108.32, -5.32)

# Version B: slightly shifted colors
r_b2 = [[0]*32 for _ in range(32)]
g_b2 = [[0]*32 for _ in range(32)]
b_b2 = [[0]*32 for _ in range(32)]
for row in range(32):
    for col in range(32):
        if row < 16 and col < 16:   r_b2[row][col], g_b2[row][col], b_b2[row][col] = 210, 50, 60  # slightly diff red
        elif row < 16 and col >= 16: r_b2[row][col], g_b2[row][col], b_b2[row][col] = 40, 200, 60
        elif row >= 16 and col < 16: r_b2[row][col], g_b2[row][col], b_b2[row][col] = 50, 60, 210
        else: r_b2[row][col], g_b2[row][col], b_b2[row][col] = 200, 180, 40  # slightly diff yellow

create_multiband(f'{OUT}/rainbow_b.tif', [r_b2, g_b2, b_b2], 108.0, -5.0, 108.32, -5.32)
print("[OK] rainbow_a + _b  (32x32 3-band RGB, full color quadrants)")

# =====================================================================
# SUMMARY
# =====================================================================
print(); print("="*55)
print("  COLORFUL TEST RASTERS")
print("="*55)
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT,f)
    if f.endswith('.tif'):
        sz = os.path.getsize(fp)
        bn = subprocess.run(['gdalinfo','-json',fp],capture_output=True,text=True)
        nb = 1
        import json
        try:
            info = json.loads(bn.stdout)
            if 'bands' in str(info): nb = len(info.get('bands',[1]))
        except: pass
        print(f"  {f:25s} {sz:>6d}B  ({nb} band{'s' if nb>1 else ''})")
print(f"  Location: {OUT}/")
