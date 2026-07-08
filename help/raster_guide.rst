======================
Raster Module Guide
======================

The Similarity Plugin supports calculating Mapcurves Similarity (Goodness-of-Fit) directly on **Raster** datasets. This allows for cell-by-cell comparison of continuous or categorical raster layers.

How to Use the Raster Module
----------------------------

1. **Select Input Layers**
   In the Input Section, choose your first raster for "Layer 1" and your second raster for "Layer 2". 

2. **Choose the Algorithm**
   In the Method section, select **Raster** from the Algorithm dropdown.

3. **Set Parameters**
   - **Threshold (Tolerance)**: For continuous raster datasets, this defines the fuzzy matching tolerance. Two pixel values are considered a "match" if the absolute difference between them is less than or equal to this tolerance. For exact matching (e.g. categorical data), set this to 0.
   - **Resampling Method**: If your two rasters have different resolutions or pixel sizes, the plugin will resample them to match. You can choose between *Nearest*, *Bilinear*, and *Cubic* resampling.

4. **Advanced Features**
   - **Block-Based Reading**: The raster module processes large datasets efficiently in blocks to prevent memory exhaustion.
   - **NODATA Handling**: Pixels marked as NODATA in either raster are properly ignored during the similarity calculation.
   - **RGB Mode / Multi-band**: When comparing multi-band rasters, the plugin calculates the overall GOF score accounting for all bands.

5. **Execution & Results**
   Click **Calculate** to begin the process. Once finished, the overall **GOF (Goodness-of-Fit)** score will be displayed in the Preview panel, and detailed band-by-band results will be available in the results table. You can also save the results to a CSV file.
