from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import compute

class RouterArgs:
    def __init__(self,
                 name,
                 network: compute.Network,
                 region="US-CENTRAL1"):
        self.name = name
        self.network = network
        self.region = region

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/routernat/
class Router(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: RouterArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.router = compute.Router(
            resource_name=name,
            network=args.network.id,
            region=args.region,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})