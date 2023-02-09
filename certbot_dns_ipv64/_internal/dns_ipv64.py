"""DNS Authenticator for IPv64."""
import logging
import requests

from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration

logger = logging.getLogger(__name__)

class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for IPv64."""

    description = 'Obtain certificates using a DNS TXT record (if you are using IPv64 for DNS).'

    @classmethod
    def add_parser_arguments(cls, add) -> None:
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='IPv64 credentials INI file.')

    def more_info(self):
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using the IPv64 API.'

    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None: 
        bearer_token = credentials.conf('bearer-token')

        if (len(bearer_token) != 32):
            logger.error('The bearer_token must be 32 characters long')
            raise errors.PluginError('The bearer_token must be 32 characters long')
        
        self.ipv64 = IPv64Client(bearer_token)

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'IPv64 credentials INI file',
            {
                'bearer-token': 'API key for IPv64 account',
            },

            self._validate_credentials

        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self.ipv64.add_txt_record(validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self.ipv64.del_txt_record(validation_name, validation)

"""Python implementation for ipv64.net"""
class IPv64Client():

    def __init__(self, bearer_token: str) -> None:
        self.api_url = 'https://ipv64.net/api.php'
        self.auth_header = {'Authorization': 'Bearer ' + bearer_token}

    def _get_dns_zone(self, domain: str) -> str:
        stripped_domain = '.'.join(domain.split('.')[-2:])
        return stripped_domain

    def _get_domain_prefix(self, domain: str, dns_zone: str) -> str:
        len_dns_zone = len(dns_zone)
        prefix = domain[:-len_dns_zone - 1]
        return prefix

    def _check_errors(self, json: str) -> None:

        if (json['info'] == 'Unauthorized'):
            logger.error('The following error occured: ' + json['info'])
            raise errors.PluginError('The following error occured: ' + json['info'])

        if (json['info'] != 'success'):
            logger.error('The following error occured: ' + json['add_record'])
            raise errors.PluginError('The following error occured: ' + json['add_record'])

        logger.info('Successfully performed action')

    def add_txt_record(self, domain: str, content: str) -> None:
        
        dns_zone = self._get_dns_zone(domain)
        prefix = self._get_domain_prefix(domain, dns_zone)

        logger.info('Adding TXT-Record ' + domain + ' to the zone ' + dns_zone)

        json = {'add_record': dns_zone, 'praefix': prefix, 'type': 'TXT', 'content': content}
        response = requests.post(self.api_url, data=json, headers=self.auth_header)

        self._check_errors(response.json())

    def del_txt_record(self, domain: str, content: str) -> None:
        
        dns_zone = self._get_dns_zone(domain)
        prefix = self._get_domain_prefix(domain, dns_zone)

        logger.info('Deleting TXT-Record ' + domain + ' from the zone ' + dns_zone)

        json = {'del_record': dns_zone, 'praefix': prefix, 'type': 'TXT', 'content': content}
        response = requests.delete(self.api_url, data=json, headers=self.auth_header)

        self._check_errors(response.json())

