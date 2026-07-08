#!/usr/bin/env python3
"""Generate realistic land-cover-like rasters with natural patterns."""
import struct, os, math, random

OUT = "realmap_rasters"
os.makedirs(OUT, exist_ok=True)

def make_tif(filename, data, ulx, uly, lrx, lry):
    rows, cols = len(data), len(data[0])
    raw = filename+'.raw'
    with open(raw,'wb') as f:
        for row in data:
            for v in row: f.write(struct.pack('B', int(v)))
    vrt = f'''<VRTDataset rasterXSize="{cols}" rasterYSize="{rows}">
  <SRS>EPSG:4326</SRS>
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
    import subprocess
    subprocess.run(['gdal_translate','-of','GTiff','-q',filename+'.vrt',filename])
    os.unlink(raw); os.unlink(filename+'.vrt')

def noise2d(w, h, scale=8.0):
    """Simple value noise for natural patterns."""
    val = [[0.0]*w for _ in range(h)]
    for octave in range(3):
        freq = 2**octave
        sx, sy = scale/freq, scale/freq
        for y in range(h):
            for x in range(w):
                nx, ny = x/sx, y/sy
                v = (math.sin(nx*12.9898+ny*78.233)*43758.5453)%1
                val[y][x] += v / (octave+1)
    # Normalize
    mn = min(min(r) for r in val)
    mx = max(max(r) for r in val)
    return [[(v-mn)/(mx-mn) for v in r] for r in val]

# ============================================================
# 1. LANDCOVER MAP (128x128, 7 natural classes) — 106.0,-6.0
# ============================================================
W, H = 128, 128
seed = 42
random.seed(seed)

# Generate terrain features with multiple noise layers
elevation = noise2d(W, H, 12.0)
moisture = noise2d(W, H, 20.0)

# Create realistic land cover classes based on elevation + moisture
lca = []
for r in range(H):
    row = []
    for c in range(W):
        e = elevation[r][c]
        m = moisture[r][c]
        
        # Simulate geography:
        # Coastline effect (edge = water)
        dx = min(c, W-1-c) / (W/2)
        dy = min(r, H-1-r) / (H/2)
        edge = min(dx, dy)
        
        # Rivers (linear moisture features)
        river = 0
        if 40 < c < 50: river = 1
        if 85 < c < 92 and r > 60: river = 1
        if abs(c - 30) < 3 and 50 < r < 90: river = 1
        
        if edge < 0.08 or (m > 0.85 and e < 0.4):
            cls = 10  # Deep water
        elif river:
            cls = 10  # River
        elif m > 0.75 and e > 0.6:
            cls = 20  # Dense forest
        elif m > 0.55 and e > 0.4:
            cls = 25  # Mixed forest
        elif m > 0.4 and e > 0.3:
            cls = 30  # Shrub/grassland
        elif (m > 0.3 and e > 0.2) or (m > 0.5 and e < 0.4):
            cls = 40  # Agriculture
        elif m > 0.2:
            cls = 50  # Urban/bare
        else:
            cls = 60  # Barren/dry
        
        # Add some noise for realism
        if random.random() < 0.02:
            neighbors = [10, 20, 25, 30, 40, 50, 60]
            cls = random.choice(neighbors)
        
        row.append(cls)
    lca.append(row)

# Version B: change ~15% of pixels (simulate different season/classification)
lcb = [row[:] for row in lca]
changes = 0
for r in range(H):
    for c in range(W):
        if random.random() < 0.15:
            # Shift by 1 class in either direction
            v = lcb[r][c]
            if v == 10: lcb[r][c] = 40  # water→agri (recede)
            elif v == 20: lcb[r][c] = 25  # dense→mixed
            elif v == 25: lcb[r][c] = 30  # mixed→shrub
            elif v == 30: lcb[r][c] = 40  # shrub→agri
            elif v == 40: lcb[r][c] = 50 if random.random()<0.5 else 30  # agri→urban/shrub
            elif v == 50: lcb[r][c] = 40  # urban→agri (regrowth)
            elif v == 60: lcb[r][c] = 50  # barren→urban
            changes += 1

make_tif(f'{OUT}/landcover_map_a.tif', lca, 106.0, -6.0, 106.5, -6.5)
make_tif(f'{OUT}/landcover_map_b.tif', lcb, 106.0, -6.0, 106.5, -6.5)
print(f"[OK] landcover_map  (128x128, ~{changes} pixels differ, ~{changes/128/128*100:.0f}%)")

# ============================================================
# 2. ELEVATION MAP (100x100, continuous) — 107.0,-6.0
# ============================================================
elev = noise2d(100, 100, 10.0)
ev1 = [[int(v*200)+30 for v in row] for row in elev]

# Version B: add erosion/subsidence in one region
ev2 = [row[:] for row in ev1]
for r in range(100):
    for c in range(100):
        # Subsidence in southwest quadrant
        if r > 60 and c < 40:
            ev2[r][c] = max(20, ev2[r][c] - int((r-60)/40*40))
        # Uplift in northeast
        if r < 30 and c > 70:
            ev2[r][c] = min(250, ev2[r][c] + 20)

make_tif(f'{OUT}/elevation_a.tif', ev1, 107.0, -6.0, 107.4, -6.4)
make_tif(f'{OUT}/elevation_b.tif', ev2, 107.0, -6.0, 107.4, -6.4)
print("[OK] elevation  (100x100, continuous with erosion/uplift)")

# ============================================================
# 3. URBAN CHANGE MAP (80x80) — Shows expansion pattern
# ============================================================
# Year 2000
urb1 = []
for r in range(80):
    row = []
    for c in range(80):
        # City center
        dist = ((r-30)**2 + (c-35)**2)**0.5
        if dist < 12:  row.append(80)  # Dense urban
        elif dist < 18: row.append(70)  # Suburban
        elif dist < 25: row.append(50)  # Peri-urban
        elif noise2d(80,80,15)[r][c] < 0.3: row.append(40)  # Farmland
        else: row.append(30)  # Forest
    urb1.append(row)

# Year 2025 — urban expanded
urb2 = [row[:] for row in urb1]
for r in range(80):
    for c in range(80):
        d = ((r-30)**2 + (c-35)**2)**0.5
        # Urban sprawl: 12→15, 18→22
        if d < 15: 
            if urb2[r][c] < 80: urb2[r][c] = 80
        elif d < 22:
            if urb2[r][c] < 70: urb2[r][c] = 70
        # New highway
        if (10 < r < 70 and 50 < c < 55) and urb2[r][c] < 70:
            urb2[r][c] = 70

make_tif(f'{OUT}/urban_2000.tif', urb1, 108.0, -5.0, 108.4, -5.4)
make_tif(f'{OUT}/urban_2025.tif', urb2, 108.0, -5.0, 108.4, -5.4)
print("[OK] urban change  (80x80, urban sprawl simulation)")

# ============================================================
# SUMMARY
# ============================================================
import subprocess
print(); print("="*55)
print("  REALISTIC TEST RASTERS")
print("="*55)
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT,f)
    if f.endswith('.tif'):
        print(f"  {f:25s} {os.path.getsize(fp):>6d}B")
print(f"  Location: {OUT}/")
