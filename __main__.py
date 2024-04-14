"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import compute, container
from components.variables import region, project_id
from components.subnetwork import Subnetwork, SubnetworkArgs, IpRangeArgs
from components.router import Router, RouterArgs
from components.vpc import Vpc, VpcArgs, GlobalAddress, GlobalAddressArgs, ServiceNetworkingConnection, ServiceNetworkingConnectionArgs
from components.nat import RouterNatSubnetworkArgs, RouterNat, RouterNatArgs, RouterNatIpAddress, RouterNatIpAddressArgs
from components.firewall import Firewall, FirewallArgs
from components.kubernetes import KubernetesCluster, KubernetesClusterArgs
from components.node_pool import NodePool, NodePoolArgs
from components.sa import ServiceAccount, ServiceAccountArgs

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

# Create Kubernetes Cluster
kubernetes = KubernetesCluster(
    "onxp-cluster",
    "gcp:modules:kubernetes:cluster",
    KubernetesClusterArgs(
        name="onxp-cluster",
        network=vpc,
        subnetwork=subnetwork,
        addons_config=container.ClusterAddonsConfigArgs(
            horizontal_pod_autoscaling=container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(disabled=True),
            http_load_balancing=container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(disabled=True)
        ),
        release_channel=container.ClusterReleaseChannelArgs(channel="REGULAR"),
        ip_allocation_policy=container.ClusterIpAllocationPolicyArgs(
            cluster_secondary_range_name=subnetwork.pod_ip_range,
            services_secondary_range_name=subnetwork.service_ip_range
        ),
        private_cluster_config=container.ClusterPrivateClusterConfigArgs(
            enable_private_nodes=True,
            enable_private_endpoint=False,
            master_ipv4_cidr_block="172.24.0.0/28"
            
        ),
        workload_identity_config=container.ClusterWorkloadIdentityConfigArgs(
            workload_pool=project_id + ".svc.id.goog"
        ),
        location="US-CENTRAL1",
        initial_node_count=1,
        remove_default_node_pool=True,
        logging_service=None,
        monitoring_service=None,
        networking_mode="VPC_NATIVE",
    )
)

# Create service account for nodepool
node_pool_sa = ServiceAccount(
    "onxp-nodepool-sa",
    "gcp:modules:kubernetes:nodepool:sa",
    ServiceAccountArgs(
        name="onxp-nodepool-sa",
        account_id="onxp-nodepool-sa"
    )
)

# Create Nodepool
node_pool = NodePool(
    "onxp-nodepool",
    "gcp:modules:kubernetes:nodepool",
    NodePoolArgs(
        name="onxp-nodepool",
        cluster=kubernetes,
        node_config=container.ClusterNodeConfigArgs(
            preemptible=True,
            machine_type="e2-micro",
            disk_size_gb=80,
            disk_type="pd-balanced",
            service_account=node_pool_sa,
            oauth_scopes = [
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        ),
        autoscaling=container.NodePoolAutoscalingArgs(
            min_node_count=1,
            max_node_count=10,
            location_policy="BALANCED"
        ),
        management=container.NodePoolManagementArgs(
            auto_repair=True,
            auto_upgrade=True
        ),
        node_count=1,
        node_locations=["US-CENTRAL1-A"]
    )
)
