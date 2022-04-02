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
call gradlew assembleRcRelease -p ./moduleTigerTrade/AppLite
call gradlew assembleRcRelease -p ./moduleTigerTrade/AppGP
goto publish_rc

:publish_rc
if "%cd:~-4%" neq "opts" (
  cd opts
)
echo build succeed. git log checking
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
if exist index_rc.html del index_rc.html
git log --max-count=50 --no-merges --pretty=tformat:"### %%ci%%n    %%s" > tmp1.txt

echo build succeed. html uploading
copy ..\moduleTigerTrade\AppLite\README_rc.md+tmp1.txt tmp2.txt
pandoc tmp2.txt -c ./default.css -H ./header.html -o index_rc.html
pscp -scp index_rc.html mobile:android/index_rc.html

pscp -scp rc_gp.png mobile:android
pscp -scp rc_lite.png mobile:android

echo build succeed. apk uploading
if exist index_rc.html del index_rc.html
pscp -scp ..\build\AppLite\outputs\apk\rc\release\AppLite-rc-release.apk mobile:android/stock_rc_lite.apk
pscp -scp ..\build\AppGP\outputs\apk\rc\release\AppGP-rc-release.apk mobile:android/stock_rc_gp.apk
cd ..
