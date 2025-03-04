from setuptools import setup, find_packages

setup(
    name="glance",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'keyboard',
        'Pillow',
        'qt-material',
    ],
)
