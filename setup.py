"""
Manus Agent - セットアップスクリプト

このスクリプトはManus Agentアプリケーションのインストールを行います。
"""

from setuptools import setup, find_packages

setup(
    name="manus_agent",
    version="0.1.0",
    description="metagptベースのDevinのような複雑なソフトウェア開発能力を持つ汎用Agent",
    author="Manus Team",
    packages=find_packages(),
    install_requires=[
        "kivy>=2.0.0",
        "kivymd>=1.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
        "requests>=2.25.0",
        "pygments>=2.10.0",
        "pytest>=6.0.0",
    ],
    entry_points={
        'console_scripts': [
            'manus_agent=main:main',
        ],
    },
    python_requires='>=3.8',
)
