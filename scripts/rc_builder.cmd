cls
echo off
:command
cls
mode con:cols=100
title Build_Install_Publish
ping -n 1 127.0.0.1 >nul
echo =====================================================================================

call build_flutter_aar.cmd dev

goto build_rc

:build_rc
rd /s /q build
python add_properties.py
call gradlew assembleRcRelease
goto publish_rc

:publish_rc
if "%cd:~-4%" neq "opts" (
  cd opts
)
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
if exist index_rc_%1.html del index_rc_%1.html
git log --max-count=50 --no-merges --pretty=tformat:"### %%ci%%n    %%s" > tmp1.txt
copy ..\modules\Stock\README_rc_branch.md+tmp1.txt tmp2.txt
call python replace_pack_name.py tmp2.txt %1
pandoc tmp2.txt -c ./default.css -H ./header.html -o index_rc_%1.html
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
pscp -scp index_rc_%1.html mobile:android/
if exist index_rc_%1.html del index_rc_%1.html
pscp -scp ..\build\Stock\outputs\apk\rc\release\Stock-rc-release.apk mobile:android/stock_rc_%1.apk
cd ..
