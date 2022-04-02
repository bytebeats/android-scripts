# coding=utf-8
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile
from os.path import basename

# init logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

PROJECT_ROOT_PATH = os.getcwd()  # 初始位置
BUILD_CMD = (
                'gradlew' if platform.system() == "Windows" else './gradlew') + ' assembleOnlineRelease --stacktrace --no-daemon'
ROBUST_MAP_PATH = "moduleTigerTrade/AppLite/robustMap"
RELEASE_PACKAGE_PATH = PROJECT_ROOT_PATH + '/release_package/'
RECYCLER_PACKAGE_PATH = PROJECT_ROOT_PATH + '/release_package/history_apk/'
APK_TOOL_PATH = PROJECT_ROOT_PATH + '/opts/modNameTool/apktool2.jar'
APK_TOOL_EXTRACT_CMD = "java -jar " + APK_TOOL_PATH + " -f -s -r d "
ARSC_TOOL_CMD = 'java -jar ' + PROJECT_ROOT_PATH + '/opts/modNameTool/ArscTool2.jar' + ' s %s -o resources_m.arsc -rf "%s","%s"'
SIGN_APK_CMD_V2 = "java -jar " + PROJECT_ROOT_PATH + "/opts/360autoBuild/jiagu/lib/apksigner.jar sign --ks " \
                  + PROJECT_ROOT_PATH + "/moduleTigerTrade/AppLite/key.jks --ks-key-alias tigerbrokers --ks-pass pass:tiger9 --out "


# 更换路径，并打印当前路径名称
def change_dir(path):
    os.chdir(path)
    logger.info('current path: ' + os.getcwd())


# 构建生成 apk， 并添加渠道
def build_apk():
    subprocess.call(BUILD_CMD , shell=True)
    logger.info('BUILD_CMD: ' + BUILD_CMD + " "+ platform.system())


# 保存生成补丁需要用的Mapping等文件
def saveMappingAndMethodsMap(apkName):
    if not os.path.exists("moduleTigerTrade/" + apkName + "/robustMap"):
        os.mkdir("moduleTigerTrade/" + apkName + "/robustMap")

    apkVersion = getApkVersion(apkName)
    apkHash = getApkHash(apkName)

    # 保存Mapping文件和MethodMap并压缩
    apkPackage = "build/" + apkName + "/outputs/robust/" + apkVersion + "_" + apkHash
    file = zipfile.ZipFile(apkPackage, 'w', zipfile.ZIP_DEFLATED)
    mappintPath = "build/" + apkName + "/outputs/mapping/onlineRelease/mapping.txt"
    robustPath = "build/" + apkName + "/outputs/robust/methodsMap.robust"
    file.write(mappintPath, basename(mappintPath))
    file.write(robustPath, basename(robustPath))
    file.close()

    shutil.copy2(apkPackage, ROBUST_MAP_PATH)
    # 整理历史打包到另外一个文件夹。一个版本只保留一个包
    # package_name.txt 负责将含有版本号的文件名传给CMD,CMD打包压缩包时就知道版本号了
    f = open(
        PROJECT_ROOT_PATH + '/build/' + apkName + '/outputs/apk/online/release/package_name.txt',
        'a')
    f.write(apkVersion + "_" + apkName + "_" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
    file.close()
    if not os.path.exists(RELEASE_PACKAGE_PATH):
        os.mkdir(RELEASE_PACKAGE_PATH)
    if not os.path.exists(RECYCLER_PACKAGE_PATH):
        os.mkdir(RECYCLER_PACKAGE_PATH)
    for file in os.listdir(RELEASE_PACKAGE_PATH):
        if file.startswith("package_" + apkVersion + "_" + apkName):
            shutil.move(RELEASE_PACKAGE_PATH + file, RECYCLER_PACKAGE_PATH + basename(file))
        if file.startswith("mapping_" + apkVersion + "_" + apkName):
            shutil.move(RELEASE_PACKAGE_PATH + file, RECYCLER_PACKAGE_PATH + basename(file))


def zipApkFiles(apkName):
    apkVersion = getApkVersion(apkName)
    suffix = apkVersion + "_" + apkName + "_" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    zipFileNameApk = "./release_package/package_" + suffix
    zipFileNameMapping = "./release_package/mapping_" + suffix
    subprocess.call(
        "7z a -t7z " + zipFileNameApk + " .\\build\\" + apkName + "\outputs\\apk\online\\release\*release*.apk -mx=9 -ms=4096m -mf -mhc -mhcf -m0=LZMA2:a=2:d=28:fb=64 -mmt -r",
        shell=True)
    subprocess.call(
        "7z a -t7z " + zipFileNameApk + " .\\build\\" + apkName + "\outputs\\robust\*_* -mx=9 -m0=LZMA2:a=2:d=26:fb=64",
        shell=True)
    subprocess.call(
        "7z a -t7z  " + zipFileNameApk + " .\\build\\" + apkName + "\outputs\\robust\R.txt -mx=9 -m0=LZMA2:a=2:d=26:fb=64",
        shell=True)
    logger.info('mapping path: ' + zipFileNameMapping)
    subprocess.call(
        "7z a -t7z " + zipFileNameMapping + " .\\build\\" + apkName + "\outputs\\robust\*_* -mx=9 -m0=LZMA2:a=2:d=26:fb=64",
        shell=True)


def getApkHash(apkName):
    # 拿到版本号和ApkHash
    f = open("build/" + apkName + "/intermediates/merged_assets/onlineRelease/out/robust.apkhash",
             'r', encoding='utf-8')
    apkHash = f.read()
    f.close()
    return apkHash


def getApkVersion(apkName):
    if apkName == "AppGlobal":
        f = open(
            "build/" + apkName + "/generated/source/buildConfig/online/release/com/tigerbrokers/stock/global/BuildConfig.java",
            'r',
            encoding='utf-8')
    else:
        f = open(
            "build/" + apkName + "/generated/source/buildConfig/online/release/com/tigerbrokers/stock/BuildConfig.java",
            'r',
            encoding='utf-8')

    buildConfig = f.read()
    start = buildConfig.find("VERSION_CODE =")
    end = buildConfig.find(";", start)
    apkVersion = buildConfig[start + 15:end]
    f.close()
    return apkVersion


def extractArscFile(apkName):
    OUTPUT_APK_PATH = PROJECT_ROOT_PATH + '/build/' + apkName + '/outputs/apk/online/release/'  # 输出apk路径
    change_dir(OUTPUT_APK_PATH)
    OUTPUT_APK_NAME = apkName + '-online-release.apk'  # 未添加渠道的apk文件名
    EXTRACT_APK_PATH = apkName + '-online-release'
    subprocess.call(APK_TOOL_EXTRACT_CMD + OUTPUT_APK_PATH + OUTPUT_APK_NAME, shell=True)
    shutil.copy2(EXTRACT_APK_PATH + "/resources.arsc", OUTPUT_APK_PATH)


def deepCopy(srcFileDir, targetApk, targetDir):
    for file in os.listdir(srcFileDir):
        if os.path.basename(file).endswith("SF") or os.path.basename(file).endswith(
                "MF") or os.path.basename(
            file).endswith("RSA"):
            continue
        if os.path.isfile(srcFileDir + "/" + file):
            targetApk.write(srcFileDir + "/" + file,
                            "META-INF/" + targetDir + os.path.basename(file))
        else:
            deepCopy(srcFileDir + "/" + file, targetApk, file + "/")


def modifyStringValue(apkName, target, src):
    OUTPUT_APK_PATH = PROJECT_ROOT_PATH + '/build/' + apkName + '/outputs/apk/online/release/'  # 输出apk路径
    EXTRACT_APK_PATH = apkName + '-online-release'
    BUILD_TMP_APK_NAME = apkName + '-online-release-tmp.apk'
    BUILD_TMP_APK_NAME_UNALIGNED = apkName + '-online-release-tmp-unaligned.apk'
    APK_TOOL_BUILD_CMD = 'java -jar ' + APK_TOOL_PATH + ' b %s -o ' + BUILD_TMP_APK_NAME_UNALIGNED
    APK_META_INF_PATH = OUTPUT_APK_PATH + "/" + apkName + "-online-release/original/META-INF"  # 原META-IN路径
    change_dir(OUTPUT_APK_PATH)
    if os.path.exists(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME):
        os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME)
    if os.path.exists(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED):
        os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED)
    logger.info(ARSC_TOOL_CMD % ("resources.arsc", target, src))
    subprocess.call(ARSC_TOOL_CMD % ("resources.arsc", target, src), shell=True)
    shutil.copy2("resources_m.arsc", EXTRACT_APK_PATH + "/resources.arsc")
    subprocess.call(APK_TOOL_BUILD_CMD % EXTRACT_APK_PATH, shell=True)
    change_dir(PROJECT_ROOT_PATH)

    # 深COPY META-INF文件
    zipped = zipfile.ZipFile(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED, 'a',
                             zipfile.ZIP_DEFLATED)
    deepCopy(APK_META_INF_PATH, zipped, "")
    zipped.close()
    ALIGN_APK_CMD = "zipalign 4 " + OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED + " " + OUTPUT_APK_PATH + BUILD_TMP_APK_NAME
    subprocess.call(ALIGN_APK_CMD, shell=True)


def signV2(path):
    # 签名
    logger.info(SIGN_APK_CMD_V2 + path + "  " + path)
    subprocess.call(SIGN_APK_CMD_V2 + path + "  " + path, shell=True)


# 为每个渠道拷贝一个 apk，并把渠道名作为一个文件添加进去
def add_channel(apk_name, channel_list):
    origin_apk_path = apk_name
    logger.info('original apk path: ' + origin_apk_path)
    # 创建一个空文件，放到 apk 里
    empty_channel_file_path = 'empty'
    open(empty_channel_file_path, 'a').close()

    for target_channel in channel_list:
        target_apk_path = origin_apk_path[:-8] + "-" + target_channel + ".apk"
        logger.info('Add channel to: ' + target_apk_path)

        shutil.copy2(origin_apk_path, target_apk_path)
        zipped = zipfile.ZipFile(target_apk_path, 'a', zipfile.ZIP_DEFLATED)
        target_channel_file_path = "META-INF/channel_{channel}".format(channel=target_channel)
        zipped.write(empty_channel_file_path, target_channel_file_path)
        zipped.close()
        signV2(target_apk_path)

    os.remove(empty_channel_file_path)


def build_apk_by_name(apkName, channelList, needModifyString):
    saveMappingAndMethodsMap(apkName)
    OUTPUT_APK_PATH = PROJECT_ROOT_PATH + '/build/' + apkName + '/outputs/apk/online/release/'  # 输出apk路径
    BUILD_TMP_APK_NAME = apkName + '-online-release-tmp.apk'
    if needModifyString:
        extractArscFile(apkName)
        modifyStringValue(apkName, "老虎证券", "老虎国际")
    else:
        shutil.copy2(OUTPUT_APK_PATH + apkName + '-online-release.apk', OUTPUT_APK_PATH + BUILD_TMP_APK_NAME)
    add_channel(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME, channelList)
    os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME)
    os.remove(OUTPUT_APK_PATH + apkName + '-online-release.apk')
    zipApkFiles(apkName)


# 确保当前运行环境为 Python 3 以上
def ensure_python_3():
    if sys.version_info > (3, 0):
        pass
    else:
        raise Exception('You must use Python 3 to avoid encoding problem')


def ensure_unicode_environment():
    logger.info('current encoding: ' + sys.stdout.encoding)
    if 'utf-8' == sys.stdout.encoding or 'UTF-8' == sys.stdout.encoding:
        pass
    else:
        raise Exception(
            'You must run this script in UTF-8 environment. Try "chcp 65001" before running this.')


CHANNEL_LIST_WITH_360 = ['online', 'market_360', 'jinli', 'bdys', 'bdys5', 'chuizi',
                         'lenoo', 'qudaoa', 'qudaob', 'sem', 'share', 'wdj', 'qq_browser',
                         'samsung',
                         'xiaomi', 'baidu', 'meizu', 'bald', 'vivo', 'bdpz', 'xiaomi_widget',
                         'bdys2', 'oppo', 'myapp', 'huawei']
CHANNEL_LIST_1 = ['google_play']
CHANNEL_LIST_3 = ['xiaomi_global', 'oppo_global', 'vivo_global', 'huawei_global']

if __name__ == '__main__':
    ensure_python_3()
    ensure_unicode_environment()

    build_apk()
    build_apk_by_name("AppLite", CHANNEL_LIST_WITH_360, True)
    build_apk_by_name("AppGP", CHANNEL_LIST_1, False)
    build_apk_by_name("AppGlobal", CHANNEL_LIST_3, False)
