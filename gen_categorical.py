import struct, os
os.makedirs('test_rasters', exist_ok=True)
# Create 10x10 raw binary with 3 class values in blocks
data = bytearray()
for r in range(10):
    for c in range(10):
        if r < 5 and c < 5:
            data.extend(struct.pack('B', 100))  # Class A
        elif r < 5 and c >= 5:
            data.extend(struct.pack('B', 200))  # Class B
        elif r >= 5 and c < 5:
            data.extend(struct.pack('B', 200))  # Class B
        else:
            data.extend(struct.pack('B', 50))   # Class C
with open('test_rasters/cat_a.raw', 'wb') as f:
    f.write(data)

# Create a slightly different version (one block changed)
data2 = bytearray()
for r in range(10):
    for c in range(10):
        if r < 5 and c < 5:
            data2.extend(struct.pack('B', 100))  # Class A
        elif r < 5 and c >= 5:
            data2.extend(struct.pack('B', 200))  # Class B
        elif r >= 5 and c < 5:
            data2.extend(struct.pack('B', 150))  # Class D (DIFFERENT!)
        else:
            data2.extend(struct.pack('B', 50))   # Class C
with open('test_rasters/cat_b.raw', 'wb') as f:
    f.write(data2)
print("Raw data created")
