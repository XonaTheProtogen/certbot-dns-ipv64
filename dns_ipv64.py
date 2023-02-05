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
    api_url = 'https://ipv64.net/api.php'

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='IPv64 credentials INI file.')

    def more_info(self):
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the IPv64 API.'

    def _validate_credentials(self, credentials: CredentialsConfiguration): 
        bearer_token = credentials.conf('bearer-token')

        if (len(bearer_token) != 32):
            logger.error("The bearer_token must be 32 characters long")
            raise errors.PluginError("The bearer_token must be 32 characters long")
        
        else:
            self.ipv64 = ipv64_client(bearer_token)

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'IPv64 credentials INI file',
            {
                'bearer-token': 'API key for IPv64 account',
            },

            self._validate_credentials

        )

    def _perform(self, domain, validation_name, validation):
        self.ipv64.add_txt_record(validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self.ipv64.del_txt_record(validation_name, validation)

"""Python implementation for ipv64.net"""
class ipv64_client():

    def __init__(self, bearer_token: str) -> None:
        self.api_url = 'https://ipv64.net/api.php'
        self.auth_header = {'Authorization': 'Bearer ' + bearer_token}

    def get_dns_zone(self, domain: str) -> str:
        stripped_domain = '.'.join(domain.split('.')[-2:])
        return stripped_domain

    def get_domain_praefix(self, domain: str, dns_zone: str) -> str:
        praefix = domain.removesuffix('.' + dns_zone)
        return praefix

    def add_txt_record(self, domain: str, content: str):
        
        dns_zone = self.get_dns_zone(domain)
        praefix = self.get_domain_praefix(domain, dns_zone)

        logger.info("Adding TXT-Record " + domain + " to zone " + dns_zone)

        json = {'add_record': dns_zone, 'praefix': praefix, 'type': 'TXT', 'content': content}
        response = requests.post(self.api_url, data=json, headers=self.auth_header)

        if (response.json()["info"] == "Unauthorized"):
            logger.error("The following error occured while adding the TXT-Record " + domain + " to the zone " + dns_zone + ": " + response.json()["info"])
            raise errors.PluginError("The following error occured while adding the TXT-Record " + domain + " to the zone " + dns_zone + ": " + response.json()["info"])

        if (response.json()["info"] != "success"):
            logger.error("The following error occured while adding the TXT-Record " + domain + " to the zone " + dns_zone + ": " + response.json()["add_record"])
            raise errors.PluginError("The following error occured while adding the TXT-Record " + domain + " to the zone " + dns_zone + ": " + response.json()["add_record"])

        else:
            logger.info("Successfully added TXT-Record "  + domain + " to the zone: " + dns_zone)

    def del_txt_record(self, domain: str, content: str):
        
        dns_zone = self.get_dns_zone(domain)
        praefix = self.get_domain_praefix(domain, dns_zone)

        logger.info("Deleting TXT-Record " + domain + " from the zone " + dns_zone)

        json = {'del_record': dns_zone, 'praefix': praefix, 'type': 'TXT', 'content': content}
        response = requests.delete(self.api_url, data=json, headers=self.auth_header)

        if (response.json()["info"] == "Unauthorized"):
            logger.warn("The following error occurred while deleting the TXT-Record " + domain + " in the zone " + dns_zone + ": " + response.json()["info"])
            
        if (response.json()["info"] != "success"):
            logger.warn("The following error occurred while deleting the TXT-Record " + domain + " in the zone " + dns_zone + ": " + response.json()["add_record"])

        else:
            logger.info("Successfully deleted the TXT-Record " + domain + " from the zone " + dns_zone)

