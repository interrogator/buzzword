import os

from setuptools import setup


def read(fname):
    """
    Helper to read README
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


ASSETS = "buzzword/parts/assets"
DOCS = "docs"

assets = [os.path.join(ASSETS, i) for i in os.listdir(ASSETS)]

docs = [os.path.join(DOCS, i) for i in os.listdir(DOCS)]

setup(
    name="buzzword",
    version="1.2.2",  # bump2version will edit this automatically!
    description="Web-app for corpus linguistics",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Danny McDonald",
    include_package_data=True,
    zip_safe=False,
    packages=["buzzword", "docs", "buzzword/parts"],
    package_dir={"buzzword/parts/assets": "buzzword/parts/assets", "docs": "docs"},
    scripts=["bin/buzzword", "bin/buzzword-create"],
    package_data={"buzzword/parts": assets, "docs": docs},
    data_files=[("buzzword/parts/assets", assets), ("docs", docs)],
    author_email="daniel.mcdonald@uzh.ch",
    license="MIT",
    keywords=[],
    install_requires=[
        "buzz>=3.0.5",
        "python-dotenv==0.10.3",
        "flask==1.1.1",
        "dash==1.1.1",
        "dash-core-components==1.1.1",
        "dash-html-components==1.0.0",
        "dash-renderer==1.0.0",
        "dash-table==4.1.0",
        "dash-daq==0.1.7",
    ],
)
