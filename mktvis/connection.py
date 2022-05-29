import ssl
import ipinfo
import routeros_api

from mktvis.config import MKTVISConfig


class IPInfoConnection:

    def __init__(self, access_token) -> None:
        self._access_token = access_token
        self._handler = ipinfo.getHandler(access_token)

    @classmethod
    def from_config(cls, config: MKTVISConfig):
        return cls(
            config.IP_INFO_ACCESS_TOKEN
        )

    @property
    def ipinfo_api(self):
        return self._handler


class RouterConnection:

    def __init__(self, host, username, password, port=8728, use_ssl=False, ssl_verify=True, ssl_verify_hostname=True, ssl_cert_path=None) -> None:

        ssl_context = None
        if use_ssl:
            ssl_context = ssl.create_default_context(cafile=ssl_cert_path)

        self._connection = routeros_api.RouterOsApiPool(
            host,
            username=username,
            password=password,
            port=port,
            use_ssl=use_ssl,
            ssl_verify=ssl_verify,
            ssl_verify_hostname=ssl_verify_hostname,
            ssl_context=ssl_context,
            plaintext_login=True
        )

        self._api = self._connection.get_api()

    @classmethod
    def from_config(cls, config: MKTVISConfig):
        return cls(
            config.ROUTERBOARD_ADDRESS,
            username=config.ROUTERBOARD_USER,
            password=config.ROUTERBOARD_PASSWORD,
            port=config.ROUTERBOARD_PORT,
            use_ssl=config.ROUTERBOARD_USE_SSL,
            ssl_verify=config.ROUTERBOARD_SSL_CERTIFICATE_VERIFY,
            ssl_cert_path=config.ROUTERBOARD_SSL_CERTIFICATE_PATH
        )

    @property
    def router_api(self):
        # TODO delay connection
        return self._api
