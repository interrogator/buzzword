import os

from setuptools import setup


def read(fname):
    """
    Helper to read README
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


setup(
    name="buzzword",
    version="0.0.1",  # bump2version will edit this automatically!
    description="Web-app for corpus linguistics",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Danny McDonald",
    include_package_data=True,
    zip_safe=False,
    packages=["buzzword"],
    scripts=["bin/buzzword"],
    author_email="daniel.mcdonald@uzh.ch",
    license="MIT",
    keywords=[],
    install_requires=[
        "buzz==2.0.5",
        "python-dotenv==0.10.3",
        "flask==1.1.1",
        "dash==1.1.1",
        "dash-daq==0.1.7",
    ],
    dependency_links=[],
)
