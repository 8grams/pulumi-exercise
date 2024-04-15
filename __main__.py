"""A Google Cloud Python Pulumi program"""

from pulumi_gcp import compute, container, sql, storage
from components.variables import region, zone, project_id, db_username, db_password
from components.subnetwork import Subnetwork, SubnetworkArgs, IpRangeArgs
from components.router import Router, RouterArgs
from components.vpc import Vpc, VpcArgs, GlobalAddress, GlobalAddressArgs, ServiceNetworkingConnection, ServiceNetworkingConnectionArgs
from components.nat import RouterNat, RouterNatArgs, RouterNatIpAddress, RouterNatIpAddressArgs
from components.firewall import Firewall, FirewallArgs
from components.kubernetes import KubernetesCluster, KubernetesClusterArgs
from components.node_pool import NodePool, NodePoolArgs
from components.sa import ServiceAccount, ServiceAccountArgs, IamBinding, IamBindingArgs, IamMember, IamMemberArgs
from components.sql import DbInstance, DbInstanceArgs, Db, DbArgs, DbUser, DbUserArgs
from components.gcs import StorageBucket, StorageBucketArgs, StorageBucketAcl, StorageBucketAclArgs
from components.gar import ArtifactRegistry, ArtifactRegistryArgs
from components.disk import Disk, DiskArgs

# VPC
vpc = Vpc("main", VpcArgs(name="main"))

# Service Networking Connection
global_address = GlobalAddress(
    "onxp_vpc_peering", 
    "gcp:modules:vpc:onxp",
    GlobalAddressArgs(
        name="vpc-peering-ip-address",
        purpose="VPC_PEERING",
        address_type="INTERNAL",
        prefix_length=16, 
        network=vpc.vpc))

service_networking_connection = ServiceNetworkingConnection(
    "onxp-service-networking-connection", 
    "gcp:modules:vpc:vpcpeering:onxp", 
    ServiceNetworkingConnectionArgs(
        network=vpc.vpc, 
        reserved_peering_ranges=[global_address.global_address]))

# Subnetwork
subnetwork = Subnetwork(
    "onxp-subnet",
    "gcp:modules:subnetwork:onxp-",
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
    "gcp:modules:router:onxp",
    RouterArgs(
        name="onxp-router",
        network=vpc.vpc,
        region=region
    ))

# NAT
# create IP Address for NAT
nat_address = RouterNatIpAddress(
    "onxp-nat-ip", 
    "gcp:modules:nat:ipaddress:onxp",
    RouterNatIpAddressArgs(
        name="onxp-nat-ip",
        address_type="EXTERNAL",
        network_tier="PREMIUM"
    )
)

nat_subnetwork = compute.RouterNatSubnetworkArgs(
    name=subnetwork.subnetwork.name,
    source_ip_ranges_to_nats=["ALL_IP_RANGES"]
)

nat = RouterNat(
    "onxp-nat",
    "gcp:modules:nat:onxp",
    RouterNatArgs(
        name="onxp-nat",
        subnetworks=[nat_subnetwork],
        router=router.router,
        region=region,
        nat_ip_allocate_option="MANUAL_ONLY",
        source_subnetwork_ip_ranges_to_nat="LIST_OF_SUBNETWORKS",
        nat_ips=[nat_address.nat_ip_address.self_link]
    )
)

# Firewall
ssh_firewall = Firewall(
    "allow-ssh",
    "gcp:modules:firewall:ssh:onxp",
    FirewallArgs(
        name="allow-ssh",
        network=vpc.vpc,
        source_ranges=["0.0.0.0/0"],
        allows=[compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22"]
        )]
    )
)

http_firewall = Firewall(
    "allow-http",
    "gcp:modules:firewall:http:onxp",
    FirewallArgs(
        name="allow-http",
        network=vpc.vpc,
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
    "gcp:modules:kubernetes:cluster:onxp",
    KubernetesClusterArgs(
        name="onxp-cluster",
        network=vpc.vpc,
        subnetwork=subnetwork.subnetwork,
        addons_config=container.ClusterAddonsConfigArgs(
            horizontal_pod_autoscaling=container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(disabled=True),
            http_load_balancing=container.ClusterAddonsConfigHorizontalPodAutoscalingArgs(disabled=True)
        ),
        release_channel=container.ClusterReleaseChannelArgs(channel="REGULAR"),
        ip_allocation_policy=container.ClusterIpAllocationPolicyArgs(
            cluster_secondary_range_name=subnetwork.pod_ip_range.range_name,
            services_secondary_range_name=subnetwork.service_ip_range.range_name
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
    "gcp:modules:kubernetes:nodepool:sa:onxp",
    ServiceAccountArgs(
        name="onxp-nodepool-sa",
        account_id="onxp-nodepool-sa"
    )
)

# Create Nodepool
node_pool = NodePool(
    "onxp-nodepool",
    "gcp:modules:kubernetes:nodepool:onxp",
    NodePoolArgs(
        name="onxp-nodepool",
        cluster=kubernetes,
        node_config=container.ClusterNodeConfigArgs(
            preemptible=True,
            machine_type="e2-micro",
            disk_size_gb=80,
            disk_type="pd-balanced",
            service_account=node_pool_sa.service_account.email,
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

# Create CloudSQL
# DB instance
db_instance = DbInstance(
    "onxp-sql",
    "gcp:modules:sql:instance:onxp",
    DbInstanceArgs(
        name="onxp-sql",
        database_version="POSTGRES_15",
        region=region,
        settings=sql.DatabaseInstanceSettingsArgs(
            tier="db-f1-micro",
            availability_type="ZONAL",
            disk_autoresize=True,
            disk_size=10,
            disk_type="PD_SSD",
            deletion_protection_enabled=True,
            backup_configuration=sql.DatabaseInstanceSettingsBackupConfigurationArgs(
                enabled=True,
                location=region,
                transaction_log_retention_days=7,
                backup_retention_settings=sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                    retained_backups=7
                )
            ),
            ip_configuration=sql.DatabaseInstanceSettingsIpConfigurationArgs(
                ipv4_enabled=True,
                private_network=vpc.vpc.id
            ),
            insights_config=sql.DatabaseInstanceSettingsInsightsConfigArgs(
                query_insights_enabled=True
            )
        )
    )
)

# create database
db = Db(
    "onxp-production",
    "gcp:modules:sql:database:onxpprod",
    DbArgs(
        "onxp-production",
        instance=db_instance.database_instance.name
    )
)

# Create db user
db = DbUser(
    "onxp-db-user",
    "gcp:modules:sql:user:onxp",
    DbUserArgs(
        name=db_username,
        password=db_password,
        instance=db_instance.database_instance.name
    )
)

# Create service account, can be used in k8s cluster
db_sa = ServiceAccount(
    "onxp-db-sa",
    "gcp:modules:sql:sa:onxp",
    ServiceAccountArgs(
        name="onxp-db-sa",
        account_id="cloudsql-onxp"
    )
)

# add permission to service account
db_iam_member = IamMember(
    "onxp-db-iam-member",
    "gcp:modules:sql:sa:iam:onxp",
    IamMemberArgs(
        project_id=project_id,
        role="roles/cloudsql.admin",
        serviceaccount=db_sa.service_account
    )
)

# binding service account to workload identity
db_iam_binding = IamBinding(
    "onxp-db-iam-binding",
    "gcp:modules:sql:sa:iambinding:onxp",
    IamBindingArgs(
        serviceaccount=db_sa.service_account,
        role="roles/iam.workloadIdentityUser",
        members=["serviceAccount:" + project_id + ".svc.id.goog[exercise/onxp-exercise-sa]"]
    )
)

# Create GCS
# Create bucket
storage_bucket = StorageBucket(
    "onxp-bucket",
    "gcp:modules:storage:bucket:onxp",
    StorageBucketArgs(
        "onxp-bucket",
        location=region,
        storage_class="STANDARD",
        uniform_bucket_level_access=False,
        lifecycle_rules=[
            storage.BucketLifecycleRuleArgs(
                condition=storage.BucketLifecycleRuleConditionArgs(
                    days_since_noncurrent_time=7
                ),
                action=storage.BucketLifecycleRuleActionArgs(
                    type = "Delete"
                )
            ),
            storage.BucketLifecycleRuleArgs(
                condition=storage.BucketLifecycleRuleConditionArgs(
                    num_newer_versions=3,
                    with_state="ARCHIVED"
                ),
                action=storage.BucketLifecycleRuleActionArgs(
                    type = "Delete"
                )
            ),
        ],
        versioning=storage.BucketVersioningArgs(
            enabled=True
        )
    )
)

# Create service account with storage admin role
bucket_sa = ServiceAccount(
    "onxp-bucket-sa",
    "gcp:modules:storage:bucket:sa:onxp",
    ServiceAccountArgs(
        name="onxp-bucket-sa",
        account_id="onxp-bucket-sa"
    )
)

# add permission to service account
bucket_iam_member = IamMember(
    "onxp-bucket-iam-member",
    "gcp:modules:storage:bucket:sa:iam:onxp",
    IamMemberArgs(
        project_id=project_id,
        role="roles/storage.admin",
        serviceaccount=bucket_sa.service_account
    )
)

# create bucket acl
bucket_acl = StorageBucketAcl(
    "onxp-bucket-acl",
    "gcp:modules:storage:bucket:acl:onxp",
    StorageBucketAclArgs(
        storage_bucket.storage.name,
        role_entity=["OWNER:user-" + bucket_sa.service_account.email]
    )
)

# Create GAR
gar = ArtifactRegistry(
    "onxp-gar",
    "gcp:modules:artifactregistry:repository:onxp",
    ArtifactRegistryArgs(
        repository_id="onxp-gar",
        location=region,
        format="DOCKER"
    )
)

# create service account for gar
gar_sa = ServiceAccount(
    "onxp-gar-sa",
    "gcp:modules:artifactregistry:sa:onxp",
    ServiceAccountArgs(
        name="onxp-gar-sa",
        account_id="onxp-gar-sa"
    )
)

# add permission to service account
gar_iam_member = IamMember(
    "onxp-gar-iam-member",
    "gcp:modules:artifactregistry:sa:iam:onxp",
    IamMemberArgs(
        project_id=project_id,
        role="roles/artifactregistry.admin",
        serviceaccount=gar_sa.service_account
    )
)

# Create disk
disk = Disk(
    "onxp-disk",
    "gcp:modules:disk:onxp",
    DiskArgs(
        name="onxp-disk",
        zone=zone,
        size=10,
        physical_block_size_bytes=4096
    )
)