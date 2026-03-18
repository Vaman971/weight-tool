@ECHO OFF

if exist ..\.venv\Scripts\python.exe (
    set "SPHINXBUILD=..\.venv\Scripts\python.exe -m sphinx"
) else (
    set "SPHINXBUILD=python -m sphinx"
)
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
