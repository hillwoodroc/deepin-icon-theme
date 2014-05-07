#!/usr/bin/env python
#-*- coding:utf-8 -*-

class PngGenerate(object):

    def __init__(self, theme_dir, src_dir):
        self.theme = theme_dir
        self.src = src_dir
        self.config_file = os.path.join(self.theme, "index.theme")
        self._init_config()
        self._init_dirs()


    def _init_config(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        self.directories = self.config.get('Icon Theme', 'Directories').split(',')
        self.theme_name = self.config.get('Icon Theme', 'Name')


    def _init_dirs(self):
        self.icon_dirs = {}
        # check if directory in format '16x16/apps'
        if self.directories[0].split('/')[0][0].isdigit():
            self.digit_first = True
        else:
            self.digit_first = False

        for directory in self.directories:
            if self.digit_first:
                size = i.split('/')[0]
                dir_type = i.split('/')[1]
            else:
                size = i.split('/')[0]
                dir_type = i.split('/')[1]
            if not self.icon_dirs.has_key(dir_type):
                self.icon_dirs[dir_type] = set()
            self.icon_dirs[icon_type].add(size)


    def _generate_png(self, image_path, icon_type):
        image_name = os.path.basename(image_path)
        for size in self.icon_dirs[icon_type]:
            if size == 'scalable':
                continue
            length = size.split('x')[0]
            if self.digit_first:
                output_dir = os.path.join(self.theme, "%sx%s" % (length, length), icon_type)
            else:
                output_dir = os.path.join(self.theme, icon_type, "%sx%s" % (length, length))

            output_file = os.path.join(output_dir, image_name)
            PngGenerate.svg_to_png(image_path, length, output_file)


    def convert(self):
        for directory in os.listdir(self.src):
            current_path = os.path.join(self.src, directory)
            for svg_file in os.listdir(directory):
                image_path = os.path.join(current_path, svg_file)
                if not svg_file.endswith(".svg"):
                    continue
                if not self.icon_dirs.has_key(directory):
                    raise Exception, 'Theme does not contain dir: %s' % directory
                self._generate_png(image_path, directory)


    @classmethod
    def svg_to_png(input_file, size, output_file):
        dir_name = os.path.dirname(output_file)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        os.system("inkscape -f %s -e %s -w %s" % (input_file, size, output_file))



if __name__ == "__main__":
    converter = PngGenerate('Deepin', 'src')
    converter.convert()
