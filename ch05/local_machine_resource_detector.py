import socket
from opentelemetry.sdk.resources import Resource, ResourceDetector


class LocalMachineResourceDetector(ResourceDetector):
    def detect(self):
        hostname = socket.gethostname()
        print(hostname)
        ip_address = socket.gethostbyname(hostname)
        print(ip_address)
        return Resource.create(
            {
                "net.host.name": hostname,
                "net.host.ip": ip_address,
            }
        )
