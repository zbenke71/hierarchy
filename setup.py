from setuptools import setup, find_namespace_packages

setup(
    name='gyermelyi-hierarchy',
    version='0.1',
    packages=find_namespace_packages(include=['gyermelyi.hierarchy', 'gyermelyi.hierarchy.*']),
    namespace_packages=['gyermelyi'],
    description='A package for hierarchy manipulation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zoltán Benke',
    author_email='benkez@gyermelyi.hu',
    url='https://gyermelyi.hu',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
