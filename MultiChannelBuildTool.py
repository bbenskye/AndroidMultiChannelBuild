#!/usr/bin/python
# coding=utf-8
import zipfile
import shutil
import os
import sys
import subprocess

def init():
    subprocess.call("rm -r  output_*" ,shell=True)
    subprocess.call("rm -r  temp_*" ,shell=True)
    subprocess.call("rm -r  *.DS_Store" ,shell=True)
    subprocess.call("rm -r  *.zip" ,shell=True)
    subprocess.call("rm -r  last_netease_*" ,shell=True)


def complete():
    subprocess.call("rm -r  temp_*" ,shell=True)
    subprocess.call("rm -r  *.DS_Store" ,shell=True)
    subprocess.call("rm -r  *.zip" ,shell=True)
    subprocess.call("rm -r  output_*" ,shell=True)


def writeChannel():
    init()
    # 空文件 便于写入此空文件到apk包中作为channel文件
    src_empty_file = 'info/imoney.txt'
    # 创建一个空文件（不存在则创建）
    f = open(src_empty_file, 'w')
    f.close()
    # 获取当前目录中所有的apk源包
    src_apks = []
    # python3 : os.listdir()即可，这里使用兼容Python2的os.listdir('.')
    for file in os.listdir('.'):
        if os.path.isfile(file):
            extension = os.path.splitext(file)[1][1:]
            if extension in 'apk':
                src_apks.append(file)

    # 获取渠道列表
    channel_file = 'info/channel.txt'
    f = open(channel_file)
    lines = f.readlines()
    f.close()
    for src_apk in src_apks:
        # file name (with extension)
        src_apk_file_name = os.path.basename(src_apk)
        # 分割文件名与后缀
        temp_list = os.path.splitext(src_apk_file_name)
        # name without extension
        src_apk_name = temp_list[0]
        # 后缀名，包含.   例如: ".apk "
        src_apk_extension = temp_list[1]

        # 创建生成目录,与文件名相关
        output_dir = 'output_' + src_apk_name + '/'

        last_dir = 'last_' + src_apk_name + '/'
        # 目录不存在则创建
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if not os.path.exists(last_dir):
            os.mkdir(last_dir)

        # 创建临时目录,与文件名相关
        temp_dir = 'temp_' + src_apk_name + '/'
        # 目录不存在则创建
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)


            # 从源apk文件中copy一个临时的文件，因为源文件有可能已经打过了渠道包
        out_temp_apk = temp_dir + src_apk_name + '_temp' + src_apk_extension;
        # copy一份没有渠道信息的apk
        zin = zipfile.ZipFile(src_apk, 'a', zipfile.ZIP_DEFLATED)
        zout = zipfile.ZipFile(out_temp_apk, 'w')
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if (item.filename[0:16:] != 'META-INF/channel'):
                zout.writestr(item, buffer)
        zout.close()
        zin.close()

        # 遍历渠道号并创建对应渠道号的apk文件
        for line in lines:
            # 获取当前渠道号，因为从渠道文件中获得带有\n,所有strip一下
            target_channel = line.strip()
            # 拼接对应渠道号的apk
            target_apk = output_dir + src_apk_name + "_" + target_channel + src_apk_extension

            last_apk = last_dir + src_apk_name + "_" + target_channel + src_apk_extension
            # 拷贝建立新apk
            shutil.copy(out_temp_apk, target_apk)
            # zip获取新建立的apk文件
            zipped = zipfile.ZipFile(target_apk, 'a', zipfile.ZIP_DEFLATED)
            # 初始化渠道信息
            empty_channel_file = "META-INF/channel_{channel}".format(channel=target_channel)

            for item in zipped.infolist():
                if (item.filename[0:16:] == 'META-INF/channel'):
                    print item.filename
            # 写入渠道信息
            zipped.write(src_empty_file, empty_channel_file)
            # 关闭zip流
            zipped.close()

            zipalign = os.environ.get('zg')
            ## zipAlign
            zipAlign = "%s -v 4 %s %s" % (zipalign,target_apk, last_apk)
            subprocess.call(zipAlign, shell=True)

            zipshell = "zip apks.zip %s"%last_dir
            subprocess.call(zipshell, shell=True)
    complete()

writeChannel()





