from setuptools import setup, find_packages

from modest import __version__

setup(
    name             = "feincms-modest",
    version          = __version__,
    author           = "Martin J. Laubach",
    author_email     = "pypi+feincms-modest@laubach.at",
    description      = ("Gallery content type for FeinCMS"),
    license          = "BSD",
    keywords         = "feincms content type gallery",
#    url              = "http://github.com/mjl/feincms-modest",
    packages         = find_packages(),
    long_description = open('README.rst').read(),
    test_suite       = "tests",
    zip_safe         = False,
    include_package_data = True,
    requires         = ['feincms (>=1.5)'],
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
