import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydynamics",
    version="0.0.8",
    author="Dan Goscomb",
    author_email="dan@flowplex.co.uk",
    description="Talk to On-Prem Dynamics CRM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dangoscomb/pydynamics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=[
        'lxml',
        'requests'
    ]
)