from setuptools import setup, find_packages

setup(
    name="dephash",
    version="0.2.0",
    description="requirements.txt dependency hasher",
    author="Aki Sasaki",
    author_email="aki@escapewindow.com",
    url="https://github.com/escapewindow/dephash",
    py_modules=["dephash"],
    entry_points={
        "console_scripts": [
            "dephash = dephash:cli",
        ],
    },
    license="MPL2",
    install_requires=[
        "click",
        "hashin",
        "pip>=8.1.2",
        "six",
        "virtualenv",
    ],
    tests_require=[
        "tox",
    ],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    )
)
