from grafana_api.grafana_face import GrafanaFace

from .feature import (
    Snapshots,
)


class SnapshotFace:
    def __init__(
            self,
            auth,
            host="localhost",
            port=None,
            url_path_prefix="",
            protocol="https",
            verify=False,
    ):
        """
                Init auth
                :param auth: API Token  (https://grafana.com/docs/http_api/auth/#create-api-token)
                :param host: Host of the API server Ex. 127.0.0.1
                :param port: Ex. 3000  (default port)
                :param protocol: http or https
                 .. code-block:: python
                 grafana = GenerateSnapshot(auth='', host='xx', port=3000, protocol="https")
                 """
        self.api = GrafanaFace(
            auth,
            host=host,
            port=port,
            url_path_prefix=url_path_prefix,
            protocol=protocol,
            verify=verify,
        )
        self.snapshots = Snapshots(self.api, host, protocol, port)
