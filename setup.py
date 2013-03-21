from setuptools import setup

from gallery import __version__

setup(
    name             = "feincms-gallery",
#    version          = __version__,
    author           = "Martin J. Laubach",
    author_email     = "pypi+feincms-gallery@laubach.at",
    description      = ("Gallery content type for FeinCMS"),
    license          = "BSD",
#    keywords         = "feincms content type gallery",
    url              = "http://github.com/mjl/feincms-gallery",
#    py_modules       = ['ecglist'],
    long_description = open('README.rst').read(),
    test_suite       = "tests",
#    classifiers      = [
#        "Development Status :: 5 - Production/Stable",
#        "Topic :: Communications :: Email",
#        "Intended Audience :: Developers",
#        "License :: OSI Approved :: BSD License",
#        "Programming Language :: Python",
#    ],
)
