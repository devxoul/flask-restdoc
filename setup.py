from distutils.core import setup
from restdoc import VERSION

setup(
    name='Flask-Restdoc',
    packages=['restdoc'],
    version=VERSION,
    description='Flask-Restdoc is a simple tool that generates RESTful API documentation automatically from python files.',
    long_description=open('README.rst').read(),
    license='MIT License',
    author='Su Yeol Jeon',
    author_email='devxoul@gmail.com',
    url='https://github.com/devxoul/flask-restdoc',
    download_url='https://pypi.python.org/packages/source/F/Flask-Restdoc/Flask-Restdoc-%s.tar.gz' % VERSION,
    keywords=['Flask', 'REST', 'API', 'Documentation'],
    classifiers=[]
)