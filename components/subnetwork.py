from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import compute

class IpRangeArgs:
    def __init__(self, 
                 ip_cidr_range,
                 range_name="default"
                 ):
          self.range_name = range_name
          self.ip_cidr_range = ip_cidr_range
        

class SubnetworkArgs:
    def __init__(self,
                 name: str, 
                 network: compute.Network,
                 ip_cidr_range: IpRangeArgs,
                 pod_address_range: IpRangeArgs,
                 service_address_range: IpRangeArgs,
                 region="US-CENTRAL1",
                 private_ip_google_access=True
                 ):
        self.name = name
        self.network = network
        self.ip_cidr_range = ip_cidr_range
        self.pod_address_range = pod_address_range
        self.service_address_range = service_address_range
        self.region = region
        self.private_ip_google_access = private_ip_google_access

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/subnetwork/
class Subnetwork(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: SubnetworkArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        self.subnetwork = compute.Subnetwork(
            resource_name=name,
            network=args.network.id,
            ip_cidr_range=args.ip_cidr_range.ip_cidr_range,
            region=args.region,
            private_ip_google_access=args.private_ip_google_access,
            secondary_ip_ranges=[compute.SubnetworkSecondaryIpRangeArgs(
                range_name=args.pod_address_range.range_name,
                ip_cidr_range=args.pod_address_range.ip_cidr_range,
                ), 
                compute.SubnetworkSecondaryIpRangeArgs(
                    range_name=args.service_address_range.range_name,
                    ip_cidr_range=args.service_address_range.ip_cidr_range,
                    )],
                    opts=child_opts)
        self.register_outputs({})
        