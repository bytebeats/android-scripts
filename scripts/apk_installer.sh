#!/bin/bash

function buildDev() {
    ./gradlew assembleDevRelease
}

function buildOnline() {
    ./gradlew assembleOnlineRelease
}

function installOnline() {
    adb -d install -r -d build/Stock/outputs/apk/online/release/Stock-online-release.apk
    adb -d shell monkey -p com.tigerbrokers.stock -c android.intent.category.LAUNCHER 1
}

function installDev() {
    adb -d install -r -d build/Stock/outputs/apk/dev/release/Stock-dev-release.apk
    adb -d shell monkey -p com.tigerbrokers.stock -c android.intent.category.LAUNCHER 1
}

# 给外部用户的
function publishOnline() {
    echo "publish online apk..."

    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    if [ -f "index.html" ]; then
        rm index_rc.html
    fi

    echo "    `date +%F' '%T`" > tmp1.txt

    cat modules/Stock/README.md tmp1.txt > tmp2.txt

    pandoc tmp2.txt -c ./opts/default.css -o index.html

    scp index.html upload@mobile.tigerbrokers.net:android/

    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    if [ -f "index.html" ]; then
        rm index.html
    fi

    scp build/Stock/outputs/apk/online/release/Stock-online-release.apk upload@mobile.tigerbrokers.net:android/stock.apk
    echo "publish online done!"
}

# 给测试同事的
function publishRc() {
    echo "publish test apk..."
    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    if [ -f "index_rc.html" ]; then
        rm index_rc.html
    fi

    git log --max-count=50 --no-merges --pretty=format:"### %ci%n    %s" > tmp1.txt

    cat modules/Stock/README_rc.md tmp1.txt > tmp2.txt

    pandoc tmp2.txt -c ./opts/default.css -o index_rc.html

    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    scp index_rc.html upload@mobile.tigerbrokers.net:android/

    if [ -f "index_rc.html" ]; then
        rm index_rc.html
    fi

    scp build/Stock/outputs/apk/rc/release/Stock-rc-release.apk upload@mobile.tigerbrokers.net:android/stock_rc.apk
    echo "publish test done!"
}

# 每日更新的，更新频率较高
function publishDaily() {
    echo "publish daily apk..."
    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    if [ -f "index_test.html" ]; then
        rm index_test.html
    fi

    git log --max-count=50 --no-merges --pretty=format:"### %ci%n    %s" > tmp1.txt

    cat modules/Stock/README_test.md tmp1.txt > tmp2.txt

    pandoc tmp2.txt -c ./opts/default.css -H ./opts/header.html -o index_test.html

    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    scp index_test.html upload@mobile.tigerbrokers.net:android/

    if [ -f "index_test.html" ]; then
        rm index_test.html
    fi

    scp build/Stock/outputs/apk/dev/release/Stock-dev-release.apk upload@mobile.tigerbrokers.net:android/stock_test.apk
    echo "publish daily done!"
}

# 专门给服务端用的
function publishServer() {
    echo "publish server apk..."
    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    if [ -f "index_server.html" ]; then
        rm index_server.html
    fi

    git log --max-count=50 --no-merges --pretty=format:"### %ci%n    %s" > tmp1.txt

    cat modules/Stock/README_server.md tmp1.txt > tmp2.txt

    pandoc tmp2.txt -c ./opts/default.css -H ./opts/header.html -o index_server.html

    if [ -f "tmp1.txt" ]; then
        rm tmp1.txt
    fi

    if [ -f "tmp2.txt" ]; then
        rm tmp2.txt
    fi

    scp index_server.html upload@mobile.tigerbrokers.net:android/

    if [ -f "index_server.html" ]; then
        rm index_server.html
    fi

    scp build/Stock/outputs/apk/dev/release/Stock-dev-release.apk upload@mobile.tigerbrokers.net:android/stock_server.apk
    echo "publish apk for server done!"
}

function all() {
    buildOnline
    installDev
    publishOnline
    publishDaily
    publishRc
}

while true;
    do
        echo -n "input command>";
        read line;
        case $line in
            bd|buildDev)
                buildDev
                ;;
            bo|buildOnline)
                buildOnline
                ;;
            id|installDev)
                installDev
                ;;
            io|installOnline)
                installOnline
                ;;
            pd|publishDaily)
                publishDaily
                ;;
            pr|publishRc)
                publishRc
                ;;
            po|publishOnline)
                publishOnline
                ;;
            ps|publishServer)
                publishServer
                ;;
            a|all)
                all
                ;;
            q|quit|exit)
                exit 0
                ;;
            *)
                echo -e "  输入命令非法!  USAGE:\n  [a|all] 完整流程  \n  [bd|buildDev] 构建开发版  \n  [bo|buildOnline] 构建线上版"
                echo -e "  [io|installOnline] 安装online apk  \n  [id|installDev] 安装dev apk"
                echo -e "  [pd|publishDaily] 发布daily build apk  \n  [po|publishOnline] 发布线上公测apk"
                echo -e "  [pr|publishRc] 发布测试版本apk  \n  [ps|publishServer] 发布服务端测试包  \n  [q|quit|exit] 退出命令行 "
                ;;
        esac
    done