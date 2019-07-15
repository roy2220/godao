from distutils.core import setup


setup(
    name="godao",
    version="0.1.0",
    description="DAO Generator for Go",
    scripts=["bin/godao"],
    install_requires=["mako", "pyyaml", "yamlordereddictloader"],
)
