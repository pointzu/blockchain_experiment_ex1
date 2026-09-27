"""Prefer the existing course DLL for this process only."""
import os
from pathlib import Path
import struct

if os.name == 'nt':
    project = Path(__file__).resolve().parent
    dll_dir = project.parents[1] / 'ObtainTestcoin'
    if not (dll_dir / 'libeay32.dll').is_file():
        dll_dir = project / '助教提示'
    dll = dll_dir / 'libeay32.dll'
    if dll.is_file():
        data = dll.read_bytes()
        offset = struct.unpack_from('<I', data, 0x3c)[0]
        machine = struct.unpack_from('<H', data, offset + 4)[0]
        expected = 0x8664 if struct.calcsize('P') == 8 else 0x14c
        if machine == expected:
            os.environ['PATH'] = str(dll_dir) + os.pathsep + os.environ['PATH']
