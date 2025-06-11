# Spax - Legal DoS Testing Tool

![Spax Badge](https://img.shields.io/badge/Spax-DoS%20Testing%20Tool-blue)

---

## Overview

**Spax** is a **Legal Denial of Service (DoS) attack simulator** designed for resilience and security testing of target systems. It helps measure system robustness and identify potential vulnerabilities by simulating various attack methods like HTTP, TCP, and UDP.

> ⚠️ **Warning:** Use this tool **only** for educational and authorized testing purposes. Unauthorized use is illegal and can lead to severe legal consequences.

---

## Features

- Supports HTTP, TCP, and UDP attack methods (Slowloris support removed)
- Multi-threading for concurrent testing
- Adjustable test duration (seconds or unlimited)
- Live statistics: requests sent, success/failure rates, RPS
- User-friendly CLI and Windows batch script support
- Automatic target IP resolution
- Safe shutdown with CTRL+C and detailed final report
- Proxy support (SOCKS5)
- Custom payloads (random/sequential mode)
- Ramp-up control for gradual load increase
- Export results as JSON or HTML reports

---

## Requirements

- Python 3.8 or higher
- Windows OS (for batch script support)
- Internet connection (for domain resolution)

---

## Installation

```bash
pip install pysocks
