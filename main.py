import uuid
import tempfile
import os
import xml.etree.ElementTree as ET
import zipfile
import shutil


class EpubMetadata:
    def __init__(self, title, author, language, description, subjects, publication_date, publisher):
        self.title = title
        self.author = author
        self.language = language
        self.description = description
        self.subjects = subjects
        self.publication_date = publication_date
        self.publisher = publisher


class EpubContent:
    def __init__(self, chapters):
        if not isinstance(chapters, list):
            raise ValueError(f'chapters must be a list')
        if not all(isinstance(chapter, EpubChapter) for chapter in chapters):
            raise ValueError(f'metadata of type {type(
                EpubChapter)} must be an instance of EpubChapter')
        self.chapters = chapters


class EpubChapter:
    def __init__(self, title, content_html, subtitle=None):
        self.id = None
        self.title = title
        self.subtitle = subtitle
        self.content_html = content_html
        self.relative_path = None


class Epub:
    def __init__(self, metadata, content, output_dir):
        if not isinstance(metadata, EpubMetadata):
            raise ValueError(f'metadata of type {type(
                metadata)} must be an instance of EpubMetadata')
        if not isinstance(content, EpubContent):
            raise ValueError(f'metadata of type {type(
                content)} must be an instance of EpubContent')
        self.metadata = metadata
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.dirname(
            os.path.realpath(__file__)) + '/templates'
        self.content = content
        self.output_dir = output_dir
        self.uuid = uuid.uuid4()

    def build(self):
        self.__create_epub_structure()
        self.__create_chapters_files()
        self.__create_toc_page()
        self.__create_toc_file()
        self.__create_metainf_file()
        self.__create_content_file()
        self.__create_mymetype_file()

        epub_file_path = os.path.join(
            self.output_dir, f'{self.metadata.title}.epub')

        with zipfile.ZipFile(epub_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as epub_zip:
            mimetype_path = os.path.join(self.temp_dir, 'mimetype')
            epub_zip.write(mimetype_path, 'mimetype',
                           compress_type=zipfile.ZIP_STORED)

            for root, _, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, self.temp_dir)
                    if archive_name != 'mimetype':
                        epub_zip.write(file_path, archive_name)

        self.__clean_up()

    def __create_epub_structure(self):
        try:
            os.makedirs(os.path.join(self.temp_dir, 'META-INF'))
            os.makedirs(os.path.join(self.temp_dir, 'OEBPS'))
            os.makedirs(os.path.join(self.temp_dir, 'OEBPS', 'Text'))
            os.makedirs(os.path.join(self.temp_dir, 'OEBPS', 'Styles'))
            os.makedirs(os.path.join(self.temp_dir, 'OEBPS', 'Images'))
        except Exception as e:
            print(e)

    def __create_toc_file(self):
        root = ET.Element(
            'ncx', {'xmlns': 'http://www.daisy.org/z3986/2005/ncx/', 'version': '2005-1'})
        head = ET.SubElement(root, 'head')
        ET.SubElement(
            head, 'meta', {'name': 'dtb:uid', 'content': str(self.uuid)})
        ET.SubElement(head, 'meta', {'name': 'dtb:depth', 'content': '1'})
        ET.SubElement(ET.SubElement(root, 'docTitle'),
                      'text').text = self.metadata.title
        nav_map = ET.SubElement(root, 'navMap')

        for index, chapter in enumerate(self.content.chapters):
            nav_point = ET.SubElement(nav_map, 'navPoint', {
                                      'id': f'navPoint-{index + 1}', 'playOrder': f'{index + 1}'})
            ET.SubElement(ET.SubElement(nav_point, 'navLabel'),
                          'text').text = chapter.title
            ET.SubElement(nav_point, 'content', {'src': chapter.relative_path})

        tree = ET.ElementTree(root)
        with open(os.path.join(self.temp_dir, 'OEBPS', 'toc.ncx'), 'w') as toc:
            tree.write(toc, encoding="utf-8", xml_declaration=True)

    def __create_chapters_files(self):
        for index, chapter in enumerate(self.content.chapters):
            chapter.id = f'C{index + 1}'
            chapter.relative_path = f'Text/{chapter.id}.xhtml'

            html = ET.Element('{http://www.w3.org/1999/xhtml}html')
            head = ET.SubElement(html, 'head')
            title = ET.SubElement(head, 'title')
            title.text = chapter.title
            ET.SubElement(head, 'link', {
                          'rel': 'stylesheet', 'type': 'text/css', 'href': '../Styles/styles.css'})
            body = ET.SubElement(html, 'body')
            h1 = ET.SubElement(body, 'h1')
            h1.text = chapter.title

            if chapter.subtitle:
                h2 = ET.SubElement(body, 'h2')
                h2.text = chapter.subtitle

            tree = ET.ElementTree(html)
            tree.write(chapter.relative_path, encoding='utf-8',
                       xml_declaration=True, method='xml')

    def __create_metainf_file(self):
        root = ET.Element('container', {
                          'version': '1.0', 'xmlns': 'urn:oasis:names:tc:opendocument:xmlns:container'})
        root_files = ET.SubElement(root, 'rootfiles')
        ET.SubElement(root_files, 'rootfile', {
                      'full-path': 'OEBPS/content.opf', 'media-type': 'application/oebps-package+xml'})

        tree = ET.ElementTree(root)
        with open(os.path.join(self.temp_dir, 'META-INF', 'container.xml'), 'w') as metainf:
            tree.write(metainf, encoding="utf-8", xml_declaration=True)

    def __create_content_file(self):
        root = ET.Element('package', {
                          'version': '2.0', 'unique-identifier': 'BookId', 'xmlns': 'http://www.idpf.org/2007/opf'})
        metadata = ET.SubElement(root, 'metadata', {
                                 'xmlns:dc': 'http://purl.org/dc/elements/1.1/', 'xmlns:opf': 'http://www.idpf.org/2007/opf'})
        identifier = ET.SubElement(metadata, 'dc:identifier', {
                                   'id': 'BookId', 'opf:scheme': 'UUID'})
        identifier.text = f'urn:uuid:{self.uuid}'
        ET.SubElement(metadata, 'dc:title').text = self.metadata.title
        ET.SubElement(metadata, 'dc:creator', {
                      'opf:file-as': self.metadata.author, 'opf:role': 'aut'}).text = self.metadata.author
        ET.SubElement(metadata, 'dc:language').text = self.metadata.language
        if self.metadata.subjects:
            ET.SubElement(metadata, 'dc:subject').text = ', '.join(
                self.metadata.subjects)
        ET.SubElement(
            metadata, 'dc:description').text = self.metadata.description
        if self.metadata.publication_date:
            ET.SubElement(metadata, 'dc:date', {
                          'opf:event': 'publication'}).text = self.metadata.publication_date
        if self.metadata.publisher:
            ET.SubElement(
                metadata, 'dc:publisher').text = self.metadata.publisher
        ET.SubElement(metadata, 'meta', {
                      'name': 'cover', 'content': 'cover.jpeg'})
        manifest = ET.SubElement(root, 'manifest')
        ET.SubElement(manifest, 'item', {
                      'id': 'toc.xhtml', 'href': 'Text/toc.xhtml', 'media-type': 'application/xhtml+xml'})
        for chapter in self.content.chapters:
            ET.SubElement(manifest, 'item', {
                          'id': chapter.id, 'href': chapter.relative_path, 'media-type': 'application/xhtml+xml'})
        spine = ET.SubElement(root, 'spine', {'toc': 'ncx'})
        ET.SubElement(spine, 'itemref', {'idref': 'toc.xhtml'})
        for chapter in self.content.chapters:
            ET.SubElement(spine, 'itemref', {'idref': chapter.id})

        tree = ET.ElementTree(root)
        with open(os.path.join(self.temp_dir, 'OEBPS', 'content.opf'), 'w') as content:
            tree.write(content, encoding="utf-8", xml_declaration=True)

    def __create_toc_page(self):
        root = ET.Element('html', {'xmlns': 'http://www.w3.org/1999/xhtml'})
        ET.SubElement(ET.SubElement(root, 'head'),
                      'title').text = 'Table of Contents'
        body = ET.SubElement(root, 'body')
        ET.SubElement(body, 'h1').text = 'Table of Contents'
        ol = ET.SubElement(body, 'ol')
        for chapter in self.content.chapters:
            ET.SubElement(ET.SubElement(ol, 'li'), 'a', {
                          'href': os.path.basename(chapter.relative_path)}).text = chapter.title

        tree = ET.ElementTree(root)
        with open(os.path.join(self.temp_dir, 'OEBPS', 'Text', 'toc.xhtml'), 'w') as toc_page:
            tree.write(toc_page, encoding="utf-8", xml_declaration=True)

    def __create_mymetype_file(self):
        mimetype_path = os.path.join(self.temp_dir, 'mimetype')
        with open(mimetype_path, 'w', encoding='utf-8') as mimetype:
            mimetype.write('application/epub+zip')

    def __clean_up(self):
        shutil.rmtree(self.temp_dir)
