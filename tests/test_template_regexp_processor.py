from template_regexp_processor import __version__
from template_regexp_processor import TexJinja2Preprocessor
import time
import io

def test_version():
    assert __version__ == '0.1.0'


bg = time.time()
o = io.StringIO()
with open('romaneio_80mm.tex', 'r') as f:
    p = TexJinja2Preprocessor()
    for l in p.run(f):
        o.write(l)
print("Took {} seconds".format(time.time() - bg))

print(o.getvalue())