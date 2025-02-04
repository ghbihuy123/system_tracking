from setuptools import setup, find_packages

# Read the content of your README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="system_tracking",
    version="0.1.1",
    packages=find_packages(where='source'),
    package_dir={"": "source"},
    include_package_data=True,
    install_requires=[
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A brief description of the system_tracking package.",
    author="Huy Luu Quang",
    author_email="ghbihuy123@example.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)