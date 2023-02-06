from setuptools import setup, find_packages

setup(
    name='certbot-dns-ipv64',
    version='1.0.0',
    description='IPv64 DNS Authenticator for Certbot',
    author='Pascal Fleischhauer',
    author_email='pascalfleischhauer@gmail.com',
    license='Apache License 2.0',
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=[
        'certbot',
        'requests',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-ipv64 = certbot_dns_ipv64._internal.dns_ipv64:Authenticator',
        ],
    },
)
