from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import compute, container

class KubernetesClusterArgs:
    def __init__(self,
                 name: str,
                 network: compute.Network,
                 subnetwork: compute.Subnetwork,
                 addons_config: container.ClusterAddonsConfigArgs,
                 release_channel: container.ClusterReleaseChannelArgs,
                 ip_allocation_policy: container.ClusterIpAllocationPolicyArgs,
                 private_cluster_config: container.ClusterPrivateClusterConfigArgs,
                 workload_identity_config: container.ClusterWorkloadIdentityConfigArgs,
                 location="US-CENTRAL1",
                 initial_node_count=1,
                 remove_default_node_pool=True,
                 logging_service=None,
                 monitoring_service=None,
                 networking_mode="VPC_NATIVE",
                 ):
        self.name = name
        self.network = network
        self.subnetwork = subnetwork
        self.addons_config = addons_config
        self.release_channel = release_channel
        self.ip_allocation_policy = ip_allocation_policy
        self.private_cluster_config = private_cluster_config
        self.workload_identity_config = workload_identity_config
        self.location = location
        self.initial_node_count = initial_node_count
        self.remove_default_node_pool = remove_default_node_pool
        self.logging_service = logging_service
        self.monitoring_service = monitoring_service
        self.networking_mode = networking_mode

# https://www.pulumi.com/registry/packages/gcp/api-docs/container/cluster/
class KubernetesCluster(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: KubernetesClusterArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.cluster = container.Cluster(
            resource_name=name,
            network=args.network.id,
            subnetwork=args.subnetwork.id,
            addons_config=args.addons_config,
            release_channel=args.release_channel,
            ip_allocation_policy=args.ip_allocation_policy,
            private_cluster_config=args.private_cluster_config,
            workload_identity_config=args.workload_identity_config,
            location="US-CENTRAL1",
            initial_node_count=1,
            remove_default_node_pool=True,
            logging_service=None,
            monitoring_service=None,
            networking_mode="VPC_NATIVE",
            opts=ResourceOptions(parent=self))
        
        self.register_outputs({})