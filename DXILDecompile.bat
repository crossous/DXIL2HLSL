@echo off

: decompile input_file
python "%~dp0DXILDecompile.py" "%1" --output "%1.hlsl"

: redirect to stdout
for %%f in ("%1") do type "%%~dpnf.hlsl"