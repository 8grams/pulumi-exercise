from typing import Sequence
from pulumi import ResourceOptions
from pulumi_gcp import container, serviceaccount

class NodePoolArgs:
    def __init__(self,
                 name,
                 cluster: container.Cluster,
                 node_config: container.ClusterNodeConfigArgs,
                 node_count=1,
                 node_locations: Sequence[str]=["US-CENTRAL1-A"],
                 autoscaling=container.NodePoolAutoscalingArgs,
                 management=container.NodePoolManagementArgs,
                ):
        self.name = name
        self.cluster = cluster
        self.node_config = node_config
        self.node_count = node_count
        self.node_locations = node_locations
        self.autoscaling = autoscaling
        self.management = management

# https://www.pulumi.com/registry/packages/gcp/api-docs/container/nodepool/
class NodePool(ResourceOptions):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: NodePoolArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.node_pool = container.NodePool(
            resource_name=args.name,
            cluster=args.cluster.id,
            node_config=args.node_config,
            node_count=args.node_count,
            node_locations=args.node_locations,
            autoscaling=args.autoscaling,
            management=args.management,
        )

        self.register_outputs({})