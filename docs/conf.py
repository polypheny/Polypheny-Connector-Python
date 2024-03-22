# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Polypheny-Connector-Python'
copyright = '2024, The Polypheny Project'
author = 'The Polypheny Project'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinx.ext.doctest',
    'myst_parser',
]

autodoc_typehints = "description"
intersphinx_mapping = {
        'python': ('https://docs.python.org/3/', None),
}
doctest_test_doctest_blocks = ''

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


def linkcode_resolve(domain, info):
    if domain != 'py':
        return None

    module = info['module']
    if module.split('.')[0] != 'polypheny':
        print(module)
        raise "Not supported: {}".format(module)

    __import__(module)
    
    fullname = info['fullname']

    from functools import reduce
    try:
        code = reduce(getattr, fullname.split('.'), globals()[module]).__code__
    except:
        return None
    from pathlib import Path
    p = Path(code.co_filename)
    lineno = code.co_firstlineno

    filename = p.parts[-1]
    if p.parts[-2] != 'polypheny':
        return None
    
    if Path('..', 'polypheny', filename).exists(): # and is_file
        return None

    return "https://github.com/polypheny/Polypheny-Connector-Python/blob/proto-without-grpc/polypheny/{}#L{}".format(filename, lineno)
