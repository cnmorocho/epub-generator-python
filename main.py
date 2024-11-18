import uuid
import tempfile
import os
import xml.etree.ElementTree as ET

class EpubMetadata:
    def __init__(self, title, author, language, description, subjects, publicationDate, publisher):
        self.title = title
        self.author = author
        self.language = language
        self.description = description
        self.subjects = subjects
        self.publicationDate = publicationDate
        self.publisher = publisher

class EpubContent:
    def __init__(self, chapters):
        self.chapters = chapters

class EpubChapter:
    def __init__(self, title, contentHtml, subtitle=None):
        self.title = title
        self.subtitle = subtitle
        self.contentHtml = contentHtml

class Epub:
    def __init__(self, metadata):
        if not isinstance(metadata, EpubMetadata):
            raise ValueError(f'metadata of type {type(metadata)} must be an instance of EpubMetadata')
        self.uuid = uuid.uuid4()
        self.title = metadata.title
        self.author = metadata.author
        self.language = metadata.language
        self.description = metadata.description
        self.subjects = metadata.subjects
        self.publicationDate = metadata.publicationDate
        self.publisher = metadata.publisher
        self.tempDir = tempfile.mkdtemp()
        self.templateDir = os.path.dirname(os.path.realpath(__file__)) + '/templates'

    def __createEpubStructure(self):
        try:
            os.makedirs(self.tempDir + '/META-INF')
            os.makedirs(self.tempDir + '/OEBPS')
            os.makedirs(self.tempDir + '/OEBPS/Text')
            os.makedirs(self.tempDir + '/OEBPS/Styles')
            os.makedirs(self.tempDir + '/OEBPS/Images')
        except Exception as e:
            print(e)

    def __createTocFile(self):
        root = ET.Element('ncx', {'xmlns': 'http://www.daisy.org/z3986/2005/ncx/', 'version': '2005-1'})
        head = ET.SubElement(root, 'head')
        ET.SubElement(head, 'meta', {'name': 'dtb:uid', 'content': str(self.uuid)})
        ET.SubElement(head, 'meta', {'name': 'dtb:depth', 'content': '1'})
        docTitle = ET.SubElement(ET.SubElement(root, 'docTitle'), 'text')
        


