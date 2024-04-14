from typing import Sequence
from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import compute, servicenetworking

class VpcArgs:
    def __init__(self,
                 name: str, 
                 routing_mode="REGIONAL", 
                 auto_create_subnetworks=False,
                 mtu="1460",
                 delete_default_routes_on_create=False
                 ):
        self.name = name
        self.routing_mode = routing_mode
        self.auto_create_subnetworks = auto_create_subnetworks
        self.mtu = mtu
        self.delete_default_routes_on_create = delete_default_routes_on_create

class GlobalAddressArgs:
    def __init__(self,
                 name: str,
                 purpose,
                 address_type,
                 prefix_length,
                 network: compute.Network):
        self.name = name
        self.purpose = purpose
        self.address_type = address_type
        self.prefix_length = prefix_length
        self.network = network

# https://www.pulumi.com/registry/packages/gcp/api-docs/servicenetworking/connection/
class ServiceNetworkingConnectionArgs:
    def __init__(self,
                 network: compute.Network,
                 reserved_peering_ranges: Sequence[compute.GlobalAddress],
                 service="servicenetworking.googleapis.com"
                ):
        self.network = network
        self.service = service
        self.reserved_peering_ranges = reserved_peering_ranges
        
# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/network/
class Vpc(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: VpcArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label , name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        self.vpc = compute.Network(name,
                                       routing_mode=args.routing_mode,
                                       auto_create_subnetworks=args.auto_create_subnetworks,
                                       mtu=args.mtu,
                                       delete_default_routes_on_create=args.delete_default_routes_on_create,
                                       opts=child_opts)
        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/globaladdress/
class GlobalAddress(ComponentResource):
    def __init__(self,
                 name: str,
                 label: str,
                 args: GlobalAddressArgs,
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        self.global_address = compute.GlobalAddress(resource_name=name,
                                                    purpose=args.purpose,
                                                    address_type=args.address_type,
                                                    prefix_length=args.prefix_length,
                                                    network=args.network.id,
                                                    opts=child_opts)
        self.register_outputs({})

class ServiceNetworkingConnection(ComponentResource):
    def __init__(self,
                 name: str,
                 label: str,
                 args: ServiceNetworkingConnectionArgs,
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        self.service_networking_connection = servicenetworking.Connection(
            resource_name=name,
            network=args.network.id,
            service=args.service,
            reserved_peering_ranges=[address.name for address in args.reserved_peering_ranges],
            opts=child_opts)
        self.register_outputs({})