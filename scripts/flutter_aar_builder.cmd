
:: 编译flutter 模块为aar, 如果设置了分支,并且分支有效，使用指定分支最新提交的代码编译，否则使用dev分支编译


set branch=%1
if "%branch%"=="" (
set "branch=dev"
)

:: 备份上次编译结果
mv -f {where_to_put_flutter_module}\flutter_module\build\host\outputs\repo flutter-repo

goto build_with_branch

:build_with_branch
echo ======分支:%branch% 开始编译flutter aar============

cd {where_to_put_flutter_module}
rmdir /s/q flutter_module
git clone -b %branch% --depth=10 git@git.tigerbrokers.net:client/flutter_module.git
if %errorlevel% == 0 (
  mkdir flutter_module\build\host\outputs
  mv -f -T ..\flutter-repo flutter_module\build\host\outputs\repo
  goto compare_and_build
) else (
echo ======flutter分支:%branch% 拉取失败，切换成dev分支编译============
set "branch=dev"
cd ../
goto build_with_branch
)

:build_aar
echo "building flutter aar..."
echo ^<pre^> 当前Flutter分支 : %branch% >../../flutter_git_log.html
git log --max-count=10 --no-merges --pretty=tformat:"### %%ci%%n %%an %%h%%n  %%s" >> ../../flutter_git_log.html
echo ^<pre^> >>../../flutter_git_log.html
set flutter_path=C:\Users\tiger\Desktop\android-sdk\flutter_281
call %flutter_path%\bin\flutter.bat clean
set errorlevel=0
call %flutter_path%\bin\cache\dart-sdk\bin\dart .\androidBuild.dart %flutter_path%\bin\flutter.bat
if %errorlevel% == 0 (
    git rev-parse HEAD > build\host\outputs\repo\flutter_aar_git_version.txt
    cd ../
    goto compare_and_build
) else (
  exit -1
)

:compare_and_build
cd flutter_module
for /F %%i in ('git rev-parse HEAD') do ( set commitid=%%i)
set /P commitid2=<build\host\outputs\repo\flutter_aar_git_version.txt
echo aar_commit_id=%commitid2%
echo newest_commit_id=%commitid%
if "%commitid%" == "%commitid2%" (
    echo "flutter aar already newest"
) else (
    goto build_aar
)
cd ../../

