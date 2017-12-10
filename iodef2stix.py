import os
import traceback
import logging

import jnius_config
jnius_config.set_classpath('.', os.path.join(os.getcwd(), r'./java_class/*'))

from jnius import autoclass, JavaException

logging.basicConfig(level=logging.INFO)

Java_String = autoclass('java.lang.String')
Java_File = autoclass('java.io.File')

Java_ConverterException = autoclass('exception.ConverterException')
Java_ValidationException = autoclass('exception.ValidationException')

Java_IntelInfo = autoclass('converter.IntelInfo')
Java_IODEFDoc = autoclass('iodef.service.IODEFDoc')
Java_XmlDoc = autoclass('util.XmlDoc')
Java_IODEF2STIX = autoclass('converter.IODEF2STIX')
Java_LoadIODEF = autoclass('iodef.service.LoadIODEF')


class ConverterException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        self.JavaObject = Java_ConverterException(message, *args, **kwargs)

    def __repr__(self):
        return self.message


class ValidationException(Exception):
    def __init__(self, format, message, content, *args, **kwargs):
        self.format = format
        self.message = message
        self.content = content
        self.JavaObject = Java_ValidationException(
            Java_String(format.encode()),
            Java_String(message.encode()),
            Java_String(content.encode()),
            *args, **kwargs,
        )

    def __repr__(self):
        return self.message


class IODEF2STIX(object):
    def __init__(self, stixXsdPath, iodefXsdPath, *args, **kwargs):
        self.stixXsdPath = stixXsdPath
        self.iodefXsdPath = iodefXsdPath

        Java_stixXsdPath = Java_String(stixXsdPath.encode())
        Java_iodefXsdPath = Java_String(iodefXsdPath.encode())

        self.JavaObject = Java_IODEF2STIX(Java_stixXsdPath, Java_iodefXsdPath, *args, **kwargs)
        self.convertToStix = self.JavaObject.convertToStix

    def getStix(self, iodefString):
        try:
            iodef = Java_LoadIODEF.getIODEFDocFromString(Java_String(iodefString.encode()))
        except JavaException as se:
            raise ConverterException('無法成功開啟檔案：{}'.format(se.args))
        return self.IodefToStix(iodef)

    def IodefToStix(self, iodef):
        method = iodef.getIncident().get(0).getMethod().get(0)
        typeName = iodef.getIncident().get(0).getExtPurpose() + method.getReferenceOrDescription().get(0).getValue()

        intelInfo = Java_IntelInfo.getStixTypeInfo(Java_String(typeName.encode()))

        if not intelInfo:
            raise ConverterException('事件或情報名稱有誤')

        iodefString = Java_IODEFDoc.getIodefString(iodef)

        try:
            iodefxsdpath = os.path.join(self.iodefXsdPath, intelInfo.getIodefXsd() + '.xsd')
            iodefXsd = Java_File(Java_String(iodefxsdpath.encode()))
            Java_XmlDoc.validateXML(iodefXsd, Java_String(iodefString.encode()))
        except JavaException as se:
            raise ValidationException('IODEF', '格式驗證有誤：\n' + se.innermessage + '\n', iodefString)

        stixPackage = self.convertToStix(iodef, intelInfo)
        stixString = stixPackage.toXMLString(True)

        try:
            stixxsdpath = os.path.join(self.stixXsdPath, intelInfo.getStixXsd(), intelInfo.getStixXsd() + '.xsd')
            stixXsd = Java_File(Java_String(stixxsdpath.encode()))
            Java_XmlDoc.validateXML(stixXsd, Java_String(stixString.encode()))
        except JavaException as se:
            raise ValidationException('STIX', '格式驗證有誤：\n' + se.innermessage + '\n', stixString)

        return stixPackage


def main(*args):
    stixXsdPath = r'stixXsd/'  # STIX 驗證檔之放置路徑
    iodefXsdPath = r'iodefXsd/'  # IODEF 驗證檔之放置路徑
    fileDirPath = r'example/'  # 請填入欲轉換之檔案位置
    savedDirPath = r'example_output/'  # 請填入轉換後之檔案儲存位置
    encoding = 'UTF-8'  # 文字編碼

    for fileName in os.listdir(fileDirPath):
        filePath = os.path.join(fileDirPath, fileName)
        if os.path.isfile(filePath) and not fileName.startswith('.'):
            logging.debug('Processing {}'.format(filePath))
            try:
                converter = IODEF2STIX(stixXsdPath, iodefXsdPath)
                with open(filePath, 'r', encoding=encoding) as iodefXml:
                    iodefString = iodefXml.read()

                stixPackage = converter.getStix(iodefString)
                stixString = stixPackage.toXMLString(True)

                with open(savedDirPath + fileName, 'w', encoding=encoding) as f:
                    f.write(stixString)
                logging.info('Finish processing {}'.format(fileName))
            except ConverterException as e:
                logging.error('Failed to process {}: {}'.format(fileName, e.message))
            except ValidationException as e:
                logging.error('Failed to process {}: {}'.format(fileName, e.message))
            except Exception as e:
                traceback.print_exc()


if __name__ == "__main__":
    main()
