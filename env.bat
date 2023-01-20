@ECHO OFF
for /f "delims== tokens=1,2" %%G in (config.txt) do set %%G=%%H
@ECHO ON