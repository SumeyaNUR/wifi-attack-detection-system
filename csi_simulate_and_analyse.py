"""Outputs:
- simulated_csi_data.csv
- csi_variance_report.txt
- CSI_Simple_plot.png
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class CSIConfig:
    n_samples: int = 2000
    normal_ratio: float = 0.7
    n_subcarriers: int = 30
    start_time: str = "2025-12-01 12:00:00"
    sample_interval_ms: int = 50

    target_normal_variance: float = 0.021574
    target_attack_variance: float = 0.300710
    threshold_multiplier: float = 3.0

    amplitude_mean: float = 1.0
    phase_mean: float = 0.0
    rssi_mean_dbm: float = -45.0

    phase_std_normal: float = 0.10
    phase_std_attack: float = 0.40
    rssi_std_normal: float = 2.0
    rssi_std_attack: float = 5.0

    seed: int = 1337


def make_timestamps(cfg: CSIConfig) -> np.ndarray:
    start_dt = datetime.strptime(cfg.start_time, "%Y-%m-%d %H:%M:%S")
    times = [start_dt + timedelta(milliseconds=i * cfg.sample_interval_ms) for i in range(cfg.n_samples)]
    return np.array([t.isoformat(sep=" ") for t in times], dtype=object)


def scale_series_to_target_variance(x: np.ndarray, target_var: float) -> np.ndarray:
    """
    Scales x to have EXACT sample variance (ddof=1) equal to target_var.
    """
    if x.size < 2:
        raise ValueError("Need at least 2 samples to define sample variance (ddof=1).")


    x0 = x - x.mean()

    current_var = x0.var(ddof=1)
    if current_var == 0:
        raise ValueError("Current variance is zero; cannot scale.")

    scale = np.sqrt(target_var / current_var)
    return x0 * scale


def generate_dataset(cfg: CSIConfig) -> pd.DataFrame:
    rng = np.random.default_rng(cfg.seed)

    timestamps = make_timestamps(cfg)
    n_normal = int(cfg.n_samples * cfg.normal_ratio)
    n_attack = cfg.n_samples - n_normal

    labels = np.array(["normal"] * n_normal + ["attack"] * n_attack, dtype=object)

    subcarrier_idx = (np.arange(cfg.n_samples) % cfg.n_subcarriers).astype(int)



    amp_normal_raw = rng.normal(0, 1, n_normal)
    amp_attack_raw = rng.normal(0, 1, n_attack)

    amp_normal = scale_series_to_target_variance(amp_normal_raw, cfg.target_normal_variance) + cfg.amplitude_mean
    amp_attack = scale_series_to_target_variance(amp_attack_raw, cfg.target_attack_variance) + cfg.amplitude_mean

    amplitude = np.concatenate([amp_normal, amp_attack]).astype(float)

    phase_normal = rng.normal(cfg.phase_mean, cfg.phase_std_normal, n_normal)
    phase_attack = rng.normal(cfg.phase_mean, cfg.phase_std_attack, n_attack)
    phase = np.concatenate([phase_normal, phase_attack])
    phase = (phase + np.pi) % (2 * np.pi) - np.pi

    rssi_normal = rng.normal(cfg.rssi_mean_dbm, cfg.rssi_std_normal, n_normal)
    rssi_attack = rng.normal(cfg.rssi_mean_dbm, cfg.rssi_std_attack, n_attack)
    rssi = np.concatenate([rssi_normal, rssi_attack]).astype(float)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "subcarrier_index": subcarrier_idx,
            "csi_amplitude": amplitude,
            "csi_phase": phase.astype(float),
            "rssi_dbm": rssi,
            "label": labels,
        }
    )
    return df


def analyse_and_report(df: pd.DataFrame, cfg: CSIConfig) -> dict:
    normal_var = df.loc[df["label"] == "normal", "csi_amplitude"].var(ddof=1)
    attack_var = df.loc[df["label"] == "attack", "csi_amplitude"].var(ddof=1)

    threshold = cfg.threshold_multiplier * normal_var
    ratio = attack_var / normal_var if normal_var > 0 else np.nan

    return {
        "normal_variance": float(normal_var),
        "attack_variance": float(attack_var),
        "attack_to_normal_ratio": float(ratio),
        "threshold_multiplier": float(cfg.threshold_multiplier),
        "variance_threshold": float(threshold),
        "targets_normal_variance": float(cfg.target_normal_variance),
        "targets_attack_variance": float(cfg.target_attack_variance),
        "targets_threshold": float(cfg.threshold_multiplier * cfg.target_normal_variance),
    }


def plot_first_n(df: pd.DataFrame, n: int = 100, outfile: str = "CSI_Simple_plot.png") -> None:
    subset = df.head(n)
    x = np.arange(len(subset))
    y = subset["csi_amplitude"].to_numpy()

    plt.figure()
    plt.plot(x, y)
    plt.title(f"CSI Amplitude (first {n} samples)")
    plt.xlabel("Sample index")
    plt.ylabel("CSI amplitude")
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()


def main() -> None:
    cfg = CSIConfig()

    df = generate_dataset(cfg)
    df.to_csv("simulated_csi_data.csv", index=False)

    report = analyse_and_report(df, cfg)

    with open("csi_variance_report.txt", "w", encoding="utf-8") as f:
        f.write("Synthetic CSI variance analysis)\n")
        f.write(f"Generated: {datetime.now().isoformat(sep=' ', timespec='seconds')}\n\n")
        for k, v in report.items():
            f.write(f"{k}: {v}\n")

    plot_first_n(df, n=100, outfile="CSI_Simple_plot.png")

    print("COMPLETE!")
    print(f"- Dataset saved: {os.path.abspath('simulated_csi_data.csv')}")
    print(f"- Variance report: {os.path.abspath('csi_variance_report.txt')}")
    print(f"- Plot saved: {os.path.abspath('CSI_Simple_plot.png')}")
    print("\nVariance check:")
    print(f"  normal_variance  : {report['normal_variance']}")
    print(f"  attack_variance  : {report['attack_variance']}")
    print(f"  variance_threshold (3x normal): {report['variance_threshold']}")


if __name__ == "__main__":
    main()
