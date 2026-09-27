"""Detect when your phone comes into (or leaves) your room.

Two detection methods, use either or both:

1. Bluetooth Low Energy (recommended for "room" range). Scans for your phone's BLE
   signal and treats it as present when the signal strength (RSSI) is above a
   threshold. Around -80 dBm is roughly 10 metres indoors; -70 is closer (~5 m).
   Identify your phone by its Bluetooth name or its address.

2. Wi-Fi ping. Treats the phone as present when it answers pings on your home
   network. Works at "whole house" range, not room range.

Run `python -m jarvis.presence --scan` to list nearby Bluetooth devices so you
can find your phone's name/address and signal strength.
"""

import argparse
import asyncio
import platform
import subprocess
import threading
import time

try:
    from bleak import BleakScanner
except ImportError:
    BleakScanner = None


def ble_scan(seconds: float = 5.0):
    """Return a list of (address, name, rssi) for nearby BLE devices."""
    if BleakScanner is None:
        raise RuntimeError("Bluetooth support missing. Run: pip install bleak")
    found = asyncio.run(BleakScanner.discover(timeout=seconds, return_adv=True))
    return [
        (addr, adv.local_name or dev.name or "", adv.rssi)
        for addr, (dev, adv) in found.items()
    ]


def ping(ip: str) -> bool:
    flag = "-n" if platform.system() == "Windows" else "-c"
    wait = ["-w", "1000"] if platform.system() == "Windows" else ["-W", "1"]
    try:
        result = subprocess.run(
            ["ping", flag, "1", *wait, ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


class PresenceDetector:
    """Watches for your phone in a background thread.

    `on_arrive` is called once when the phone comes into range and `on_leave`
    once when it has been out of range for `away_after` seconds (so a brief
    signal drop doesn't make Jarvis say hello again).
    """

    def __init__(self, phone_name="", phone_address="", phone_ip="",
                 rssi_threshold=-80, away_after=90, scan_seconds=5.0,
                 on_arrive=None, on_leave=None):
        self.phone_name = phone_name.lower().strip()
        self.phone_address = phone_address.lower().strip()
        self.phone_ip = phone_ip.strip()
        self.rssi_threshold = rssi_threshold
        self.away_after = away_after
        self.scan_seconds = scan_seconds
        self.on_arrive = on_arrive or (lambda: None)
        self.on_leave = on_leave or (lambda: None)

        self.present = False
        self.last_seen = 0.0
        self._stop = threading.Event()
        self._thread = None

        if not (self.phone_name or self.phone_address or self.phone_ip):
            raise ValueError(
                "Tell Jarvis which phone to look for: set JARVIS_PHONE_NAME, "
                "JARVIS_PHONE_ADDRESS or JARVIS_PHONE_IP in your .env file."
            )

    def _phone_nearby(self) -> bool:
        if self.phone_name or self.phone_address:
            try:
                for addr, name, rssi in ble_scan(self.scan_seconds):
                    matches = (
                        (self.phone_address and addr.lower() == self.phone_address)
                        or (self.phone_name and self.phone_name in name.lower())
                    )
                    if matches and rssi >= self.rssi_threshold:
                        return True
            except Exception as e:
                print(f"(Bluetooth scan failed: {e})")
                time.sleep(self.scan_seconds)
        if self.phone_ip and ping(self.phone_ip):
            return True
        return False

    def check_once(self):
        """Run one detection cycle and fire callbacks on state changes."""
        now = time.time()
        if self._phone_nearby():
            self.last_seen = now
            if not self.present:
                self.present = True
                self.on_arrive()
        elif self.present and now - self.last_seen >= self.away_after:
            self.present = False
            self.on_leave()

    def _run(self):
        while not self._stop.is_set():
            self.check_once()
            self._stop.wait(1)

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()


def main():
    parser = argparse.ArgumentParser(description="Find your phone's Bluetooth details.")
    parser.add_argument("--scan", action="store_true", help="list nearby Bluetooth devices")
    parser.add_argument("--seconds", type=float, default=8.0)
    args = parser.parse_args()
    if not args.scan:
        parser.print_help()
        return
    print(f"Scanning for {args.seconds:.0f} seconds... keep your phone's Bluetooth ON.")
    devices = sorted(ble_scan(args.seconds), key=lambda d: d[2], reverse=True)
    print(f"\n{'SIGNAL':>7}  {'ADDRESS':<40}  NAME")
    for addr, name, rssi in devices:
        print(f"{rssi:>4} dBm  {addr:<40}  {name or '(no name)'}")
    print("\nStrongest signals are closest. Move your phone away and scan again to spot it.")


if __name__ == "__main__":
    main()
