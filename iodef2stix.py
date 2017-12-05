import os
import traceback

import jnius_config
jnius_config.set_classpath('.', os.path.join(os.getcwd(), r'./java_class/*'))

import jnius
from jnius import autoclass


FileUtils = autoclass('org.apache.commons.io.FileUtils')
STIXPackage = autoclass('org.mitre.stix.stix_1.STIXPackage')
IODEF2STIX = autoclass('converter.IODEF2STIX')
ConverterException = autoclass('exception.ConverterException')
ValidationException = autoclass('exception.ValidationException')
Java_File = autoclass('java.io.File')


def main(*args):
    stixXsdPath = os.path.join(os.getcwd(), r'./stixXsd/')  # STIX 驗證檔之放置路徑
    iodefXsdPath = os.path.join(os.getcwd(), r'./iodefXsd/')  # IODEF 驗證檔之放置路徑
    filePath = os.path.join(os.getcwd(), r'./example/')  # 請填入欲轉換之檔案位置
    savedPath = os.path.join(os.getcwd(), r'./example_output/')  # 請填入轉換後之檔案儲存位置
    print(filePath)
    encoding = 'UTF-8'  # 文字編碼

    try:
        converter = IODEF2STIX(stixXsdPath, iodefXsdPath)
        with open(filePath, 'r', encoding=encoding) as iodefXml:
            iodefString = iodefXml.read()

        stixPackage = converter.getStix(iodefString)
        stixString = stixPackage.toXMLString(true)

        savedPath = savedPath + f.name.split('-')[-1]
        with open(savedPath, 'w', encoding=encoding) as f:
            f.write(stixString)
    except Exception:
        traceback.print_exc()


main()
