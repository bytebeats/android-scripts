cls
chcp 65001
echo off
:command
cls
mode con:cols=100
title Build_Install_Publish
ping -n 1 127.0.0.1 >nul
echo =====================================================================================
echo  Select:
echo.
echo    bd. build_dev
echo.
echo    br. build_rc
echo.
echo    bo. build_online
echo.
echo    id. install_dev
echo.
echo    ir. install_rc
echo.
echo    pd. publish_dev
echo.
echo    pr. publish_rc
echo.
echo    e.  exit
echo ====================================================================================
echo.
SET /P choice=Input your choice (Press 'Enter' to confirm)
echo.&echo.
IF %choice%==bd goto build_dev
IF %choice%==br goto build_rc
IF %choice%==bo goto build_online
IF %choice%==bp goto build_google_play
IF %choice%==bx goto build_xiaomi
IF %choice%==id goto install_dev
IF %choice%==ir goto install_rc
IF %choice%==pd goto publish_dev
IF %choice%==pr goto publish_rc
IF %choice%==e exit
goto command

:install_dev
adb -d install -r -d build/Stock/outputs/apk/dev/release/Stock-dev-release.apk
adb -d shell monkey -p com.tigerbrokers.stock -c android.intent.category.LAUNCHER 1
@pause
goto command

:install_rc
adb -d install -r -d build/Stock/outputs/apk/rc/release/Stock-rc-release.apk
adb -d shell monkey -p com.tigerbrokers.stock -c android.intent.category.LAUNCHER 1
@pause
goto command

:publish_dev
if "%cd:~-4%" neq "opts" (
  cd opts
)
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
if exist index_test.html del index_test.html
git log --max-count=50 --no-merges --pretty=tformat:"### %%ci%%n    %%s" > tmp1.txt
copy ..\modules\Stock\README_test.md+tmp1.txt tmp2.txt
pandoc tmp2.txt -c ./default.css -H ./header.html -o index_test.html
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
pscp -scp index_test.html mobile:android/
if exist index_test.html del index_test.html
pscp -scp ..\build\Stock\outputs\apk\Stock-dev-release.apk mobile:android/stock_test.apk
cd ..
@pause
goto command

:publish_rc
if "%cd:~-4%" neq "opts" (
  cd opts
)
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
if exist index_rc.html del index_rc.html
git log --max-count=50 --no-merges --pretty=tformat:"### %%ci%%n    %%s" > tmp1.txt
copy ..\modules\Stock\README_rc.md+tmp1.txt tmp2.txt
pandoc tmp2.txt -c ./default.css -H ./header.html -o index_rc.html
if exist tmp1.txt del tmp1.txt
if exist tmp2.txt del tmp2.txt
pscp -scp index_rc.html mobile:android/
if exist index_rc.html del index_rc.html
pscp -scp ..\build\Stock\outputs\apk\Stock-rc-release.apk mobile:android/stock_rc.apk
cd ..
@pause
goto command

:build_dev
call gradlew assembleDevRelease
@pause
goto command

:build_rc
call gradlew assembleRcRelease
goto :archiveMapping

:build_online
call gradlew assembleOnlineRelease
python opts/channel.py
goto :archiveMapping

:archiveMapping
xcopy /s/y build\Stock\outputs\mapping\online\release\mapping.txt "%USERPROFILE%\mapping\%DATE%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%\"
@pause
goto command
