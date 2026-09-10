import ctypes
import os
import sys
from ctypes import wintypes


print(f"python: {sys.executable}")
print(f"cwd: {os.getcwd()}")

# Check WebView2 Runtime
try:
    import winreg

    keys = [
        r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
        r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
    ]
    found = False
    for key_path in keys:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                version, _ = winreg.QueryValueEx(key, "pv")
                print(f"WebView2 Runtime: found, version={version}")
                found = True
                break
        except OSError:
            continue
    if not found:
        print("WebView2 Runtime: not found")
except Exception as e:
    print(f"WebView2 Runtime check error: {e}")

# Check dist
base = os.path.dirname(os.path.abspath(sys.argv[0]))
print(f"project: {base}")
print(f"dist exists: {os.path.isdir(os.path.join(base, 'dist'))}")
print(f"index.html exists: {os.path.isfile(os.path.join(base, 'dist', 'index.html'))}")
assets_dir = os.path.join(base, "dist", "assets")
if os.path.isdir(assets_dir):
    print(f"assets files: {os.listdir(assets_dir)}")

# Check shortcut
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
lnk = os.path.join(desktop, "Markdown 笔记.lnk")
url = os.path.join(desktop, "Markdown 笔记.url")
print(f"desktop .lnk exists: {os.path.exists(lnk)}")
print(f"desktop .url exists: {os.path.exists(url)}")

if os.path.exists(lnk):
    try:
        CLSID_ShellLink = ctypes.create_string_buffer(
            b"\x01\x14\x02\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46"
        )
        IID_IShellLinkW = ctypes.create_string_buffer(
            b"\xF9\x14\x02\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46"
        )
        IID_IPersistFile = ctypes.create_string_buffer(
            b"\x0B\x01\x00\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46"
        )
        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)
        shell_link = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(
            ctypes.byref(CLSID_ShellLink), None, 0x1, ctypes.byref(IID_IShellLinkW), ctypes.byref(shell_link)
        )
        if hr:
            print(f"CoCreateInstance failed: 0x{hr:08X}")
        else:
            vtbl = ctypes.cast(shell_link, ctypes.POINTER(ctypes.c_void_p)).contents.value
            methods = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p * 20)).contents
            persist = ctypes.c_void_p()
            qi = ctypes.WINFUNCTYPE(
                ctypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)
            )
            qi(methods[0])(shell_link, ctypes.byref(IID_IPersistFile), ctypes.byref(persist))
            pvtbl = ctypes.cast(persist, ctypes.POINTER(ctypes.c_void_p)).contents.value
            pmethods = ctypes.cast(pvtbl, ctypes.POINTER(ctypes.c_void_p * 8)).contents
            load = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_wchar_p, wintypes.DWORD)
            load(pmethods[5])(persist, lnk, 0)

            def get_string(idx: int, size: int) -> str:
                buf = ctypes.create_unicode_buffer(size)
                gp = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int)
                gp(methods[idx])(shell_link, buf, size)
                return buf.value

            print(f"shortcut target: {get_string(3, 1024)}")
            print(f"shortcut args: {get_string(10, 1024)}")
            print(f"shortcut working_dir: {get_string(8, 1024)}")
    except Exception as e:
        print(f"shortcut read error: {e}")
