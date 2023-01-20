call env.bat
%ECHO ON
python -m raspil_rt.client %client_file% %config%

set /p asd="Hit enter to continue"