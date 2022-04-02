cls
echo off
:command
cls
mode con:cols=100
title Build_Install_Publish
ping -n 1 127.0.0.1 >nul
echo =====================================================================================

call build_flutter_aar.cmd %2
goto build_dev

:build_dev

rd /s /q build
python add_properties.py

::在Jenkins里面设置 BUILD_ONLINE 为true，用户临时打线上包发给用户测试
if  "%BUILD_ONLINE%"=="true" (
  set BUILD_VARIANTS=Online
) else (
  set BUILD_VARIANTS=Dev
)

if "%CLEAN%"=="true"  (
   call gradlew clean assemble%BUILD_VARIANTS%Release
   goto publish_dev
)
cd AndroidDpLog
call python gen_version_log.py
cd ..
echo ############Unit Test Start#######################
call gradlew :moduleTigerTrade:UnitTest:clean
call gradlew :moduleTigerTrade:UnitTest:testReleaseUnitTest
echo ############Unit Test End#######################
call gradlew assemble%BUILD_VARIANTS%Release -p ./moduleTigerTrade/AppLite
call gradlew assemble%BUILD_VARIANTS%Release -p ./moduleTigerTrade/AppGP
call gradlew assemble%BUILD_VARIANTS%Release -p ./moduleTigerTrade/AppGlobal
goto publish_dev

:publish_dev
if "%cd:~-4%" neq "opts" (
  cd opts
)
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
if exist index_%1.html del index_%1.html
git log --max-count=50 --no-merges --pretty=tformat:"### %%ci%%n    %%s" > tmp1.txt
copy ..\moduleTigerTrade\AppLite\README_test.md+tmp1.txt tmp2.txt
call python replace_pack_name.py tmp2.txt %1
pandoc tmp2.txt -c ./default.css -H ./header.html -o index_%1.html
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt

if exist ..\build\AppLite\outputs\apk\%BUILD_VARIANTS%\release\*.apk (
  echo build succeed. apk uploading

  pscp -scp index_%1.html mobile:android/
  if exist index_%1.html del index_%1.html

  pscp -scp ..\build\AppLite\outputs\apk\%BUILD_VARIANTS%\release\AppLite-%BUILD_VARIANTS%-release.apk mobile:android/stock_%1_AppLite.apk
  pscp -scp ..\build\AppGP\outputs\apk\%BUILD_VARIANTS%\release\AppGP-%BUILD_VARIANTS%-release.apk mobile:android/stock_%1_AppGP.apk
  pscp -scp ..\build\AppGlobal\outputs\apk\%BUILD_VARIANTS%\release\AppGlobal-%BUILD_VARIANTS%-release.apk mobile:android/stock_%1_AppGL.apk
) else (
  ::echo build failed. project cleaning
  ::cd ..
  ::call gradlew clean
  ::rd /s /q moduleTigerTrade\tigertrade_flutter_module
)

cd ..

