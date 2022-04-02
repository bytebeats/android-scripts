# coding=utf-8
"""
Works on macOS, Ubuntu and Windows

1. find all {modules} in modules-precompiled dir
2. cp settings.gradle build.settings.copy
3. write {modules} to settings.gradle
4. generate compile cmd list
5. mv build/{module}/outputs/aar/{module_name}.aar libs/aars/
6. rm -rf build/{modules}
7. rm settings.gradle
8. mv settings.gradle.copy settings.gradle
"""

import os
import shutil
import sys
import platform

settings_gradle_copy = 'settings.gradle.copy'
settings_gradle_src = 'settings.gradle'

build_file = 'build.gradle'

debug = 'Debug'
release = 'Release'
gradle = 'gradlew ' if platform.system() == "Windows" else './gradlew '
modules_prefix = 'modules-precompiled'

build_aar_template_dir = 'build/%s/outputs/aar/'


def move_aars_2_libs(modules, build_type=release):
    aar_paths = [build_aar_template_dir % key for key in modules]
    dst_paths = ['libs/aars/%s.aar' % key for key in modules]
    for path, dst_path in zip(aar_paths, dst_paths):
        aar_files = os.listdir(path)
        for file in aar_files:
            if file.endswith('%s.aar' % build_type) or file.endswith('%s.aar' % build_type.lower()):
                shutil.copy2(path + file, dst_path)


def clean_temp_file(modules):
    for build_temp in ['build/%s' % key for key in modules]:
        try:
            shutil.rmtree(build_temp)
        except Exception as e:
            pass


def gen_command(module, task='assemble', build_type=release):
    return gradle + ":" + modules_prefix + ":" + module + ":" + task + build_type


def build_aar(modules):
    build_type = release
    if len(sys.argv) > 1:
        build_type = sys.argv[1]

    build_cmds = [gen_command(module=module, build_type=build_type) for module in modules]

    print(build_aar)
    print(build_cmds)
    for build_command in build_cmds:
        if os.system(build_command) != 0:
            clean_temp_file(modules)
            restore_gradle()
            raise RuntimeError('build failed!!!')


def save_gradle(modules):
    if len(modules):
        settings_content = 'include '
        for module in modules:
            settings_content += "':%s:%s'," % (modules_prefix, module)

        shutil.copy2(settings_gradle_src, settings_gradle_copy)
        with open(settings_gradle_src, 'w', encoding='utf-8') as f:
            f.write(settings_content[:-1])


def restore_gradle():
    shutil.move(settings_gradle_copy, settings_gradle_src)


def all_pre_module():
    modules_dirs = os.listdir(modules_prefix)
    modules = []
    for module in modules_dirs:
        if os.path.isdir(os.path.join(modules_prefix, module)):
            module_files = os.listdir(os.path.join(modules_prefix, module))
            is_android_module = False
            for module_file in module_files:
                if module_file == "AndroidManifest.xml":
                    is_android_module = True
                if module_file == build_file and is_android_module:
                    modules.append(module)
    return modules


def build(pre_modules):
    save_gradle(pre_modules)
    build_aar(pre_modules)
    move_aars_2_libs(pre_modules)
    clean_temp_file(pre_modules)
    restore_gradle()


if __name__ == '__main__':

    modules = all_pre_module()
    i = 0
    for module in modules:
        print(str(i) + ":" + module)
        i += 1
    while True:
        if sys.version_info[0] == 2:
            cmd = raw_input('->')
        elif sys.version_info[0] == 3:
            cmd = input('->')
        if cmd.isdigit():
            if int(cmd) >= 0 and int(cmd) < len(modules):
                build([modules[int(cmd)]])
                break
