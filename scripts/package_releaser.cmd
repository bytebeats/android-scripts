echo =====================================================================================

call build_flutter_aar.cmd %1
goto build_online

:build_online
rd /s /q build
chcp 65001
set PYTHONIOENCODING=utf-8
echo 构建正式发布包
python add_properties.py
python build_channel2.py
