"""Part 1, Exercise 1: mask out invalid (NaN) samples from a raw measurement series.

Space plasma instruments (e.g. a solar wind ion spectrometer) regularly drop
samples during data gaps, calibration windows, or telemetry loss. Those gaps
show up as NaN in the raw time series. Before any further processing
(filtering, feature extraction, etc.) you typically need to drop them.

Implement `mask_invalid_samples` below using boolean indexing (no pandas).
"""

import numpy as np


def mask_invalid_samples(raw_series: np.ndarray) -> np.ndarray:
    """Return `raw_series` with all NaN entries removed.

    Parameters
    ----------
    raw_series : np.ndarray
        1-D array of float measurements (e.g. proton density in cm^-3),
        possibly containing NaN where the instrument had no valid reading.

    Returns
    -------
    np.ndarray
        1-D array containing only the finite (non-NaN) values of
        `raw_series`, in their original order.
    """
    # TODO: replace this stub with a boolean-indexing solution, e.g.
    # return raw_series[~np.isnan(raw_series)]
    return raw_series


if __name__ == "__main__":
    example = np.array([1.0, np.nan, 2.5, np.nan, 3.25])
    print(mask_invalid_samples(example))
