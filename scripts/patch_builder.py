# coding=utf-8
import base64
import hashlib
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile
from os.path import basename

ROBUST_MAP_PATH = "{rootProject}/{module}/robustMap"
BUILD_CMD = (
                'gradlew' if platform.system() == 'Windows' else './gradlew') + ' assembleOnlineRelease --stacktrace -p ./{rootProject}/{module}'
PATCH_FILE_PATH = "build/{module}/outputs/robust/patch.jar"
PATCH_FILE_OUTPUT_PATH = "patch/"

# init logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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


def recoverGradleBuild():
    f = open("{rootProject}/{module}/build.gradle", 'r+', encoding='utf-8')
    original = f.read()
    application_ = "apply plugin: 'auto-patch-plugin'"
    findStart = original.find("%s" % application_)
    pos = findStart + len(application_)
    if findStart != -1:
        original = original[:pos - len(application_) - 1] + original[pos:]
        f.seek(0, os.SEEK_SET)
        f.truncate()
        f.write(original)
    f.close()


def listApkVersion(index):
    a_file = os.listdir(ROBUST_MAP_PATH)[int(index)]
    currentTime = time.strftime("_%Y%m%d_%H_%M", time.localtime())
    print ("building " +  a_file.split("_")[0])

    extractPathMapping(int(index))
    buildPatch()
    fp = open("build/{module}/outputs/robust/patch.jar", 'rb')
    contents = fp.read()
    fp.close()
    print("补丁MD5:  " + hashlib.md5(contents).hexdigest())
    md5File = "build/{module}/outputs/robust/patch_" + a_file.split("_")[0]  + currentTime + ".txt"
    fp = open(md5File, 'w')
    fp.write("{")
    fp.write("md5:\"" + hashlib.md5(contents).hexdigest() + "\",")
    fp.write("apkHash:\"" + a_file.split("_")[1] + "\",")
    fp.write("content:\"" + toBase64(PATCH_FILE_PATH) + "\"")
    fp.write("}")
    fp.close()
    if not os.path.exists(PATCH_FILE_OUTPUT_PATH):
        os.mkdir(PATCH_FILE_OUTPUT_PATH)
    shutil.move(md5File, PATCH_FILE_OUTPUT_PATH + basename(md5File))


def toBase64(file):
    with open(file, 'rb') as fileObj:
        image_data = fileObj.read()
        base64_data = base64.b64encode(image_data)
        return base64_data.decode()


# 加压打补丁需要的Mapping文件
def extractPathMapping(target):
    currentPath = os.getcwd()
    os.chdir(ROBUST_MAP_PATH)
    if os.path.exists(".DS_Store"):
        os.remove(".DS_Store")
    index = 0
    for a_file in os.listdir():
        if index == target:
            print("extractPathMapping " + str(a_file))
            file = zipfile.ZipFile(a_file, 'r')
            file.extractall("../robust/")
            file.close()
            break
        index += 1
    os.chdir(currentPath)


def buildPatch():
    # 在Gradle文件加入 apply plugin: 'auto-patch-plugin,一定要加在com.android.application下面
    f = open("{rootProject}/{module}/build.gradle", 'r+', encoding='utf-8')
    original = f.read()
    application_ = "apply plugin: 'auto-patch-plugin'"
    findStart = original.find("%s" % application_)
    if findStart == -1:
        application_ = "apply plugin: 'com.android.application'"
        pos = original.find("%s" % application_) + len(application_)
        original = original[:pos] + "\napply plugin: 'auto-patch-plugin'" + original[pos:]
        f.seek(0, os.SEEK_SET)
        f.truncate()
        f.write(original)
    f.close()
    subprocess.call(BUILD_CMD, shell=True)
    recoverGradleBuild()

# TEST 后期看是否有需要压缩
def zipFile():
    f = zipfile.ZipFile('archive.zip', 'w', zipfile.ZIP_DEFLATED)
    f.write('file_to_add.py')
    f.close()


# TEST 后期看是否有需要压缩
def zipFile():
    f = zipfile.ZipFile('archive.zip', 'w', zipfile.ZIP_DEFLATED)
    f.write('file_to_add.py')
    f.close()


if __name__ == '__main__':
    ensure_python_3()
    ensure_unicode_environment()
    currentPath = os.getcwd()
    os.chdir(ROBUST_MAP_PATH)
    patchSize = len(os.listdir())
    os.chdir(currentPath)
    for index in range(0, patchSize):
        listApkVersion(index)
