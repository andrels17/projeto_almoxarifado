"""
Script de configuração para Streamlit Cloud
"""

from setuptools import setup, find_packages

setup(
    name="dashboard-almoxarifado",
    version="1.0.0",
    description="Dashboard do Almoxarifado - Sistema de análise de dados",
    author="Andre",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "streamlit>=1.28.0",
        "plotly>=5.15.0",
        "numpy>=1.24.0",
        "openpyxl>=3.1.0",
        "scipy>=1.11.0",
    ],
    python_requires=">=3.8",
)
