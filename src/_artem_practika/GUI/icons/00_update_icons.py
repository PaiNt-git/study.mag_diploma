#!/usr/bin/env python3

import sys
import os
import argparse
from subprocess import PIPE, run


class CreateQrc:

    @staticmethod
    def watch_in_dir(path, depth=999999, only_files=None, only_dirs=None, relative=True, *args, **kw):
        """
        Сканирует директорию с заданным уровнем вложенности и возвращает список найденных
        файлов и/или папок
                                Типичный вызов:
        "{{ path + '/' | watch_in_dir(depth=2, only_files=True, relative=False) }}"
        Пример использования:
        {%- set dest = (_pnu_dirs.files, 'context/for_build/') | path_join -%}
        {%- set path = (_pnu_dirs.templates, 'for_build/') | path_join -%}
        {%- set images = path | watch_in_dir(depth=1, only_dirs=True, relative=True) -%}
        {%- set return_dict = {} -%}
        {%- for image in images -%}
          {%- set current_path = (path, image) | path_join + '/' -%}
          {%- set dest_path = (dest, image) | path_join + '/' -%}
          {%- do return_dict.update({
            image: {
              'src_dir': current_path,
              'dest_dir': dest_path,
              'src_files': current_path | watch_in_dir(depth=2, only_files=True, relative=True),
            }
          }) -%}
        {%- endfor -%}
        {{ return_dict }}

        MSG: {'domino_32': {'src_dir': '/home/adminka/General/shared/ansible/roles/our_images.management/templates/pnu_portal/for_build/domino_32/', 'dest_dir': '/home/adminka/General/shared/ansible/roles/our_images.management/files/pnu_portal/context/for_build/domino_32/', 'src_files': ['123/1.txt', 'silent_x32.dat']}}

        tree /home/adminka/General/shared/ansible/roles/our_images.management/templates/pnu_portal/for_build
        └── domino_32
            ├── 123
            │   └── 1.txt
            └── silent_x32.dat

        Пример 2:
        _pnu_for_run: >-
          {%- set dest = _pnu_dirs.mount.local + '/' -%}
          {%- set path = (_pnu_dirs.templates, 'for_run/') | path_join -%}
          {%- set files = path | watch_in_dir(depth=999, only_files=True, relative=False) -%}
          {%- set return_list = [] -%}
          {%- for file in files -%}
            {%- do return_list.append({
              'src': file,
              'dest': file | replace(path, dest),
            }) -%}
          {%- endfor -%}
          {{ return_list }}

        MSG: [
          { "dest": "/home/adminka/General/shared/ansible/roles/our_images.management/files/pnu_portal/context/mounts/configs/ALL/uwsgi/portal.ini",
            "src": "/home/adminka/General/shared/ansible/roles/our_images.management/templates/pnu_portal/for_run/uwsgi/portal.ini"},
          { "dest": "/home/adminka/General/shared/ansible/roles/our_images.management/files/pnu_portal/context/mounts/configs/ALL/domino_x32-64/notes.ini",
            "src": "/home/adminka/General/shared/ansible/roles/our_images.management/templates/pnu_portal/for_run/domino_x32-64/notes.ini"
          },
          ...
        """

        def generator_p(path: str, depth: int):
            depth -= 1
            with os.scandir(path) as p:
                for entry in p:
                    yield entry.path
                    if entry.is_dir() and depth > 0:
                        yield from generator_p(path=entry.path, depth=depth)

        if only_files == None and only_dirs == None:
            only_files = True
            only_dirs = False
        elif only_files == True:
            only_dirs = False
        elif only_dirs == True:
            only_files = False
        elif only_files == False:
            only_dirs = True
        elif only_dirs == False:
            only_files = True

        paths = [elem for elem in generator_p(path, depth)]
        if only_files:
            paths = [elem for elem in paths if os.path.isfile(elem)]
        elif only_dirs:
            paths = [elem for elem in paths if os.path.isdir(elem)]

        if relative:
            paths = [elem.replace(path, '') for elem in paths if elem != path]

        return paths

    @staticmethod
    def write_file(input_file, new_content):
        """Функция для перезаписи содержимого файла

        :param input_file: Полный путь до файла
        :type input_file: str
        :raises [Exception]: [BaseException] Не удалось загрузить файл `input_file`
        """
        try:
            with open(input_file, mode='w') as file:
                file.write(new_content)
        except:
            raise Exception('Не удалось загрузить %s!' % input_file)

    @staticmethod
    def create_dir(directory: str, mode='755'):
        mode = int(mode, base=8)
        if not os.path.isdir(directory):
            os.makedirs(directory, mode)

    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.analyze_cli_parameters()
        self.files_in_src = self.watch_in_dir(
            self.options.src, only_files=True, relative=True,
            depth=self.options.max_depth
        )
        self.svg_files = [file for file in self.files_in_src if file.lower().endswith('.svg')]
        if len(self.svg_files) == 0:
            print(f"\nВ директории {self.options.src} не обнаружены svg файлы!")
            sys.exit(1)
        else:
            self.main_actions()

    def analyze_cli_parameters(self):
        self.parser = argparse.ArgumentParser(
            prog=sys.argv[0],
            description='Скрипт для генерации qrc',
            epilog='Adminka-root 2023. https://github.com/adminka-root'
        )

        self.main_group = self.parser.add_argument_group(title='Параметры')

        self.main_group.add_argument(
            '-s', '--src', type=lambda x: os.path.expanduser(os.path.abspath(x)),
            default=self.script_dir,
            help=f"Указать исходную директорию (default={self.script_dir})",
            metavar='STR'
        )

        default_dest = os.path.join(
            os.path.dirname(self.script_dir), 'icons.qrc'
        )
        self.main_group.add_argument(
            '-d', '--dest', type=lambda x: os.path.expanduser(os.path.abspath(x)),
            default=default_dest, metavar='STR',
            help=f"Указать путь к выходному файлу qrc (default={default_dest})",
        )

        self.main_group.add_argument(
            '-m', '--max_depth', type=int, default=999999, metavar='INT',
            help='Максимальную глубину сканирования src директории (default=1)',
        )

        self.main_group.add_argument(
            '-r', '--run', action='store_true', default=False, required=False,
            help='Сгенерировать также py файл рядом с dest'
        )

        self.options = self.parser.parse_args(sys.argv[1:])

        err_message = ''
        if self.options.max_depth < 1:
            err_message += f"--depth='{self.options.max_depth}' < 1!\n"
        if not os.access(self.options.src, os.R_OK | os.X_OK):
            err_message += f"--src='{self.options.src}' директория не доступна!\n"

        dest_dirname = os.path.dirname(self.options.dest)
        self.icons_subpath = self.options.src.replace(dest_dirname + '/', '')

        if err_message:
            self.parser.print_help()
            print('\nОшибка:\n', err_message)
            sys.exit(1)
        self.create_dir(os.path.dirname(self.options.dest))

    def main_actions(self):
        qrc_lines = '<RCC>\n  <qresource prefix="icons">\n'

        for svg in self.svg_files:
            qrc_lines += f"    <file>{self.icons_subpath + svg}</file>\n"
        qrc_lines += '  </qresource>\n</RCC>'
        # print(qrc_lines)
        self.write_file(self.options.dest, qrc_lines)
        print(f"'{self.options.dest}' created!")
        if self.options.run:
            dest_py = self.options.dest[:self.options.dest.rindex('.')] + '.py'
            # conda activate image_optimizer
            # pip install pyqt5
            generate_py = run(
                ['pyrcc5', '-o', dest_py, self.options.dest],
                stdout=PIPE, stderr=PIPE, universal_newlines=True
            )
            if generate_py.returncode == 1:
                print('\nОшибка:\n', generate_py.stderr)
                sys.exit(1)
            else:
                print(f"'{dest_py}' created!")

if __name__ == "__main__":
    CreateQrc(
        script_dir=os.path.abspath(os.path.dirname(sys.argv[0]))
    )
