import logging
from pathlib import Path
from types import SimpleNamespace
import sys

import stealth_scan.scanner as scanner


class FakeScanner:
    def __init__(self):
        self._data = {
            "127.0.0.1": {
                "status": "up",
                "tcp": {
                    445: {
                        "state": "open",
                        "name": "microsoft-ds",
                        "product": "Samba",
                        "version": "4.0",
                        "extrainfo": "",
                        "script": {"rdp-vuln-ms12-020": "safe"},
                    }
                },
            }
        }

    def scan(self, hosts, arguments):
        return

    def all_hosts(self):
        return list(self._data.keys())

    def __getitem__(self, host):
        host_data = self._data[host]
        class HostView:
            def state(self):
                return host_data["status"]

            def all_protocols(self):
                return ["tcp"]

            def __getitem__(self, proto):
                return host_data[proto]

        return HostView()


def test_run_nmap_scan(monkeypatch):
    logger = logging.getLogger("test")
    fake_nmap = SimpleNamespace(PortScanner=FakeScanner, PortScannerError=RuntimeError)
    sys.modules["nmap"] = fake_nmap
    results = scanner.run_nmap_scan("127.0.0.1", logger)

    assert len(results) == 1
    assert results[0].port == 445


def test_write_outputs(tmp_path):
    results = [
        scanner.ScanResult(
            host="127.0.0.1",
            status="up",
            protocol="tcp",
            port=3389,
            state="open",
            name="ms-wbt-server",
            product="",
            version="",
            extrainfo="",
            script_output="{}",
        )
    ]
    written = scanner.write_outputs(results, tmp_path, ["csv", "json", "html"])

    assert len(written) == 3
    for path in written:
        assert Path(path).exists()
