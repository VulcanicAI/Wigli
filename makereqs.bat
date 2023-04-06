@echo off
@REM Dynamically update requirements.txt and toml
if exist %~dp0requirements.txt (
    del %~dp0requirements.txt
)
pip install -U pipreqs
pipreqs %~dp0\src\wigli --savepath %~dp0\requirements.txt
python %~dp0makereqs.py
