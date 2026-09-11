# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

opencv_data = collect_data_files("cv2", includes=["data/*.xml"])
analysis = Analysis(["run_faceiq.py"], pathex=["src"], binaries=[], datas=opencv_data, hiddenimports=["faceiq.analyzer", "faceiq.detector", "faceiq.quality", "faceiq.exporter"], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(analysis.pure)
exe = EXE(pyz, analysis.scripts, analysis.binaries, analysis.datas, [], name="FaceIQ", debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)
