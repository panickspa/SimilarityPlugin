# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
    QgsRasterBlock,
    QgsPointXY,
    Qgis
)

import datetime
import time
import math


class CalculationRasterModule(QObject):
    """
    Calculation Module for checking raster similarity using MapCurves GOF method.

    Compares two raster layers over their overlapping extent pixel-by-pixel.

    Supports:
    - Single-band comparison (categorical or continuous with tolerance)
    - Multi-band RGB comparison (3-band exact or tolerance match)
    - Configurable tolerance for continuous data
    - Block-based reading (faster than per-pixel identify)

    MapCurves GOF score:
        GOF = (N_match / N_A) * (N_match / N_B)

    Where:
        N_match = pixels matching between both rasters
        N_A     = valid (non-nodata) pixels in raster A within overlap
        N_B     = valid (non-nodata) pixels in raster B within overlap
    """

    killed = False
    layer: QgsRasterLayer
    layer2: QgsRasterLayer

    def __init__(self):
        super().__init__()
        self.layer = None
        self.layer2 = None
        self.band_a = 1       # Raster 1 band index for single-band comparison
        self.band_b = 1       # Raster 2 band index for single-band comparison
        self.rgb_mode = False # If True, compare all 3 bands (RGB)
        self.tolerance = 0.0  # Tolerance for continuous data comparison

    # ------------------------------------------------------------------
    #  Setters
    # ------------------------------------------------------------------

    def setLayers(self, layer: QgsRasterLayer, layer2: QgsRasterLayer,
                  band_a: int = 1, band_b: int = 1,
                  rgb_mode: bool = False):
        """Set input raster layers and band configuration.

        :param layer: First raster layer
        :param layer2: Second raster layer
        :param band_a: Band index for layer 1 (1-based)
        :param band_b: Band index for layer 2 (1-based)
        :param rgb_mode: If True, compare bands 1,2,3 as RGB
        """
        self.layer = layer
        self.layer2 = layer2
        self.band_a = band_a
        self.band_b = band_b
        self.rgb_mode = rgb_mode

    def setTolerance(self, tolerance: float):
        """Set tolerance for continuous value comparison.

        Pixels match if |val_A - val_B| <= tolerance.
        For RGB mode, all 3 bands must be within tolerance.
        """
        self.tolerance = tolerance

    # ------------------------------------------------------------------
    #  Lifecycle
    # ------------------------------------------------------------------

    def run(self):
        """Run the calculation in a background thread."""
        start = time.perf_counter()
        if self.killed:
            return

        self.eventTask.emit("Calculating raster similarity ...")

        try:
            score, stats = self._calc_similarity()
            elapsed = time.perf_counter() - start
            self.eventTask.emit(
                f"Finished in {elapsed:.1f}s | "
                f"Score: {score:.4f} | "
                f"Match: {stats['match']:,}/{stats['common']:,} valid pixels"
            )
            self.finished.emit([score, stats])
        except Exception as e:
            self.error.emit(f"Raster calculation error: {str(e)}")
            self.eventTask.emit("Error occurred")
            import traceback
            self.error.emit(traceback.format_exc())

    def kill(self):
        """Request graceful termination."""
        self.killed = True

    def alive(self):
        """Clear kill flag."""
        self.killed = False

    # ------------------------------------------------------------------
    #  Core algorithm
    # ------------------------------------------------------------------

    def _calc_similarity(self):
        """Main similarity calculation.

        Returns (score, stats_dict).
        """
        p1 = self.layer.dataProvider()
        p2 = self.layer2.dataProvider()

        e1 = self.layer.extent()
        e2 = self.layer2.extent()

        # ---- Overlap extent ----
        xmin = max(e1.xMinimum(), e2.xMinimum())
        xmax = min(e1.xMaximum(), e2.xMaximum())
        ymin = max(e1.yMinimum(), e2.yMinimum())
        ymax = min(e1.yMaximum(), e2.yMaximum())

        if xmin >= xmax or ymin >= ymax:
            raise ValueError("Rasters have no overlapping extent")

        overlap_ext = QgsRectangle(xmin, ymin, xmax, ymax)

        # ---- Determine common grid resolution (finer of the two) ----
        rx1 = abs(self.layer.rasterUnitsPerPixelX())
        ry1 = abs(self.layer.rasterUnitsPerPixelY())
        rx2 = abs(self.layer2.rasterUnitsPerPixelX())
        ry2 = abs(self.layer2.rasterUnitsPerPixelY())

        rx = min(rx1, rx2)
        ry = min(ry1, ry2)

        cols = int(math.ceil((xmax - xmin) / rx))
        rows = int(math.ceil((ymax - ymin) / ry))

        total_cells = rows * cols
        self.eventTask.emit(
            f"Overlap grid: {cols} × {rows} = {total_cells:,} cells "
            f"@ {rx:.4g} × {ry:.4g} {self.layer.crs().ellipsoidAcronym() or 'units'}"
        )

        # ---- Read blocks from both rasters (resampled to common grid) ----
        self.eventTask.emit("Reading raster data ...")
        # Report read progress (0-20%)
        self.progress.emit(5.0)

        # Read blocks — initialize all variables to avoid unbound warnings
        block_a = None
        block_b = None
        blocks_a = None
        blocks_b = None

        if self.rgb_mode:
            blocks_a = [
                self._read_block(self.layer, b, overlap_ext, cols, rows)
                for b in (1, 2, 3)
            ]
            blocks_b = [
                self._read_block(self.layer2, b, overlap_ext, cols, rows)
                for b in (1, 2, 3)
            ]
        else:
            block_a = self._read_block(self.layer, self.band_a, overlap_ext, cols, rows)
            block_b = self._read_block(self.layer2, self.band_b, overlap_ext, cols, rows)

        self.progress.emit(20.0)

        # ---- NODATA values ----
        nodata_a = self._get_nodata(p1, self.band_a if not self.rgb_mode else 1)
        nodata_b = self._get_nodata(p2, self.band_b if not self.rgb_mode else 1)

        self.eventTask.emit("Comparing pixels ...")

        # ---- Iterate over common grid ----
        match_count = 0
        total_valid = 0  # pixels where both rasters have valid data

        step = max(1, total_cells // 100)  # report ~100 progress updates
        check_kill_step = max(1, total_cells // 20)

        for row in range(rows):
            if self.killed:
                break

            for col in range(cols):
                idx = row * cols + col

                # Periodic kill check
                if idx % check_kill_step == 0 and self.killed:
                    break

                # Read values from both rasters
                if self.rgb_mode:
                    v_a = self._read_rgb_vals(blocks_a, row, col)
                    v_b = self._read_rgb_vals(blocks_b, row, col)
                else:
                    v_a = self._read_block_val(block_a, row, col)
                    v_b = self._read_block_val(block_b, row, col)

                # NODATA check
                if v_a is None or v_b is None:
                    continue

                total_valid += 1

                # Compare
                if self._values_match(v_a, v_b):
                    match_count += 1

                # Progress
                if idx % step == 0:
                    pct = 20.0 + (idx / total_cells) * 70.0
                    self.progress.emit(min(pct, 90.0))

        self.progress.emit(95.0)

        # ---- Compute GOF score ----
        # Need total valid pixels for each raster individually
        total_a_valid = self._count_valid(p1, overlap_ext, cols, rows,
                                          self.band_a if not self.rgb_mode else 1,
                                          nodata_a)
        total_b_valid = self._count_valid(p2, overlap_ext, cols, rows,
                                          self.band_b if not self.rgb_mode else 1,
                                          nodata_b)

        if total_a_valid == 0 or total_b_valid == 0:
            score = 0.0
        else:
            score = (match_count / total_a_valid) * (match_count / total_b_valid)

        self.progress.emit(100.0)

        stats = {
            'match': match_count,
            'common': total_valid,
            'valid_a': total_a_valid,
            'valid_b': total_b_valid,
            'grid_cols': cols,
            'grid_rows': rows,
        }

        self.eventTask.emit(
            f"Match: {match_count:,} / Common valid: {total_valid:,} | "
            f"Area A valid: {total_a_valid:,} | Area B valid: {total_b_valid:,}"
        )

        return score, stats

    # ------------------------------------------------------------------
    #  Helpers — block reading
    # ------------------------------------------------------------------

    def _read_block(self, layer: QgsRasterLayer, band: int,
                    extent: QgsRectangle, cols: int, rows: int):
        """Read a raster band as a QgsRasterBlock resampled to target grid."""
        if self.killed:
            return None
        provider = layer.dataProvider()
        block = provider.block(band, extent, cols, rows)
        if block is None or not block.isValid():
            self.eventTask.emit(f"Warning: block read failed for band {band}")
        return block

    def _read_block_val(self, block, row: int, col: int):
        """Read a single value from a QgsRasterBlock with NODATA check.

        Returns float value or None if NODATA/invalid.
        """
        if block is None or not block.isValid():
            return None
        val = block.value(row, col)
        if val is None:
            return None
        # QgsRasterBlock.value() returns inf/nan for NODATA
        if math.isinf(val) or math.isnan(val):
            return None
        return val

    def _read_rgb_vals(self, blocks, row: int, col: int):
        """Read RGB values from a list of 3 QgsRasterBlocks.

        Returns tuple (r, g, b) or None if any band is NODATA.
        """
        vals = []
        for b in blocks:
            v = self._read_block_val(b, row, col)
            if v is None:
                return None
            vals.append(v)
        return tuple(vals)

    def _get_nodata(self, provider, band: int):
        """Get NODATA value for a band, or None if not defined."""
        try:
            if provider.sourceHasNoDataValue(band):
                return provider.sourceNoDataValue(band)
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    #  Helpers — value comparison
    # ------------------------------------------------------------------

    def _values_match(self, v_a, v_b) -> bool:
        """Compare two pixel values (single or RGB tuple).

        Exact match if tolerance == 0, within tolerance otherwise.
        """
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
    #  Helpers — counting valid pixels
    # ------------------------------------------------------------------

    def _count_valid(self, provider, extent: QgsRectangle,
                     cols: int, rows: int, band: int, nodata) -> int:
        """Count valid (non-NODATA) pixels in a raster over the given grid."""
        if self.killed:
            return 0

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

                # Check kill periodically
                if (row * cols + col) % step == 0 and self.killed:
                    break

        return count

    # ------------------------------------------------------------------
    #  PyQt Signals
    # ------------------------------------------------------------------

    finished = pyqtSignal(list)
    """Emitted on completion with [score, stats_dict]."""

    error = pyqtSignal(str)
    """Emitted on error with error message."""

    progress = pyqtSignal(float)
    """Progress percentage (0-100)."""

    eventTask = pyqtSignal(str)
    """Status message for the UI console/log."""
