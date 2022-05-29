import setuptools


setuptools.setup(
    name="mktvis",
    version='0.0.1',
    author="Leon Morten Richter",
    author_email="github@leonmortenrichter.de",
    description="Mikrotik connection visualizer",
    url="TBD",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "Topic :: System :: Networking",
        "Typing :: Typed",
    ],
    keywords=[],
    python_requires='>=3.7',
    install_requires=[
        "RouterOS-api==0.17.0",
        "ipinfo==4.2.1",
        "pyyaml==6.0",
    ],
    extras_require={
        'dev': ['mypy', 'flake8', 'coverage', 'twine']
    },
    entry_points={
        "console_scripts": [
            ''
        ]
    }
)
