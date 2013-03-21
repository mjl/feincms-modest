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
    classifiers      = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: FeinCMS',
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
