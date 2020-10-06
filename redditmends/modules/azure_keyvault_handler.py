from azure.keyvault.secrets import SecretClient
from azure.common.credentials import ServicePrincipalCredentials

from accounts.azure_service_principal import SERVICE_PRINCIPALS


class KeyVaultHandler():
    def __init__(self, vault_url):

        credentials = ServicePrincipalCredentials(
            client_id=SERVICE_PRINCIPALS["redditmends-app"]["clientID"],
            secret=SERVICE_PRINCIPALS["redditmends-app"]["secret"],
            tenant=SERVICE_PRINCIPALS["redditmends-app"]["tenantID"]
        )

        self.client = KeyVaultClient(credentials)
        self.client = SecretClient
        self.vault_url = vault_url

    def get_keyvault_secret(self, secret_id):
        secret_bundle = self.client.get_secret(
            self.vault_url, secret_id, secret_version="")
        return secret_bundle.value
