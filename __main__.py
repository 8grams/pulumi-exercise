"""A Google Cloud Python Pulumi program"""

import pulumi
from components.subnetwork import Subnetwork, SubnetworkArgs, IpRangeArgs
from components.router import Router, RouterArgs
from components.vpc import Vpc, VpcArgs, GlobalAddress, GlobalAddressArgs, ServiceNetworkingConnection, ServiceNetworkingConnectionArgs
from components.variables import region


# VPC
vpc = Vpc("main", VpcArgs(name="main"))

# Service Networking Connection
global_address = GlobalAddress(
    "vpc_peering_ip_address", 
    "gcp:modules:vpc", 
    GlobalAddressArgs(
        name="vpc-peering-ip-address",
        purpose="VPC_PEERING",
        address_type="INTERNAL",
        prefix_length=16, 
        network=vpc.vpc))

service_networking_connection = ServiceNetworkingConnection(
    "private_service_networking_connection", 
    ServiceNetworkingConnectionArgs(network=vpc.vpc, reserved_peering_ranges=[global_address.global_address])
)

# Subnetwork
subnetwork = Subnetwork("private", SubnetworkArgs(
    name="private",
    network=vpc.vpc,
    ip_cidr_range=IpRangeArgs(ip_cidr_range="10.0.0.0/18", range_name="default"),
    pod_address_range=IpRangeArgs(ip_cidr_range="10.48.0.0/14", range_name="k8s-pods-ip-range"),
    service_address_range=IpRangeArgs(ip_cidr_range="10.52.0.0/20", range_name="k8s-services-ip-range"),
    region=region,
    private_ip_google_access=True
))

# Router
router = Router("")
