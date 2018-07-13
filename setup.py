from setuptools import setup

setup(
	name='tagit',
	version='1.0.0',
	description='Generates tags for a given AKN fulltext document',
	packages=['tagit'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		'Flask==1.0.2',
		'gensim==3.4.0',
		'nltk==3.3',
		'Flask-Bootstrap==3.3.7.1',
		'stop-words==2015.2.23.1'
	],
)