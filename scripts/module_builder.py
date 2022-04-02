# coding=utf-8
"""
Works on macOS, Ubuntu and Windows
功能：修改aar依赖，把aar和module依赖相互转换

使用： python module_builder.py,运行起来按照提示操作即可

"""

from __future__ import print_function

import os
import sys

_modules_dir = 'modules'
_modules_pre_dir = 'modules-precompiled'
_modules_build_file = 'build.gradle'
_project_setting_gradle = 'settings.gradle'

_build_aar_template = "implementation(name: libs.{}, ext: 'aar')"
_build_module_template = "implementation project(path: '{}')"


class Module(object):
    def __init__(self, dir, name, active=False):
        # type: (str, str, bool) -> object
        self._active = active
        self._dir = dir
        self._name = name
        self._active_name = ':' + dir + ':' + name
        self.gradle_file = os.path.join(dir, name, _modules_build_file)
        self._key = None
        self._build_aar = None
        self._build_module = None

    @property
    def active_name(self):
        return self._active_name

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active

    def __str__(self):
        return self._active_name

    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(other, Module):
            return self._name == other._name and \
                   self._active_name == other._active_name
        return False

    @staticmethod
    def gen_new_settings(all_module):

        settings_str = 'include '
        prefix = ',\n' + (' ' * len(settings_str))
        for ind, m in enumerate(all_module):
            if m.active:
                if ':' not in settings_str:
                    settings_str += "'{}'".format(m.active_name)
                else:
                    settings_str += "{}'{}'".format(prefix, m.active_name)
        return settings_str

    def change_active(self, all_module):
        if not self._dir == _modules_pre_dir:
            print('only can change pre module')
            return False

        self.find_renamed_module()
        self._build_aar = _build_aar_template.format(self._key)
        self._build_module = _build_module_template.format(self._active_name)

        for m in all_module:
            f = open(m.gradle_file, 'r', encoding='utf-8')
            f_str = f.read()
            f.close()
            if not self._active:
                if self._build_aar in f_str:
                    self.active = not self.active
                    print('*' * 10 + m.gradle_file)
                    # 重写依赖该module的build.gradle
                    f = open(m.gradle_file, 'w', encoding='utf-8')
                    f.write(f_str.replace(self._build_aar, self._build_module))
                    f.close()
                    # 修改settings.gradle
                    settings_new = Module.gen_new_settings(all_module)
                    f = open(_project_setting_gradle, 'w', encoding='utf-8')
                    f.write(settings_new)
                    f.close()
                    return True
            else:
                if self._build_module in f_str:
                    self.active = not self.active
                    print('*' * 10 + m.gradle_file)
                    # 重写依赖该module的build.gradle
                    f = open(m.gradle_file, 'w', encoding='utf-8')
                    f.write(f_str.replace(self._build_module, self._build_aar))
                    f.close()
                    # 修改settings.gradle
                    settings_new = Module.gen_new_settings(all_module)
                    f = open(_project_setting_gradle, 'w', encoding='utf-8')
                    f.write(settings_new)
                    f.close()
                    return True

    def find_renamed_module(self):
        """
        找到build.gradle 中的libs 字典
        """
        with open(_modules_build_file, encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if '("' + self._name + '")' in line:
                    self._key = line.strip().split(":")[0].strip()

    def build(self):
        if not self._dir == _modules_pre_dir:
            print('only can change pre module')
            return False
        import build_aar
        build_aar.build([self._name])


def find_modules(path):
    modules = []
    for module in os.listdir(path):
        if not os.path.isdir(os.path.join(path, module)):
            continue
        if _modules_build_file in os.listdir(os.path.join(path, module)):
            modules.append(Module(dir=path, name=module))
    return modules


def get_active_modules():
    modules = []
    with open(_project_setting_gradle, encoding='utf-8') as active_file:
        lines = active_file.readlines()
        valid_modules = ''
        for line in lines:
            if not line.strip().startswith(r'//'):
                valid_modules += line.strip()

        if len(valid_modules) and valid_modules.find('include') >= 0:
            valid_modules = valid_modules.replace('include', '').strip()
            valid_modules = valid_modules.replace("'", '').strip()
            modules_str = valid_modules.split(',')

            for module_str in modules_str:
                strs = module_str.split(':')
                modules.append(Module(strs[len(strs) - 2], strs[len(strs) - 1]))
    return modules


def _help():
    print(u'-' * 100)
    print(u'* 表示在setting.gradle中的moudle')
    print(u'.exit  退出')
    print(u'.help  帮助')
    print(u'[n] n为索引，切换aar依赖或者moudle依赖 ')
    print(u'build [array] 构建aar.   e.g. build 12,13 构建12，13对应的moudle')
    print(u'-' * 100)


def refresh_status():
    pre_modules = find_modules(_modules_pre_dir)
    modules = find_modules(_modules_dir)
    active_modules = get_active_modules()
    all_module = []
    all_module.extend(modules)
    all_module.extend(pre_modules)
    for index, module in enumerate(all_module):
        if module in active_modules:
            module.active = True
            print('* ' + str(index) + str(module))
        else:
            module.active = False
            print('  ' + str(index) + str(module))

    return all_module


def run():
    _help()
    all_module = refresh_status()
    while True:
        if sys.version_info[0] == 2:
            cmd = raw_input('->')
        elif sys.version_info[0] == 3:
            cmd = input('->')
        else:
            raise RuntimeError('platform not support!!')
        if cmd == '.exit':
            break
        if cmd == '.help':
            _help()
            continue
        if cmd.isdigit():
            index = int(cmd)
            if 0 <= index < len(all_module):
                if all_module[index].change_active(all_module):
                    all_module = refresh_status()
                    continue
            else:
                print('index must in the range [%d,%d]' % (0, len(all_module) - 1))
        if cmd.startswith('build '):
            args = cmd[len('build '):].split(',')

            for arg in args:
                if arg.isdigit() and 0 <= int(arg) < len(all_module):
                    all_module[int(arg)].build()
            all_module = refresh_status()
            continue

        print('cmd not right!')


if __name__ == '__main__':
    run()
