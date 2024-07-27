from setuptools import find_packages, setup

setup(
    name="nk-shared",
    version="0.1",
    description="Shared models for nk",
    url="https://github.com/narfman0/nk",
    author="narfman0",
    author_email="narfman0@blastedstudios.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=True,
    test_suite="tests",
)
