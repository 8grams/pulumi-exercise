from typing import Sequence
from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import serviceaccount
import pulumi_gcp.projects as gcp_projects
from components.variables import project_id

class ServiceAccountArgs:
    def __init__(self,
                 name: str,
                 account_id: str,
                 project_id: str
                ):
        self.name = name
        self.account_id = account_id
        self.project_id = project_id

class IamMemberArgs:
    def __init__(self,
                 role: str,
                 serviceaccount: serviceaccount.Account) -> None:
        self.role = role
        self.serviceaccount = serviceaccount

class IamBindingArgs:
    def __init__(self,
                 serviceaccount: serviceaccount.Account,
                 role: str,
                 members: Sequence[str],
                 ):
        self.serviceaccount = serviceaccount
        self.role = role
        self.members = members

class ServiceAccountKeyArgs:
    def __init__(self,
                 service_account_id: str,
                 public_key_type: str,
                ):
        self.service_account_id = service_account_id
        self.public_key_type = public_key_type

# https://www.pulumi.com/registry/packages/gcp/api-docs/projects/iambinding/
class IamBinding(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: IamBindingArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.iam_binding = gcp_projects.IAMBinding(
            resource_name=name,
            project=project_id,
            role=args.role,
            members=args.members
        )

        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/projects/iammember/
class IamMember(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: IamMemberArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.iam_member = gcp_projects.IAMMember(
            resource_name=name,
            project=project_id,
            role=args.role,
            member=args.serviceaccount.email.apply(lambda email: "serviceAccount:" + email)
        )

        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/serviceaccount/account/
class ServiceAccount(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: ServiceAccountArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.service_account = serviceaccount.Account(
            resource_name=args.name,
            account_id=args.account_id,
            display_name=args.name,
            project=args.project_id
        )

        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/serviceaccount/key/
class ServiceAccountKey(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: ServiceAccountKeyArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.service_account_key = serviceaccount.Key(
            service_account_id=args.service_account_id,
            public_key_type=args.public_key_type,
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({})