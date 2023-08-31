from setuptools import setup, find_packages

setup(
	author='ronik-v',
	name='Investing Bot',
	license='Apache-2.0 license',
	packages=find_packages(include=['src']),
	install_requires=[
		'aiogram', 'pandas', 'pandas-datareader', 'numpy', 'matplotlib'
	]
)
