#!/usr/bin/env python3
"""
AgentScope-PaaS 框架安装配置

支持通过pip install -e . 进行开发模式安装
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件作为长描述
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# 读取版本信息
version_file = Path(__file__).parent / "agentscope_paas" / "__init__.py"
version = "1.0.0"
if version_file.exists():
    version_content = version_file.read_text(encoding="utf-8")
    for line in version_content.split('\n'):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"').strip("'")
            break

setup(
    name="agentscope-paas",
    version=version,
    author="AgentScope-PaaS Team",
    author_email="support@agentscope-paas.example.com",
    description="配置文件驱动的智能体PaaS化框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/agentscope-paas",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/agentscope-paas/issues",
        "Source": "https://github.com/your-repo/agentscope-paas",
        "Documentation": "https://github.com/your-repo/agentscope-paas/wiki",
    },

    # 包配置
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    python_requires=">=3.8,<4.0",

    # 核心依赖
    install_requires=[
        "agentscope~=1.0.19",
        "pyyaml>=6.0,<7.0",
        "python-dateutil>=2.8.0,<3.0",
        "requests>=2.28.0,<3.0",
    ],

    # 可选依赖
    extras_require={
        "dev": [
            "mypy>=1.0.0,<2.0",
            "black>=22.0.0,<24.0",
            "isort>=5.10.0,<6.0",
            "flake8>=4.0.0,<5.0",
            "pytest>=7.0.0,<8.0",
            "pytest-cov>=4.0.0,<5.0",
            "ipython>=8.0.0,<9.0",
        ],
        "test": [
            "pytest>=7.0.0,<8.0",
            "pytest-cov>=4.0.0,<5.0",
            "pytest-mock>=3.10.0,<4.0",
            "pytest-asyncio>=0.21.0,<1.0",
        ],
        "docs": [
            "sphinx>=4.5.0,<6.0",
            "sphinx-rtd-theme>=1.0.0,<2.0",
        ],
        "all": [
            # 包含所有可选依赖
            "python-dotenv>=1.0.0,<2.0",
            "typing-extensions>=4.4.0,<5.0",
            # 开发工具
            "mypy>=1.0.0,<2.0",
            "black>=22.0.0,<24.0",
            "isort>=5.10.0,<6.0",
            "flake8>=4.0.0,<5.0",
            # 测试工具
            "pytest>=7.0.0,<8.0",
            "pytest-cov>=4.0.0,<5.0",
            "ipython>=8.0.0,<9.0",
        ],
    },

    # 包含数据文件
    include_package_data=True,
    package_data={
        "agentscope_paas": [
            "configs/*.yaml",
            "docs/*.md",
        ],
    },

    # 命令行入口
    entry_points={
        "console_scripts": [
            "agentscope-paas=agentscope_paas.cli:console_script_main",
        ],
    },

    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],

    # 关键词
    keywords="agentscope paas agent framework llm ai configuration-driven",

    # 许可证
    license="MIT",

    # zip_safe=False，因为包包含需要特殊处理的文件
    zip_safe=False,
)