
from setuptools import setup

setup(
    name='certbot-dns-ipv64',
    version='1.0.0',
    description='IPv64 DNS Authenticator for Certbot',
    author='Pascal Fleischhauer',
    author_email='pascalfleischhauer@gmail.com',
    license='Apache License 2.0',
    package='dns-ipv64.py',
    install_requires=[
        'certbot',
        'requests',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-ipv64 = dns_ipv64:Authenticator',
        ],
    },
)