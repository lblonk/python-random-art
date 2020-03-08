from pathlib import Path
this_dir = Path(__file__).parent
from yattag import Doc

doc, tag, text = Doc().tagtext()

with tag('html'):
    with tag('body'):
        for item in (this_dir.parent/'static/gallery_images').iterdir():
            with tag('p'):
                text('')
            with tag('img', cls = 'image', src=f'/static/gallery_images{item.name}'):
                text('')


result = doc.getvalue()
print(result)