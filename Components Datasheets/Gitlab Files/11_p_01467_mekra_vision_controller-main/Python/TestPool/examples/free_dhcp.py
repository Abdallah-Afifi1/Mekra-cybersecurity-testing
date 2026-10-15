# -----------------------------------------------------------------------------
# free_dhcp.py - stop a leftover DHCP-server (python) holding UDP port 67
# Run this when a test hung at "DHCP server is starting..." and left port 67 busy.
# -----------------------------------------------------------------------------
import subprocess

PORT = 67


def _ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                          capture_output=True, text=True).stdout.strip()


def pids_on_udp(port):
    out = _ps(f"Get-NetUDPEndpoint -LocalPort {port} -ErrorAction SilentlyContinue"
              f" | Select-Object -ExpandProperty OwningProcess")
    return sorted({int(x) for x in out.split() if x.isdigit()})


pids = pids_on_udp(PORT)
if not pids:
    print(f"UDP port {PORT} is already free. Nothing to do.")
else:
    for pid in pids:
        name = _ps(f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName")
        if name.lower() == "python":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"])
            print(f"Killed leftover DHCP server: python (PID {pid}) -> port {PORT} freed")
        else:
            print(f"Port {PORT} held by PID {pid} ({name or 'unknown'}) - NOT python, skipped. Check it manually.")

print("Done.")