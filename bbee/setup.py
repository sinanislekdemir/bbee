import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bbee",
    version="0.1.0",
    author="Sinan Islekdemir",
    author_email="sinan@islekdemir.com",
    entry_points={
        'console_scripts': [
            'bbee = bbee:main',
        ]
    },
    description="A small C/C++ Builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sinanislekdemir/bbee",
    packages=setuptools.find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
