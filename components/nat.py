from typing import Sequence
from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import compute

class RouterNatSubnetworkArgs:
    def __init__(self,
                 subnetwork: compute.Subnetwork,
                 source_ip_ranges_to_nat=["ALL_IP_RANGES"]):
        self.name = subnetwork.id
        self.source_ip_ranges_to_nat = source_ip_ranges_to_nat

class RouterIpAddressArgs:
    def __init__(self,
                 name: str,
                 address_type="EXTERNAL",
                 network_tier="PREMIUM",):
        self.name = name
        self.address_type = address_type
        self.network_tier = network_tier

class RouterNatArgs:
    def __init__(self,
                 name,
                 subnetworks: Sequence[RouterNatSubnetworkArgs],
                 router: compute.Router,
                 region="US-CENTRAL1",
                 nat_ip_allocate_option="MANUAL_ONLY",
                 source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS",
                 nat_ips: RouterIpAddressArgs=None):
        self.name = name
        self.router = router
        self.region = region
        self.nat_ip_allocate_option = nat_ip_allocate_option
        self.source_subnetwork_ip_ranges_to_nat = source_subnetwork_ip_ranges_to_nat
        self.nat_ips = nat_ips
        self.subnetworks = subnetworks

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/routernat/
class RouterNat(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: RouterNatArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.nat = compute.RouterNat(
            resource_name=name,
            router=args.router.id,
            region=args.region,
            nat_ip_allocate_option=args.nat_ip_allocate_option,
            source_subnetwork_ip_ranges_to_nat=args.source_subnetwork_ip_ranges_to_nat,
            nat_ips=args.nat_ips,
            subnetworks=args.subnetworks,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})
