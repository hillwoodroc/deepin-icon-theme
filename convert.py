#!/usr/bin/env python2
#-*- coding:utf-8 -*-
#

# Depends on imagemagick inkscape
# Get png file metadata 'identify -verbose FILE.png'
# write png metadate 'convert INFILE.png -set Title "foobar the great" OUTFILE.png'

import os
import sys
import subprocess
import ConfigParser
import time

OPTIPNG = '/usr/bin/optipng'
INKSCAPE = '/usr/bin/inkscape'
CONVERT = '/usr/bin/convert'
IDENTIFY = '/usr/bin/identify'

INDEX = 'index.theme'
SOURCE = ('src/apps','src/categories','src/devices','src/games','src/mimetypes')
inkscape_process = None

cf = ConfigParser.ConfigParser()
cf.read(INDEX)

def get_info(Section,Key):
    return cf.get(Section,Key)

DIRECTORIES = get_info('Icon Theme','Directories').split(',')
MAINDIR = get_info('Icon Theme','Name')

if DIRECTORIES[0].split('/')[0].replace('x','').isdigit:
    is_Directories_Digit_First = True
else:
    is_Directories_Digit_First = False


folder_tuple = {}
for i in DIRECTORIES:
    if not is_Directories_Digit_First:
        first = i.split('/')[0]
        second = i.split('/')[1]
    else:
        second = i.split('/')[0]
        first = i.split('/')[1]

    if not folder_tuple.has_key(first):
        folder_tuple[first] = set()
    folder_tuple[first].add(second)


def main(SRC):
    def optimize_png(png_file):
        if os.path.exists(OPTIPNG):
            process = subprocess.Popen([OPTIPNG, '-quiet', '-o7', png_file])
            process.wait()

    def set_png_metadata(png_file):
    # write png metadate 'convert INFILE.png -set Title "foobar the great" OUTFILE.png'
        if os.path.exists(CONVERT):
            now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            information = "Autogen by Debhelper @ %s" % now
            process = subprocess.Popen([CONVERT,png_file,'-set','Identify',information,png_file])
            process.wait()

    def check_png_metadata(png_file):
    # Get png file metadata 'identify -verbose FILE.png'
        if os.path.exists(IDENTIFY) and os.path.exists(png_file):
            process = subprocess.Popen([IDENTIFY,'-verbose',png_file],stdout=subprocess.PIPE)
            result = process.communicate()
            if 'Identify' in result[0]:
                return True
            else:
                return False
        else:
            return False

    def wait_for_prompt(process, command=None):
        if command is not None:
            process.stdin.write((command+'\n').encode('utf-8'))
        output = process.stdout.read(1)
        if output == b'>':
            return
        output += process.stdout.read(1)
        while output != b'\n>':
            output += process.stdout.read(1)
            output = output[1:]
    def start_inkscape():
        process = subprocess.Popen([INKSCAPE, '--shell'], bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        wait_for_prompt(process)
        return process

    def inkscape_render(icon_file, width, height,output_file):
        global inkscape_process
        if inkscape_process is None:
            inkscape_process = start_inkscape()
        wait_for_prompt(inkscape_process,'%s -w %s -w %s -e %s' %(icon_file, width, height, output_file))
        optimize_png(output_file)
        set_png_metadata(output_file)

    class ContentHandler():
        def __init__(self,file,force=False,filter=None):
            self.force = force
            self.filter = filter
            self.file = file
            self.section = file.split('/')[2]
            print self.file
            print self.section
            self.size = folder_tuple[self.section]
            self.icon_name = file.split('/')[3].replace('.svg','')
        def render(self):
            for size in self.size:
                if 'scalable' in size:
                    pass
                else:
                    if 'x' in size:
                        height = size.split('x')[0]
                        width = size.split('x')[0]
                    else:
                        height = size
                        width = size
                    if is_Directories_Digit_First:
                        dir = os.path.join(MAINDIR,"%sx%s" % (width,height), self.section)
                    else:
                        dir = os.path.join(MAINDIR,self.section,"%sx%s" % (width,height) )
                    outfile = os.path.join(dir, self.icon_name+'.png')
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    if self.force or not os.path.exists(outfile):
                        inkscape_render(self.file, width,height, outfile)
                        sys.stdout.write('.')
                    else:
                        if check_png_metadata(outfile):
                            inkscape_render(self.file, width,height,outfile)
                            sys.stdout.write('-')
                        else:
                            sys.stdout.write('Pass %s ...' % outfile)





    if not os.path.exists(MAINDIR):
        os.mkdir(MAINDIR)
    print('')
    print('Rendering from SVGs in ', SRC)
    for file in os.listdir(SRC):
        if file[-4:] == '.svg':
            file = os.path.join(SRC,file)
            handler = ContentHandler(file)
            handler.render()
    print ('')

for sources in SOURCE:
    SRC = os.path.join('.',sources)
    main(SRC)
