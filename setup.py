#!/usr/bin/python3
import setuptools

setuptools.setup(
    name="music-visualization-framework",
    version="0.1",
    author="Nick Pesce",
    author_email="nickpesce22@gmail.com",
    description="Music Visualization Framework",
    url=["https://github.com/nickpesce/music-visualization-framework"],
    packages=["music_visualization_framework"],
    entry_points={
        "console_scripts": ["musicd=music_visualization_framework.musicd:start"],
    },
    install_requires=["numpy", "pyserial"],
    classifiers=["License :: MIT License", "Operating System :: Linux",],
)
