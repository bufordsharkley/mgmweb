import os

import mutagen.mp3

"""A script in development, never actually tested"""

class NoMetadata(Exception):
    pass


def process_path(path):
    if not os.path.isabs(path):
        raise Exception('Only absolute paths', path)
    name = os.path.basename(path)
    name, ext = os.path.splitext(name)
    track_number = track_number_from_name(name)
    if ext == '.mp3':
        muta = mutagen.mp3.MP3(path, ID3=mutagen.id3.ID3)
    else:
        raise Exception(ext)
    if not muta:
        raise NoMetadata
    for field, info in muta.items():
        if field == 'TIT2':
            assert info.text == [name]
        elif field == 'TPE1':
            assert info.text == ['Matt Rabin and Hervey Okkles']
        elif field == 'TALB':
            assert info.text == ['Loon Talk']
        elif field == 'TRCK':
            assert info.text == [track_number]
        elif field == 'TCON':
            assert info.text == ['Loon']
        elif field == 'APIC:loon_talk.png':
            assert len(info.data) == 983388
        elif field == 'TDRC':
            assert info.text == [mutagen.id3.ID3TimeStamp(name.split('-')[0])]
        else:
            raise Exception(field)
    expected_fields = set(['TIT2', 'TPE1', 'TALB', 'TRCK', 'TCON',
                           'APIC:loon_talk.png', 'TDRC'])

    extra = set(muta.keys()) - expected_fields
    if extra:
        raise Exception(extra)
    print('VALIDATED {}'.format(path))
    return

def create_metadata(path):
    muta = mutagen.mp3.MP3(path, ID3=mutagen.id3.ID3)
    if muta.tags is None:
        muta.tags = mutagen.id3.ID3()
    #print(muta.tags is None)
    print('tag {}'.format(muta))
    #except mutagen.id3.ID3NoHeaderError:
    #    raise
    #muta = mutagen.File(path)
    #muta.add_tags()
    #muta = mutagen.id3.ID3(path)
    # 3: utf8
    name = os.path.basename(path)
    name, ext = os.path.splitext(name)
    track_number = track_number_from_name(name)
    #muta.add(TIT2(encoding=3, text=name))
    print(muta.tags)
    print(type(muta.tags))
    muta.tags["TIT2"] = mutagen.id3.TIT2(encoding=3, text=name)
    muta.tags["TPE1"] = mutagen.id3.TPE1(encoding=3, text="Matt Rabin and Hervey Okkles")
    muta.tags["TALB"] = mutagen.id3.TALB(encoding=3, text="Loon Talk")
    muta.tags["TRCK"] = mutagen.id3.TRCK(encoding=3, text=track_number)
    muta.tags["TCON"] = mutagen.id3.TCON(encoding=3, text="Loon")
    #muta.tags["APIC:loon_talk.png"] = mutagen.id3.TIT2(encoding=3, text=name)
    #muta.tags["TDRC"] = mutagen.id3.TIT2(encoding=3, text=mutagen.id3.ID3TimeStamp(name.split('-')[0]))

    #elif field == 'APIC:loon_talk.png':
    #    assert len(info.data) == 983388
    #assert info.text == [mutagen.id3.ID3TimeStamp(name.split('-')[0])]
    print(muta.tags)

"""
tags["TIT2"] = TIT2(encoding=3, text=title)
tags["TPE1"] = TPE1(encoding=3, text=u'mutagen Artist')
tags["TALB"] = TALB(encoding=3, text=u'mutagen Album Name')
tags["TRCK"] = TRCK(encoding=3, text=u'track_number')
tags["TCON"] = TCON(encoding=3, text=u'mutagen Genre')

tags["TPE2"] = TPE2(encoding=3, text=u'mutagen Band')
tags["COMM"] = COMM(encoding=3, lang=u'eng', desc='desc', text=u'mutagen comment')
tags["TCOM"] = TCOM(encoding=3, text=u'mutagen Composer')
tags["TDRC"] = TDRC(encoding=3, text=u'2010')

tags.save(fname)
#>>> meta['title'] = "This is a title"
#>>> meta['artist'] = "Artist Name"
#>>> meta['genre'] = "Space Funk"
#>>> meta.save(filePath, v1=2)
#>>> changed = EasyID3("8049.mp3")
#>>> changed
{'genre': [u'Space Funk'], 'title': [u'This is a title'], 'artist': [u'Artist Name']}
#        tags.add(TXXX(encoding=3, desc=u'ISBN', text=str(isbn)))
#        tags.save(filename)
    muta.add(TIT2(encoding=3, desc=u'ISBN', text=str(isbn)))
"""

def track_number_from_name(name):
    return ''.join(x[-2:] for x in name.split('-'))



loon_talks = (
        '2021-10-23.mp3',
        '2021-02-13.mp3',
        )

LOON_FOLDER = '/home/mgm/Desktop/UPLOAD'


for talk in loon_talks:
    path = os.path.join(LOON_FOLDER, talk)
    try:
        process_path(path)
    except NoMetadata:
        print('no metadata for {}'.format(path))
        create_metadata(path)
