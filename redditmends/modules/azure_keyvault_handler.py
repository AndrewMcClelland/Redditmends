from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential

from accounts.azure_service_principal import SERVICE_PRINCIPALS


class KeyVaultHandler():
    def __init__(self, vault_url):

        credentials = ClientSecretCredential(
            client_id=SERVICE_PRINCIPALS["redditmends-app"]["clientID"],
            client_secret=SERVICE_PRINCIPALS["redditmends-app"]["secret"],
            tenant_id=SERVICE_PRINCIPALS["redditmends-app"]["tenantID"]
        )

        self.client = SecretClient(vault_url, credentials)

    def get_keyvault_secret(self, secret_name):
        secret_bundle = self.client.get_secret(secret_name)
        return secret_bundle.value
