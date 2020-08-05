import setuptools
from src import bl_info

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name         = "blender-auto-reload-libraries-gandalf3",
    version      = ".".join(map(str, bl_info["version"])),
    author       = bl_info["author"],
    author_email = "gandalf3@blendermonkey.com",
    description  = bl_info["description"],
    long_description = readme,
    url = bl_info["doc_url"],
    packages = setuptools.find_packages(),
    install_requires = ['watchdog'],
)
