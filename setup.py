from distutils.core import setup


setup(
    name="godao",
    version="0.1.0",
    description="DAO Generation for Go",
    scripts=["bin/godao"],
    install_requires=["mako", "pyyaml", "yamlordereddictloader"],
)
