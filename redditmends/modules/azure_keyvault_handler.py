from azure.keyvault import KeyVaultClient
from azure.common.credentials import ServicePrincipalCredentials

from accounts.azure_service_principal import service_principals

class KeyVaultHandler():
	def __init__(self, vault_url):

		credentials = ServicePrincipalCredentials(
			client_id = service_principals["redditmends-app"]["clientID"],
			secret = service_principals["redditmends-app"]["secret"],
			tenant = service_principals["redditmends-app"]["tenantID"]
		)

		self.client = KeyVaultClient(credentials)
		self.vault_url = vault_url

	def get_keyvault_secret(self, secret_id):
		secret_bundle = self.client.get_secret(self.vault_url, secret_id, secret_version = "")
		return secret_bundle.value
