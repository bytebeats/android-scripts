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

CHANNEL_LIST_WITH_360 = ['online', 'market_360', 'jinli', 'bdys', 'bdys5', 'chuizi',
                         'lenovo', 'qudaoa', 'qudaob', 'sem', 'share', 'wdj', 'qq_browser', 'samsung',
                         'xiaomi', 'baidu', 'meizu', 'bald', 'vivo', 'bdpz', 'xiaomi_widget',
                         'bdys2', 'oppo', 'myapp', 'huawei']
CHANNEL_LIST_1 = ['google_play']
CHANNEL_LIST_3 = ['xiaomi_global', 'oppo_global', 'vivo_global']
APP_NAME_FULL = u'Tiger Trade'
APP_NAME_1 = u'Tiger Trade老虎美港股'
APP_NAME_3 = u'Tiger Trade-Global Invest&Save'

ORIGINAL_APK_NAME = 'AppLite-online-release-market_360.apk'  # 将要被加固的原始apk文件名
OUTPUT_APK_NAME = 'AppLite-online-release.apk'  # 未添加渠道的apk文件名
JIAGU_APK_NAME = 'AppLite-online-release-market_360_aligned.apk'  # 加固后、未添加渠道的apk文件名

JIAGU_USERNAME = 'android-client@tigerbrokers.com'  # 360加固服务的用户名
JIAGU_PASSWORD = 'TigerBrokers~9'  # 360加固服务的密码
KEY_PWD = 'tiger9'  # keystore password
ALIAS = 'tigerbrokers'  # alias
ALIAS_PWD = 'tiger9'  # alias password

INIT_PATH = os.getcwd()  # 初始位置
JIAGU_TOOLKIT_PATH = INIT_PATH + '/opts/360autoBuild/jiagu'  # 360加固工具包路径
APK_TOOL_PATH = INIT_PATH + '/opts/modNameTool/apktool2.jar'
ARSC_TOOL_PATH = INIT_PATH + '/opts/modNameTool/ArscTool.jar'
CUSTOM_JRE_PATH = JIAGU_TOOLKIT_PATH + '/java/bin'  # 自定义JRE路径
JIAGU_JAR_PATH = JIAGU_TOOLKIT_PATH + '/jiagu.jar'  # 加固工具包的位置
JIAGU_CACHE_PATH = os.path.normpath(JIAGU_TOOLKIT_PATH + '/.cache')  # 加固工具包的缓存文件夹的位置
PROJECT_ROOT_PATH = INIT_PATH  # Android 项目根路径
KEY_PATH = PROJECT_ROOT_PATH + '/moduleTigerTrade/AppLite/key.jks'  # keystore位置
OUTPUT_APK_PATH = PROJECT_ROOT_PATH + '/build/AppLite/outputs/apk/online/release/'  # 输出apk路径
APK_TARGET = OUTPUT_APK_PATH + ORIGINAL_APK_NAME  # 输入的apk位置
APK_META_INF_PATH = OUTPUT_APK_PATH + "/AppLite-online-release/original/META-INF"  # 原META-IN路径
JIAGU_APK_TARGET = OUTPUT_APK_PATH + JIAGU_APK_NAME  # 加固后的apk位置
RELEASE_PACKAGE_PATH = PROJECT_ROOT_PATH + '/release_package/'
RECYCLER_PACKAGE_PATH = PROJECT_ROOT_PATH + '/release_package/history_apk/'
# base cmd
JAVA = 'java'
CMD = '-jar'
# login
CMD_LOGIN = '-login'
# sign
CMD_SIGN = '-importsign'
# jiagu
CMD_JIAGU = '-jiagu'
# showsign
CMD_SHOWSIGN = '-showsign'
# autosign
CMD_AUTOSIGN = '-autosign'
# automulpkg
CMD_AUTOMULPKG = '-automulpkg'

ROBUST_MAP_PATH = "moduleTigerTrade/AppLite/robustMap"

BUILD_CMD = (
                'gradlew' if platform.system() == "Windows" else './gradlew') + ' clean assembleOnlineRelease --stacktrace --no-daemon'

ARSC_TOOL_CMD = 'java -jar ' + ARSC_TOOL_PATH + ' s %s -o resources_m.arsc -t "Tiger Trade","%s"'

APK_TOOL_EXTRACT_CMD = "java -jar " + APK_TOOL_PATH + " -f -s -r d "
EXTRACT_APK_PATH = 'AppLite-online-release'

BUILD_TMP_APK_NAME_UNALIGNED = 'AppLite-online-release-tmp-unaligned.apk'
BUILD_TMP_APK_NAME = 'AppLite-online-release-tmp.apk'

APK_TOOL_BUILD_CMD = 'java -jar ' + APK_TOOL_PATH + ' b %s -o ' + BUILD_TMP_APK_NAME_UNALIGNED

JAR_SIGNER_PATH = PROJECT_ROOT_PATH + '/opts/360autoBuild/jiagu/java/bin/jarsigner'
SIGN_APK_CMD = "jarsigner  -sigalg SHA1withRSA -digestalg SHA1 -keystore " + PROJECT_ROOT_PATH + "/moduleTigerTrade/AppLite/key.jks -storepass tiger9 " + OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED + " tigerbrokers"
SIGN_APK_CMD_V2 = "java -jar "+ PROJECT_ROOT_PATH +"/opts/360autoBuild/jiagu/lib/apksigner.jar sign --ks "\
                  +PROJECT_ROOT_PATH + "/moduleTigerTrade/AppLite/key.jks --ks-key-alias tigerbrokers --ks-pass pass:tiger9 --out "
ALIGN_APK_CMD = "zipalign 4 " + OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED + " " + OUTPUT_APK_PATH + BUILD_TMP_APK_NAME


# 根据文件名后缀查找当前路径的匹配文件
def get_file_name_by_extension(extension):
    for a_file in os.listdir('.'):
        if os.path.isfile(a_file):
            a_extension = os.path.splitext(a_file)[1][1:]
            if extension in a_extension:
                return os.path.basename(a_file)
    raise Exception('file ends with ' + extension + ' not found in ' + os.getcwd())


# 更换路径，并打印当前路径名称
def change_dir(path):
    os.chdir(path)
    logger.info('current path: ' + os.getcwd())


def signV2(path):
    # 签名
    print("start sign")
    print(SIGN_APK_CMD_V2 + path +"  " + path)
    subprocess.call(SIGN_APK_CMD_V2 + path +"  " + path, shell=True)

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


# 产生 cmd 命令
def gen_cmd(*args):
    s = ''
    for arg in args:
        s = s + arg + u' '
    logger.info('generate cmd: \t' + s)
    return s


def exec_command(auto_login_cmd):
    subprocess.call(gen_cmd(*auto_login_cmd), shell=True)


def encrypt_and_sign():
    logger.info(u'产生 360 加固包，并进行签名')
    auto_login_cmd = [JAVA, CMD, JIAGU_JAR_PATH, CMD_LOGIN, JIAGU_USERNAME, JIAGU_PASSWORD]
    auto_import_sign_cmd = [JAVA, CMD, JIAGU_JAR_PATH, CMD_SIGN, KEY_PATH, KEY_PWD, ALIAS, ALIAS_PWD]
    auto_show_sign_cmd = [JAVA, CMD, JIAGU_JAR_PATH, CMD_SHOWSIGN]
    auto_jiagu_sign_cmd = [JAVA, CMD, JIAGU_JAR_PATH, CMD_JIAGU, APK_TARGET, INIT_PATH, CMD_AUTOSIGN, CMD_AUTOMULPKG]
    subprocess.call('chcp 936', shell=True)
    exec_command(auto_login_cmd)
    exec_command(auto_import_sign_cmd)
    exec_command(auto_show_sign_cmd)
    exec_command(auto_jiagu_sign_cmd)


def move_signed_apk_to_output():
    logger.info(u'移动加固并签名的 apk 到 outputs/apk 目录')
    signed_apk_name = get_file_name_by_extension('apk')
    shutil.move(signed_apk_name, JIAGU_APK_TARGET)

def clean_jiagu_cache_files():
    logger.info(u'清理缓存文件')
    subprocess.call('rd /S /Q ' + JIAGU_CACHE_PATH, shell=True)

# # 如果360加固后的apk文件没有签名可用该方法再次签名（如果有签名则直接注释该方法即可）
# def resign_360_apk():
#     logger.info(u'重新签名已加固的360安装包')
#     sign_360_apk_cmd = ['jarsigner', '-verbose', '-sigalg', 'SHA1withRSA', '-digestalg', 'SHA1', '-keystore', KEY_PATH,
#                         '-storepass', KEY_PWD, JIAGU_APK_TARGET, ALIAS]
#     exec_command(sign_360_apk_cmd)


# 360 加固并重新添加渠道的整个流程
def jiagu_360():
    change_dir(CUSTOM_JRE_PATH)
    encrypt_and_sign()
    change_dir(INIT_PATH)
    move_signed_apk_to_output()
    signV2(JIAGU_APK_TARGET)
    change_dir(OUTPUT_APK_PATH)
    # add_channel_360_to_apk()
    change_dir(INIT_PATH)
    clean_jiagu_cache_files()


# 构建生成 apk， 并添加渠道
def build_apk():
    # 删除auto-patch-plugin
    f = open("moduleTigerTrade/AppLite/build.gradle", 'r+', encoding='utf-8')
    original = f.read()
    application_ = "apply plugin: 'auto-patch-plugin'"
    findStart = original.find("%s" % application_)
    pos = findStart + len(application_)
    if findStart != -1:
        original = original[:pos - len(application_) - 1] + original[pos:]
        f.seek(0, os.SEEK_SET)
        f.write(original)
    f.close()
    subprocess.call(BUILD_CMD, shell=True)
    logger.info('BUILD_CMD: ' + BUILD_CMD + " " + platform.system())
    saveMappingAndMethodsMap()


# 保存生成补丁需要用的Mapping等文件
def saveMappingAndMethodsMap():
    if not os.path.exists(ROBUST_MAP_PATH):
        os.mkdir(ROBUST_MAP_PATH)
    # 拿到版本号和ApkHash
    f = open("build/AppLite/intermediates/merged_assets/onlineRelease/out/robust.apkhash", 'r', encoding='utf-8')
    apkHash = f.read()
    f.close()
    f = open("build/AppLite/generated/source/buildConfig/online/release/com/tigerbrokers/AppLite/BuildConfig.java", 'r',
             encoding='utf-8')
    buildConfig = f.read()
    start = buildConfig.find("VERSION_CODE =")
    end = buildConfig.find(";", start)
    apkVersion = buildConfig[start + 15:end]
    f.close()

    # 保存Mapping文件和MethodMap并压缩
    apkPackage = 'build/AppLite/outputs/robust/' + apkVersion + "_" + apkHash
    file = zipfile.ZipFile(apkPackage, 'w', zipfile.ZIP_DEFLATED)
    mappintPath = "build/AppLite/outputs/mapping/onlineRelease/mapping.txt"
    robustPath = "build/AppLite/outputs/robust/methodsMap.robust"
    file.write(mappintPath, basename(mappintPath))
    file.write(robustPath, basename(robustPath))
    file.close()

    shutil.copy2(apkPackage, ROBUST_MAP_PATH)
    # 整理历史打包到另外一个文件夹。一个版本只保留一个包
    # package_name.txt 负责将含有版本号的文件名传给CMD,CMD打包压缩包时就知道版本号了
    f = open(OUTPUT_APK_PATH + "package_name.txt", 'a')
    f.write(apkVersion + "_" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
    file.close()
    if not os.path.exists(RELEASE_PACKAGE_PATH):
        os.mkdir(RELEASE_PACKAGE_PATH)
    if not os.path.exists(RECYCLER_PACKAGE_PATH):
        os.mkdir(RECYCLER_PACKAGE_PATH)
    for file in os.listdir(RELEASE_PACKAGE_PATH):
        if file.startswith("package_" + apkVersion):
            shutil.move(RELEASE_PACKAGE_PATH + file, RECYCLER_PACKAGE_PATH + basename(file))
        if file.startswith("mapping_" + apkVersion):
            shutil.move(RELEASE_PACKAGE_PATH + file, RECYCLER_PACKAGE_PATH + basename(file))


def modifyAppName(appName):
    change_dir(OUTPUT_APK_PATH)
    if os.path.exists(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME):
        os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME)
    if os.path.exists(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED):
        os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED)
    subprocess.call(ARSC_TOOL_CMD % ("resources.arsc", appName), shell=True)
    shutil.copy2("resources_m.arsc", EXTRACT_APK_PATH + "/resources.arsc")
    subprocess.call(APK_TOOL_BUILD_CMD % EXTRACT_APK_PATH, shell=True)
    change_dir(PROJECT_ROOT_PATH)

    # 深COPY META-INF文件
    zipped = zipfile.ZipFile(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED, 'a', zipfile.ZIP_DEFLATED)
    deepCopy(APK_META_INF_PATH, zipped, "")
    zipped.close()

    subprocess.call(ALIGN_APK_CMD, shell=True)


def extractArscFile():
    change_dir(OUTPUT_APK_PATH)
    subprocess.call(APK_TOOL_EXTRACT_CMD + OUTPUT_APK_PATH + OUTPUT_APK_NAME, shell=True)
    shutil.copy2(EXTRACT_APK_PATH + "/resources.arsc", OUTPUT_APK_PATH)


def add_channels_to_apk(channel_list):
    logger.info(u'添加渠道名称: ' + str(channel_list))
    add_channel(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME, channel_list)


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
        raise Exception('You must run this script in UTF-8 environment. Try "chcp 65001" before running this.')


def deepCopy(srcFileDir, targetApk, targetDir):
    for file in os.listdir(srcFileDir):
        if os.path.basename(file).endswith("SF") or os.path.basename(file).endswith("MF") or os.path.basename(
                file).endswith("RSA"):
            continue
        if os.path.isfile(srcFileDir + "/" + file):
            targetApk.write(srcFileDir + "/" + file, "META-INF/" + targetDir + os.path.basename(file))
        else:
            deepCopy(srcFileDir + "/" + file, targetApk, file + "/")


if __name__ == '__main__':
    ensure_python_3()
    ensure_unicode_environment()

    build_apk()
    extractArscFile()

    modifyAppName(APP_NAME_1)
    add_channels_to_apk(CHANNEL_LIST_1)

    modifyAppName(APP_NAME_3)
    add_channels_to_apk(CHANNEL_LIST_3)

    modifyAppName(APP_NAME_FULL)
    add_channels_to_apk(CHANNEL_LIST_WITH_360)

    if 'Windows' in platform.system():
        jiagu_360()
    else:
        logger.info(u'请在Windows系统加固360渠道包')
    os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME)
    os.remove(OUTPUT_APK_PATH + BUILD_TMP_APK_NAME_UNALIGNED)
    os.remove(OUTPUT_APK_PATH + ORIGINAL_APK_NAME)
