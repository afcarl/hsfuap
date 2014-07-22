try:
    from setuptools import setup
    from setuptools.extension import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

import numpy as np
import os

def cython_ext(extension, **kw):
    assert len(extension.sources) == 1
    base, ext = os.path.splitext(extension.sources[0])
    # setuptools sometimes "nicely" turns .pyx into .c for us
    assert ext in {'.pyx', '.c'}
    pyx_path = base + '.pyx'
    c_path = base + '.c'

    try:
        from Cython.Build import cythonize
    except ImportError:
        have_cythonize = False
    else:
        have_cythonize = True

    have_pyx = os.path.exists(pyx_path)
    have_c = os.path.exists(c_path)
    if have_cythonize and have_pyx:
        return cythonize([extension])[0]

    msg = "{} extension needs to be compiled, but {} not available".format(
        extension.name, "sources" if not have_pyx and not have_c
                        else "pyx source" if not have_pyx
                        else "cython")
    if not have_c:
        raise ImportError(msg)

    if have_pyx and have_c:
        pyx_time = os.path.getmtime(pyx_path)
        c_time = os.path.getmtime(c_path)
        if pyx_time > c_time:
            import datetime
            new_msg = "{pyx_name} has mtime {pyx_t}, {c_name} has {c_t}"
            raise ImportError(msg + ':\n' + new_msg.format(
                pyx_name=os.path.basename(pyx_path),
                c_name=os.path.basename(c_path),
                pyx_t=datetime.datetime.fromtimestamp(pyx_time),
                c_t=datetime.datetime.fromtimestamp(c_time),
            ))

    extension.sources[0] = c_path
    return extension

setup(
    name='hsfuap',
    version='0.1.0dev2014.07.22.0',
    author='Dougal J. Sutherland',
    author_email='dougal@gmail.com',
    url='https://github.com/dougalsutherland/hsfuap/',
    packages=[
        'hsfuap',
        'hsfuap.io',
        'hsfuap.kde',
        'hsfuap.kernels',
        'hsfuap.misc',
        'hsfuap.plotting',
        'hsfuap.sdm',
    ],
    description='Some miscellaneous utilities I find useful.',
    install_requires=[
        'humanize',
    ],
    entry_points={
        'console_scripts': [
            'hsfuap-nystroem = hsfuap.kernels.nystroem:main',
            'hsfuap-sdm-gather = hsfuap.sdm.gather_results:main',
            'hsfuap-sdm-kernelize = hsfuap.sdm.make_kernels:main',
        ],
    },
    ext_modules = [
        cython_ext(Extension('hsfuap.kde._bandwidth',
                             ['hsfuap/kde/_bandwidth.pyx'],
                             include_dirs=[np.get_include()],
                             extra_compile_args=['-fopenmp'],
                             extra_link_args=['-fopenmp'])),
    ],
    zip_safe=False,
)
