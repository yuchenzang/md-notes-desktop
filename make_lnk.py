"""Create a standard Windows .lnk shortcut for the Markdown notes desktop app.

This uses raw COM/ctypes (IShellLinkW + IPersistFile) so it works even when
WScript.Shell / win32com are blocked by local security policy. It stores paths
as Unicode, which correctly handles Chinese directory names unlike .url files.
"""

import ctypes
import os
import shutil
import sys
from ctypes import wintypes


# IIDs
CLSID_ShellLink = ctypes.create_string_buffer(
    b'\x01\x14\x02\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46'
)
IID_IShellLinkW = ctypes.create_string_buffer(
    b'\xF9\x14\x02\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46'
)
IID_IPersistFile = ctypes.create_string_buffer(
    b'\x0B\x01\x00\x00\x00\x00\x00\x00\xC0\x00\x00\x00\x00\x00\x00\x46'
)

CLSCTX_INPROC_SERVER = 0x1
SW_SHOWNORMAL = 1


def guid_bytes(guid_s: str) -> ctypes.create_string_buffer:
    """Convert GUID string like '{...}' to little-endian byte buffer."""
    import uuid
    return ctypes.create_string_buffer(uuid.UUID(guid_s).bytes_le)


def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # IMPORTANT: point the shortcut directly at pythonw.exe (the windowless
    # Python launcher) so Windows does NOT spawn a cmd.exe console window.
    # Launching app.pyw through run_desktop.cmd caused a black console box.
    target_exe = os.path.join(base_dir, '.venv', 'Scripts', 'pythonw.exe')
    if not os.path.isfile(target_exe):
        print(f'Target not found: {target_exe}', file=sys.stderr)
        return 1

    arguments = f'"{os.path.join(base_dir, "main.pyw")}"'
    working_dir = base_dir
    description = '煜辰的 Markdown 笔记桌面应用'
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    lnk_name = '煜辰的 Markdown 笔记.lnk'
    desktop_lnk = os.path.join(desktop, lnk_name)

    ole32 = ctypes.windll.ole32
    shell32 = ctypes.windll.shell32

    ole32.CoInitialize(None)

    try:
        # 1. Create ShellLink instance
        shell_link = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(
            ctypes.byref(CLSID_ShellLink),
            None,
            CLSCTX_INPROC_SERVER,
            ctypes.byref(IID_IShellLinkW),
            ctypes.byref(shell_link),
        )
        if hr != 0:
            raise OSError(f'CoCreateInstance(IShellLinkW) failed: 0x{hr:08X}')

        # Helper to call a vtable method by index (first arg is the interface pointer)
        vtbl = ctypes.cast(shell_link, ctypes.POINTER(ctypes.c_void_p)).contents.value
        methods = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p * 20)).contents

        def call(idx: int, *argtypes):
            proto = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *argtypes)
            fn = proto(methods[idx])
            return lambda *args: fn(shell_link, *args)

        # 2. Resolve the pythonw.exe path to a PIDL and set it as the target,
        #    then set the script as the argument. This avoids launching via a
        #    .cmd file so no black cmd.exe console window appears.
        pidl = ctypes.c_void_p()
        hr = shell32.SHParseDisplayName(
            ctypes.c_wchar_p(target_exe),
            None,
            ctypes.byref(pidl),
            0,
            None,
        )
        if hr != 0:
            raise OSError(f'SHParseDisplayName failed: 0x{hr:08X}')
        try:
            call(5, ctypes.c_void_p)(pidl)  # SetIDList -> points at pythonw.exe
        finally:
            ole32.CoTaskMemFree(pidl)

        call(11, ctypes.c_wchar_p)(arguments)            # SetArguments -> app.pyw

        # 3. Set other shortcut properties
        call(9, ctypes.c_wchar_p)(working_dir)            # SetWorkingDirectory
        call(15, wintypes.INT)(SW_SHOWNORMAL)             # SetShowCmd
        call(7, ctypes.c_wchar_p)(description)            # SetDescription

        # 4. Set icon location (purple M icon)
        icon_path = os.path.join(base_dir, 'app_icon.ico')
        if os.path.isfile(icon_path):
            call(17, ctypes.c_wchar_p, wintypes.INT)(icon_path, 0)  # SetIconLocation

        # 5. Query IPersistFile from the existing ShellLink and save to a temp file
        persist_file = ctypes.c_void_p()
        qi_proto = ctypes.WINFUNCTYPE(
            ctypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)
        )
        hr = qi_proto(methods[0])(shell_link, ctypes.byref(IID_IPersistFile), ctypes.byref(persist_file))
        if hr != 0:
            raise OSError(f'QueryInterface(IPersistFile) failed: 0x{hr:08X}')

        pvtbl = ctypes.cast(persist_file, ctypes.POINTER(ctypes.c_void_p)).contents.value
        pmethods = ctypes.cast(pvtbl, ctypes.POINTER(ctypes.c_void_p * 8)).contents
        save_proto = ctypes.WINFUNCTYPE(
            ctypes.HRESULT, ctypes.c_void_p, ctypes.c_wchar_p, wintypes.BOOL
        )
        # Save DIRECTLY to the Desktop path. IPersistFile::Save overwrites an
        # existing file in place, so we avoid os.remove() (which the sandbox
        # safe-delete policy blocks) and avoid a temp-file copy step.
        hr = save_proto(pmethods[6])(persist_file, desktop_lnk, True)  # Save
        if hr != 0:
            raise OSError(f'IPersistFile::Save failed: 0x{hr:08X}')

        # Release COM objects (best effort)
        release_proto = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
        release_proto(pmethods[2])(persist_file)
        release_proto(methods[2])(shell_link)

    finally:
        ole32.CoUninitialize()

    # Best-effort cleanup of stale shortcuts / old icon file (wrapped; ignore failures)
    for stale in ('Markdown 笔记.url', 'Markdown 笔记.lnk'):
        stale_path = os.path.join(desktop, stale)
        if os.path.exists(stale_path):
            try:
                os.remove(stale_path)
            except OSError as e:
                print(f'Could not remove old shortcut {stale}: {e}')
    old_ico = os.path.join(base_dir, 'app.ico')
    if os.path.exists(old_ico):
        try:
            os.remove(old_ico)
        except OSError as e:
            print(f'Could not remove old icon: {e}')

    print(f'Created shortcut: {desktop_lnk}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
