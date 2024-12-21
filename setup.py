from setuptools import setup, find_packages

setup(
    name="geek_analytics",
    packages=find_packages(),
    version="0.2.0",
    install_requires=[
        "streamlit",
        "plotly",
        "pandas",
        "streamlit-aggrid",
        "cryptography",
        "mysql-connector-python"
    ],
    python_requires=">=3.8",
)