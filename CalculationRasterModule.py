# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
    QgsRasterBlock,
    QgsProject,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsPointXY,
    Qgis
)

import datetime
import time
import math
import os
import tempfile


class CalculationRasterModule(QObject):
    """
    Calculation Module for raster similarity using MapCurves GOF method.

    Compares two raster layers over their overlapping extent with
    support for different pixel sizes, CRS transformations, and
    multiple comparison modes.

    MapCurves GOF score:
        GOF = (N_match / N_A) * (N_match / N_B)

    Where:
        N_match = pixels matching between both rasters
        N_A     = valid (non-nodata) pixels in raster A within overlap
        N_B     = valid (non-nodata) pixels in raster B within overlap
    """

    killed = False

    def __init__(self):
        super().__init__()
        self.layer = None       # QgsRasterLayer
        self.layer2 = None      # QgsRasterLayer
        self.band_a = 1
        self.band_b = 1
        self.rgb_mode = False
        self.categorical = False  # If True, exact class label comparison
        self.resampling = 'nearest'  # nearest, bilinear, cubic
        self.tolerance = 0.0

    # ------------------------------------------------------------------
    #  Setters
    # ------------------------------------------------------------------

    def setLayers(self, layer: QgsRasterLayer, layer2: QgsRasterLayer,
                  categorical: bool = False,
                  resampling: str = 'nearest'):
        self.layer = layer
        self.layer2 = layer2
        self.categorical = categorical
        self.resampling = resampling

    def setTolerance(self, tolerance: float):
        self.tolerance = tolerance

    # ------------------------------------------------------------------
    #  Lifecycle
    # ------------------------------------------------------------------

    def run(self):
        """Run the calculation in a background thread."""
        start = time.perf_counter()
        if self.killed:
            return

        self.eventTask.emit("Preparing raster similarity calculation ...")

        try:
            score, stats = self._calc_similarity()
            elapsed = time.perf_counter() - start
            bands = stats.get('per_bands', [])
            n_band = len(bands)
            msg = (
                f"Finished in {elapsed:.1f}s | "
                f"Score: {score:.4f} ({n_band} band{'s' if n_band>1 else ''})"
            )
            self.eventTask.emit(msg)
            self.finished.emit([score, stats])
        except Exception as e:
            self.error.emit(f"Raster calculation error: {str(e)}")
            self.eventTask.emit("Error occurred")
            import traceback
            self.error.emit(traceback.format_exc())

    def kill(self):
        self.killed = True

    def alive(self):
        self.killed = False

    # ------------------------------------------------------------------
    #  Core algorithm
    # ------------------------------------------------------------------

    def _calc_similarity(self):
        """Main similarity calculation.

        Handles different pixel sizes (resampling), CRS reprojection,
        categorical/continuous comparison modes.

        Returns (avg_score, stats_dict).
        """
        p1 = self.layer.dataProvider()
        p2 = self.layer2.dataProvider()

        e1 = self.layer.extent()
        e2 = self.layer2.extent()

        # ---- Handle CRS mismatch ----
        crs1 = self.layer.crs()
        crs2 = self.layer2.crs()
        same_crs = crs1 == crs2 or crs1.authid() == crs2.authid()

        if not same_crs:
            self.eventTask.emit(
                f"CRS differ: {crs1.authid()} vs {crs2.authid()} — "
                f"reprojecting on-the-fly"
            )
            transform = QgsCoordinateTransform(crs2, crs1, QgsProject.instance())
            try:
                rect2_geom = QgsGeometry.fromRect(e2)
                rect2_geom.transform(transform)
                e2 = rect2_geom.boundingBox()
            except Exception:
                self.eventTask.emit("Warning: CRS reprojection failed, using original extents")

        # ---- Overlap extent ----
        xmin = max(e1.xMinimum(), e2.xMinimum())
        xmax = min(e1.xMaximum(), e2.xMaximum())
        ymin = max(e1.yMinimum(), e2.yMinimum())
        ymax = min(e1.yMaximum(), e2.yMaximum())

        if xmin >= xmax or ymin >= ymax:
            raise ValueError("Rasters have no overlapping extent")

        overlap_ext = QgsRectangle(xmin, ymin, xmax, ymax)

        # ---- Determine common resolution ----
        rx1 = abs(self.layer.rasterUnitsPerPixelX())
        ry1 = abs(self.layer.rasterUnitsPerPixelY())
        rx2 = abs(self.layer2.rasterUnitsPerPixelX())
        ry2 = abs(self.layer2.rasterUnitsPerPixelY())

        ratio_x = max(rx1, rx2) / min(rx1, rx2) if min(rx1, rx2) > 0 else 1
        needs_resampling = ratio_x > 1.05

        if needs_resampling:
            self.eventTask.emit(
                f"Pixel sizes differ: {rx1:.4g}×{ry1:.4g} vs {rx2:.4g}×{ry2:.4g} — "
                f"resampling using {self.resampling.capitalize()}"
            )
            rx = min(rx1, rx2)
            ry = min(ry1, ry2)
        else:
            rx = (rx1 + rx2) / 2
            ry = (ry1 + ry2) / 2

        cols = int(math.ceil((xmax - xmin) / rx))
        rows = int(math.ceil((ymax - ymin) / ry))

        total_cells = rows * cols
        if total_cells > 100_000_000:
            self.eventTask.emit(
                f"WARNING: Grid {cols}×{rows} = {total_cells:,} cells is very large. "
                f"This may be slow or run out of memory."
            )

        self.eventTask.emit(f"Overlap grid: {cols} × {rows} = {total_cells:,} cells")

        # ---- Auto-detect band count ----
        try:
            band_count = min(
                p1.bandCount() if hasattr(p1, 'bandCount') else 1,
                p2.bandCount() if hasattr(p2, 'bandCount') else 1
            )
        except Exception:
            band_count = 1

        self.eventTask.emit(
            f"Bands detected: {band_count} "
            f"({'multi' if band_count > 1 else 'single'})"
        )

        mode_desc = "Categorical" if self.categorical else "Continuous"
        self.eventTask.emit(f"Mode: {mode_desc} (tolerance={self.tolerance})")

        # ---- Compare each band ----
        per_bands = []
        total_score_sum = 0.0

        for band in range(1, band_count + 1):
            if self.killed:
                break

            self.eventTask.emit(f"Processing Band {band}/{band_count} ...")

            # Read blocks
            block_a = self._read_block(self.layer, band, overlap_ext, cols, rows)
            block_b = self._read_block(self.layer2, band, overlap_ext, cols, rows)
            self.progress.emit(5.0)

            nodata_a = self._get_nodata(p1, band)
            nodata_b = self._get_nodata(p2, band)

            match_count = 0
            total_valid = 0
            step = max(1, total_cells // 100)
            kill_step = max(1, total_cells // 20)

            for row in range(rows):
                if self.killed:
                    break
                for col in range(cols):
                    idx = row * cols + col
                    if idx % kill_step == 0 and self.killed:
                        break

                    v_a = self._read_block_val(block_a, row, col)
                    v_b = self._read_block_val(block_b, row, col)

                    # NODATA
                    if v_a is None or v_b is None:
                        continue
                    if nodata_a is not None and abs(v_a - nodata_a) < 1e-10:
                        continue
                    if nodata_b is not None and abs(v_b - nodata_b) < 1e-10:
                        continue

                    total_valid += 1

                    if self._values_match(v_a, v_b):
                        match_count += 1

                    if idx % step == 0:
                        pct = 5.0 + (idx / total_cells) * 85.0
                        self.progress.emit(min(pct, 90.0))

            self.progress.emit(95.0)

            # Count total valid for each raster individually
            total_valid_a = self._count_band_valid(block_a, nodata_a, rows, cols)
            total_valid_b = self._count_band_valid(block_b, nodata_b, rows, cols)

            if total_valid_a > 0 and total_valid_b > 0:
                band_gof = (match_count / total_valid_a) * (match_count / total_valid_b)
            else:
                band_gof = 0.0

            per_bands.append({
                'band': band,
                'match': match_count,
                'valid': total_valid,
                'valid_a': total_valid_a,
                'valid_b': total_valid_b,
                'gof': round(band_gof, 6),
            })
            total_score_sum += band_gof

            self.eventTask.emit(
                f"  Band {band}: GOF={band_gof:.4f}  "
                f"({match_count:,}/{total_valid:,} match)"
            )

        # ---- Final score = average GOF across bands ----
        avg_score = total_score_sum / max(band_count, 1)
        self.progress.emit(100.0)

        stats = {
            'score_avg': round(avg_score, 6),
            'band_count': band_count,
            'per_bands': per_bands,
            'grid_cols': cols,
            'grid_rows': rows,
            'total_cells': total_cells,
        }

        return avg_score, stats

    # ------------------------------------------------------------------
    #  Block reading
    # ------------------------------------------------------------------

    def _read_block(self, layer, band, extent, cols, rows):
        """Read a raster band as block resampled to target grid."""
        if self.killed:
            return None
        provider = layer.dataProvider()
        block = provider.block(band, extent, cols, rows)
        if block is None or not block.isValid():
            self.eventTask.emit(f"Warning: block read failed for band {band}")
        return block

    def _read_block_val(self, block, row, col):
        """Read single value from block with NODATA check."""
        if block is None or not block.isValid():
            return None
        val = block.value(row, col)
        if val is None:
            return None
        if math.isinf(val) or math.isnan(val):
            return None
        return val

    def _read_rgb_vals(self, blocks, row, col):
        """Read RGB tuple from 3 blocks."""
        vals = []
        for b in blocks:
            v = self._read_block_val(b, row, col)
            if v is None:
                return None
            vals.append(v)
        return tuple(vals)

    def _get_nodata(self, provider, band):
        """Get NODATA value or None."""
        try:
            if provider.sourceHasNoDataValue(band):
                return provider.sourceNoDataValue(band)
        except Exception:
            pass
        return None

    def _count_band_valid(self, block, nodata, rows, cols):
        """Count valid (non-NODATA) pixels in a raster block."""
        if self.killed or block is None or not block.isValid():
            return 0
        count = 0
        for row in range(rows):
            if self.killed:
                break
            for col in range(cols):
                val = block.value(row, col)
                if val is not None and not math.isinf(val) and not math.isnan(val):
                    if nodata is not None and abs(val - nodata) < 1e-10:
                        continue
                    count += 1
        return count

    # ------------------------------------------------------------------
    #  Value comparisons
    # ------------------------------------------------------------------

    def _values_match(self, v_a, v_b) -> bool:
        """Compare pixel values.

        For categorical mode: exact match only.
        For continuous mode: match if |a-b| <= tolerance.
        """
        if self.categorical:
            # Exact class label comparison
            if isinstance(v_a, tuple) and isinstance(v_b, tuple):
                # For RGB categorical: all bands must be exactly equal
                return all(a == b for a, b in zip(v_a, v_b))
            return v_a == v_b

        if self.tolerance > 0:
            if isinstance(v_a, tuple) and isinstance(v_b, tuple):
                return all(
                    abs(a - b) <= self.tolerance
                    for a, b in zip(v_a, v_b)
                )
            return abs(v_a - v_b) <= self.tolerance
        else:
            if isinstance(v_a, tuple) and isinstance(v_b, tuple):
                return all(
                    abs(a - b) < 1e-10
                    for a, b in zip(v_a, v_b)
                )
            return abs(v_a - v_b) < 1e-10

    # ------------------------------------------------------------------
    #  Valid pixel counting
    # ------------------------------------------------------------------

    def _count_valid(self, provider, extent, cols, rows, band, nodata):
        """Count valid (non-NODATA) pixels over the grid."""
        if self.killed:
            return 0

        if provider is None:
            # RGB mode — rough estimate from total pixels
            return cols * rows

        block = self._read_block(
            self.layer if provider == self.layer.dataProvider() else self.layer2,
            band, extent, cols, rows
        )
        if block is None or not block.isValid():
            return 0

        count = 0
        step = max(1, (rows * cols) // 50)
        for row in range(rows):
            if self.killed:
                break
            for col in range(cols):
                val = block.value(row, col)
                if val is not None and not math.isinf(val) and not math.isnan(val):
                    if nodata is not None and abs(val - nodata) < 1e-10:
                        continue
                    count += 1
                if (row * cols + col) % step == 0 and self.killed:
                    break
        return count

    # ------------------------------------------------------------------
    #  Difference raster output
    # ------------------------------------------------------------------

    def _write_diff_raster(self, diff_pixels, rows, cols,
                           extent, pixel_x, pixel_y):
        """Generate a binary difference raster.

        Creates a 2-band raster where:
        - Band 1 = 0 (match) / 255 (mismatch)
        - Band 2 = confidence/value difference (for future use)

        Returns path to the output raster.
        """
        try:
            from osgeo import gdal, osr
            import numpy as np
        except ImportError:
            self.eventTask.emit(
                "GDAL not available for diff raster output. "
                "Install python3-gdal or numpy."
            )
            return None

        self.eventTask.emit("Writing difference raster ...")

        # Build sparse array of differences
        diff_arr = np.ones((rows, cols), dtype=np.uint8) * 255  # default: no data
        for row, col, val in diff_pixels:
            if 0 <= row < rows and 0 <= col < cols:
                diff_arr[row, col] = val

        # Create in-memory or temp file
        out_path = os.path.join(
            tempfile.gettempdir(),
            f"similarity_diff_{int(time.time())}.tif"
        )

        # GDAL setup
        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(out_path, cols, rows, 1, gdal.GDT_Byte)
        
        # GeoTransform
        gt = [extent.xMinimum(), pixel_x, 0,
              extent.yMaximum(), 0, -pixel_y]
        ds.SetGeoTransform(gt)

        # CRS
        crs = self.layer.crs()
        if crs.authid():
            srs = osr.SpatialReference()
            srs.SetFromUserInput(crs.authid())
            ds.SetProjection(srs.ExportToWkt())

        # Write data
        ds.GetRasterBand(1).WriteArray(diff_arr)
        ds.GetRasterBand(1).SetNoDataValue(255)
        ds.GetRasterBand(1).SetDescription("Similarity Difference (0=match, 255=mismatch)")
        ds.FlushCache()
        ds = None

        # Load into QGIS project
        diff_layer = QgsRasterLayer(out_path, "Similarity Difference", "gdal")
        if diff_layer.isValid():
            # Apply styling: green for match, red for mismatch
            fcn = QgsColorRampShader()
            fcn.setColorRampType(QgsColorRampShader.Interpolated)
            lst = [
                QgsColorRampShader.ColorRampItem(0, QColor(0, 180, 0, 180), "Match"),
                QgsColorRampShader.ColorRampItem(255, QColor(200, 40, 40, 200), "Mismatch"),
            ]
            fcn.setColorRampItemList(lst)
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(fcn)
            renderer = QgsSingleBandPseudoColorRenderer(
                diff_layer.dataProvider(), 1, shader
            )
            diff_layer.setRenderer(renderer)

            QgsProject.instance().addMapLayer(diff_layer)
            return f"loaded as '{diff_layer.name()}'", diff_layer
        else:
            return f"saved to {out_path}", None

    # ------------------------------------------------------------------
    #  Signals
    # ------------------------------------------------------------------

    finished = pyqtSignal(list)
    """Emitted with [score, stats_dict]."""

    error = pyqtSignal(str)

    progress = pyqtSignal(float)

    eventTask = pyqtSignal(str)
