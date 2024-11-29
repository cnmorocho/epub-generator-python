from src.main import Epub, EpubChapter, EpubContent, EpubMetadata, EpubConfig
from src.utils.language import Language
import os


def test_build_epub() -> None:
    """
    Given the metadata and content of an epub, and an ouput directory
    When is all correct
    Then should build an epub file
    """

    metadata = EpubMetadata('David Copperfield', 'Charles Dickens', Language.English, 'David Copperfield is the eighth novel by Charles Dickens. The story follows the life of David Copperfield from childhood to maturity.', [
                            'fiction', 'literature', 'Classics'], '1850-05-01', 'Bradbury & Evans')
    chapters = [
        {
            'title': 'Chapter 1',
            'subtitle': 'I Am Born',
            'contentHTML': f'<p>Whether I shall turn out to be the hero of my own life, or whether that station will be held by anybody else, these pages must show. To begin my life with the beginning of my life, I record that I was born (as I have been informed and believe) on a Friday, at twelve o\'clock at night. It was remarked that the clock began to strike, and I began to cry, simultaneously.</p>',
        },
        {
            'title': 'Chapter 2',
            'subtitle': 'I Observe',
            'contentHTML': '<p>Of course, the fact that I had the misfortune to be a posthumous child, and to be born on a Friday at twelve o\'clock at night, is a wonderful coincidence. This may perhaps account for my not being considered by the fondest of mothers, or the fondest of aunts, to be anything better than a poor child.</p>',
        },
        {
            'title': 'Chapter 3',
            'subtitle': 'I Have a Change',
            'contentHTML': '<p>At last, I came to the conclusion that I must leave Peggotty and the house at once, and go home to my mother. On the road thither, I considered that if I had no friends, I should like to wander about the streets and see the world.</p>',
        },
    ]

    epub_chapters = [
        EpubChapter(
            title=chapter['title'], content_html=chapter['contentHTML'], subtitle=chapter.get('subtitle'))
        for chapter in chapters
    ]

    content = EpubContent(epub_chapters)
    output_dir = '.'
    Epub(metadata, content, output_dir, EpubConfig(styles_path='__tests__/utils/styles.css')).build()

    assert os.path.exists(os.path.join(output_dir, f'{metadata.title}.epub'))
