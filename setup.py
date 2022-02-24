import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='jsonclasses-pymongo',
      version='3.3.0',
      description='jsonclasses integration with pymongo',
      long_description=README,
      long_description_content_type="text/markdown",
      author='Fillmula Inc.',
      author_email='victor.teo@fillmula.com',
      license='MIT',
      packages=find_packages(exclude=("tests")),
      package_data={'jsonclasses_pymongo': ['py.typed']},
      zip_safe=False,
      url='https://github.com/fillmula/jsonclasses-pymongo',
      include_package_data=True,
      python_requires='>=3.10',
      install_requires=[
            'pymongo>=4.0.1,<5.0.0',
            'inflection-plus>=0.1.0,<2.0.0',
            'qsparser>=1.1.0,<2.0.0'
      ])
