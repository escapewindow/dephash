from setuptools import setup, find_packages

setup(
    name="reqhash",
    version="0.1.0",
    description="requirements.txt hasher",
    author="Aki Sasaki",
    author_email="aki@escapewindow.com",
    url="https://github.com/escapewindow/reqhash",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "reqhash = reqhash:main",
        ],
    },
    license="MPL2",
    install_requires=[
        "pip>=8.1.2",
        "six",
        "virtualenv>=15.0.2",
    ],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    )
)
