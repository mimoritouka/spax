# Spax - Legal DoS Testing Tool

![Spax Banner](https://img.shields.io/badge/Spax-DoS%20Testing%20Tool-blue)

## Overview

**Spax** is a **Legal Denial of Service (DoS) attack simulator** developed for resilience and security testing of target systems. This tool is designed to measure system robustness and identify potential vulnerabilities by using different attack methods (HTTP, TCP, UDP, Slowloris).

![image](https://github.com/user-attachments/assets/fedb91c6-a509-4af0-a8fb-11537efb3100)


> **WARNING:** This tool should only be used for educational and legal testing purposes. Unauthorized use is illegal and may result in serious legal consequences.

---

## Features

- HTTP, TCP, UDP, and Slowloris attack methods  
- Multi-threading support  
- Adjustable attack duration (in seconds or unlimited)  
- Live statistics tracking (requests sent, successes/failures, RPS)  
- User-friendly command line interface and batch script for easy usage  
- Automatic target URL/IP resolution  
- Safe shutdown with CTRL+C and statistics display  

---

## Requirements

- Python 3.8 or higher  
- Windows OS (for batch script support)  
- Internet connection (for target IP resolution)  

---

## Usage

### Batch Script (Windows)

1. Spax.py and spax.bat files must be in the same folder.  
2. Run the `spax.bat` file.  
3. Enter the target domain/IP, attack method, thread count, and duration when prompted.  
4. The attack will start and live statistics will be displayed.  
5. Press CTRL+C to stop the attack safely.  

---

### Command Line Options (Python Script)

```bash
python spax.py -d <target> [-m <method>] [-t <threads>] [-s <seconds>] [--quiet]
