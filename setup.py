import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dca", # Replace with your own username
    version="v0.1",
    author="Orkahub",
    author_email="scuervo91@gmail.com",
    description="Decline Curve Analysis For Oil and Gas Industry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scuervo91/reservoirpy",
    download_url="https://github.com/orkahub/dcapy/archive/0.1.tar.gz",
    packages=setuptools.find_packages(),
    include_package_data = True,
    package_data = {'':['*.csv','*.json']},
    install_requires=[            
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scipy',
        'scikit-image',
        'statsmodels'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
