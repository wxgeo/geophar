cd ..
rmdir /Q/S build dist
C:\python27\python.exe setup_windows.py bdist_msi > cx_freeze.log
del /Q/S E:\Geophar*.msi
del /Q/S E:\Geophar-sans-installation*.exe
xcopy dist\*.msi /S/Q/Y E:\
xcopy dist\*.exe /S/Q/Y E:\
dist\Geophar\geophar\geophar-console-mode.exe
pause
