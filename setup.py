from setuptools import setup, find_packages

# load libs and readme...
with open('requirements.txt') as file:
	requires = file.readlines()

with open('README.md') as file:
	readme = file.readlines()


setup(
	author='ronik-v',
	name='Investing Bot',
	license='Apache-2.0 license',
	packages=find_packages(include=['src']),
	python_requires='>=3.11',
	url='https://github.com/ronik-v/Investing-Telegram-Bot'
)
