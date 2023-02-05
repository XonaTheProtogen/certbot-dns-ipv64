# certbot-dns-ipv64
This plugin for certbot allows users of the DynDNS provider IPv64.net to prove ownership of a domain name and request SSL-Certificates. Internally the plugin adds and removes the requested TXT-Records for the ACME-Challenge by using the provided IPv64-API.

**This plugin is currently in an untested state!**

## Building the plugin
To build the plugin, run the following command:

```python3 ./setup.py build```

## Installing the plugin
To install the plugin, run the following command:

```python3 ./setup.py install```

To make sure the plugin installed correctly, use this command:

```certbot plugins```

Certbot should output the following lines:
```
* dns-ipv64
Description: Obtain certificates using a DNS TXT record (if you are using IPv64
for DNS).
Interfaces: Authenticator, Plugin
Entry point: dns-ipv64 = dns_ipv64:Authenticator
```

## Using the plugin ##
First you will need to create a configuration file with your api token. The content of the file has to look like this:

```
dns_ipv64_bearer_token = 123456789abcdefg123456789abcdefg
```

To request a certificate, run the command:

```certbot certonly --authenticator dns-ipv64```

The plugin allows the usage of the following arguments:
| Argument                         | Description                                                     |
| ---------------------------------| --------------------------------------------------------------- |
| --dns-ipv64-credentials          | Path to the credentials file                                     |
| --dns-ipv64-propagation-seconds  | Manually set the propagation time (default 10 seconds)          |

