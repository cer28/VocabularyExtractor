set PATH=C:\Program Files\Python27;c:\Program Files\TortoiseSVN\bin;%PATH%

RMDIR /S /Q stage

@REM BASE URL is http://svn.zhtoolkit.com/ChineseWordExtractor/tags/release-0_3_0

REM **Make sure to choose the proper tags/release-* directory as the source
TortoiseProc.exe /command:export /path:stage

@REM TortoiseProc.exe /command:dropexport /path:http://svn.zhtoolkit.com/ChineseWordExtractor/tags/release-0_3_0 /droptarget:stage

pause

cd stage


copy ..\Microsoft.VC90.CRT.manifest .\
copy ..\msvcm90.dll .\
copy ..\msvcp90.dll .\
copy ..\msvcr90.dll .\


python exe-setup.py py2exe


chdir dist
del "Vocabulary Extractor.exe"
ren main.exe "Vocabulary Extractor.exe"

cd ..
ren dist "Vocabulary Extractor"

REM Now zip the folder "Vocabulary Extractor", and rename the zip file
