# Wi-Fi Attack Detection System

Final-year university project investigating Wi-Fi attack patterns and developing an automated detection system for identifying deauthentication attacks and CSI-based anomalies.

## Overview

This project implements a proof-of-concept Wi-Fi intrusion detection system using Python.

The system follows two separate detection paths:

* Packet-based detection of IEEE 802.11 deauthentication flood attacks
* Statistical detection of abnormal Channel State Information (CSI) behaviour

The project was developed and tested in an isolated Kali Linux virtual machine.

## Features

### Deauthentication Attack Detection

The `deauth_detection.py` script:

* Loads IEEE 802.11 packet capture files using Scapy
* Identifies deauthentication management frames
* Groups deauthentication activity by source MAC address
* Analyses frames within one-second time windows
* Generates an alert when activity exceeds 10 deauthentication frames per second
* Can be tested against both normal WPA2 traffic and attack traffic

### CSI Anomaly Detection

The `csi_simulate_and_analyse.py` script:

* Generates synthetic Channel State Information data
* Simulates normal and attack-labelled wireless behaviour
* Calculates CSI amplitude variance
* Compares normal and attack variance
* Applies a statistical anomaly threshold
* Generates a CSV dataset
* Generates a variance report
* Produces a CSI amplitude plot

## Technologies

* Python
* Scapy
* NumPy
* Pandas
* Matplotlib
* Wireshark
* Kali Linux
* IEEE 802.11 / Wi-Fi packet analysis

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Deauthentication Detection

Run the detector against an IEEE 802.11 packet capture:

```bash
python3 deauth_detection.py <pcap_file>
```

Example:

```bash
python3 deauth_detection.py deauth.pcap
```

The detector reports the source MAC address, number of deauthentication frames per second and the associated time window when a flood is detected.

### CSI Simulation and Analysis

Run:

```bash
python3 csi_simulate_and_analyse.py
```

The script generates:

* `simulated_csi_data.csv`
* `csi_variance_report.txt`
* `CSI_Simple_plot.png`

## Project Structure

```text
wifi-attack-detection-system/
├── csi_simulate_and_analyse.py
├── deauth_detection.py
├── requirements.txt
├── simulated_csi_data.csv
├── csi_variance_report.txt
├── CSI_Simple_plot.png
├── deauth.pcap
├── wpa2linkuppassphraseiswireshark.pcap
└── README.md
```

## Detection Approach

The deauthentication component uses transparent rule-based detection rather than a machine-learning model. IEEE 802.11 management frames are inspected and deauthentication activity is measured over one-second windows.

The CSI component provides a complementary anomaly-detection approach. Normal wireless behaviour is represented by lower CSI amplitude variance, while attack-labelled behaviour is simulated with greater variation.

## Ethical Use

This project was developed for defensive cyber security research in an isolated environment.

No real networks were targeted during development. Packet captures were used for offline analysis, and the CSI component uses simulated data.

The project is intended for education, research and defensive security purposes only.

## Academic Project

Developed as part of a BSc Digital Forensics and Cyber Security final-year project.
