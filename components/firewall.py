from typing import Sequence
from pulumi import ResourceOptions
from pulumi_gcp import compute

class FirewallArgs:
    def __init__(self,
                 name,
                 network: compute.Network,
                 source_ranges: Sequence[str],
                 allows: Sequence[compute.FirewallAllowArgs]):
        self.name = name
        self.network = network
        self.source_ranges = source_ranges
        self.allow = allows

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/firewall/
class Firewall:
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: FirewallArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.firewall = compute.Firewall(
            resource_name=name,
            network=args.network.id,
            source_ranges=args.source_ranges,
            allows=args.allows,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})