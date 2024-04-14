"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import compute
from components.variables import region
from components.subnetwork import Subnetwork, SubnetworkArgs, IpRangeArgs
from components.router import Router, RouterArgs
from components.vpc import Vpc, VpcArgs, GlobalAddress, GlobalAddressArgs, ServiceNetworkingConnection, ServiceNetworkingConnectionArgs
from components.nat import RouterNatSubnetworkArgs, RouterNat, RouterNatArgs, RouterNatIpAddress, RouterNatIpAddressArgs
from components.firewall import Firewall, FirewallArgs


# VPC
vpc = Vpc("main", VpcArgs(name="main"))

# Service Networking Connection
global_address = GlobalAddress(
    "onxp_vpc_peering", 
    "gcp:modules:vpc",
    GlobalAddressArgs(
        name="vpc-peering-ip-address",
        purpose="VPC_PEERING",
        address_type="INTERNAL",
        prefix_length=16, 
        network=vpc.vpc))

service_networking_connection = ServiceNetworkingConnection(
    "onxp-service-networking-connection", 
    "gcp:modules:vpc:vpcpeering", 
    ServiceNetworkingConnectionArgs(
        network=vpc.vpc, 
        reserved_peering_ranges=[global_address.global_address]))

# Subnetwork
subnetwork = Subnetwork(
    "onxp-subnet",
    "gcp:modules:subnetwork",
    SubnetworkArgs(
        name="onxp-subnet",
        network=vpc.vpc,
        ip_cidr_range=IpRangeArgs(ip_cidr_range="10.0.0.0/18", range_name="default"),
        pod_address_range=IpRangeArgs(ip_cidr_range="10.48.0.0/14", range_name="k8s-pods-ip-range"),
        service_address_range=IpRangeArgs(ip_cidr_range="10.52.0.0/20", range_name="k8s-services-ip-range"),
        region=region,
        private_ip_google_access=True))

# Router
router = Router(
    "onxp-router", 
    "gcp:modules:router",
    RouterArgs(
        name="onxp-router",
        network=vpc,
        region=region
    ))

# NAT
# create IP Address for NAT
nat_address = RouterNatIpAddress(
    "onxp-nat-ip", 
    "gcp:modules:nat:ipaddress",
    RouterNatIpAddressArgs(
        name="onxp-nat-ip",
        address_type="EXTERNAL",
        network_tier="PREMIUM"
    )
)

nat_subnetwork = RouterNatSubnetworkArgs(
    "onxp-nat-subnetwork",
    "gcp:modules:nat:subnetwork",
    RouterNatSubnetworkArgs(
        subnetwork=subnetwork,
        source_ip_ranges_to_nat=["ALL_IP_RANGES"]
    )
)

nat = RouterNat(
    "onxp-nat",
    "gcp:modules:nat",
    RouterNatArgs(
        name="onxp-nat",
        subnetworks=[nat_subnetwork],
        router=router,
        region=region,
        nat_ip_allocate_option="MANUAL_ONLY",
        source_subnetwork_ip_ranges_to_nat="LIST_OF_SUBNETWORKS",
        nat_ips=[nat_address],
        subnetwork=nat_subnetwork
    )
)

# Firewall
ssh_firewall = Firewall(
    "allow-ssh",
    "gcp:modules:firewall:ssh",
    FirewallArgs(
        name="allow-ssh",
        network=vpc,
        source_ranges=["0.0.0.0/0"],
        allows=[compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22"]
        )]
    )
)

http_firewall = Firewall(
    "allow-http",
    "gcp:modules:firewall:http",
    FirewallArgs(
        name="allow-http",
        network=vpc,
        source_ranges=["0.0.0.0/0"],
        target_tags=["http-server"],
        allows=[compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["80", "443"]
        )]
    )
)
