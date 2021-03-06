from setuptools import find_namespace_packages, setup

setup(
    author='Benoit Lagae',
    author_email='benoit.lagae@hotmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.9',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
    ],
    description=(''),
    # find actual keywords in future
    keywords=['literature', 'philology', 'text processing', 'archive'],
    license='AGPL',
    long_description="""Elisio is a scanning engine for (classical) Latin verse""",
    name='elisio',
    packages=find_namespace_packages(include=["elisio", "elisio.*"], exclude=["tests", "tests.*"]),
    url='https://github.com/blagae/elisio',
    version='0.1.0',
    install_requires=['whitakers_words @ git+git://github.com/blagae/whitakers_words.git#egg=whitakers_words']
)
