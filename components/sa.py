from typing import Sequence
from pulumi import ResourceOptions
from pulumi_gcp import serviceaccount
from variables import zone

class ServiceAccountArgs:
    def __init__(self,
                 name: str,
                 account_id: str,
                ):
        self.name = name
        self.account_id = account_id

class IamMemberArgs:
    def __init__(self,
                 project_id: str,
                 role: str,
                 serviceaccount: serviceaccount.Account) -> None:
        self.project_id = project_id
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

# https://www.pulumi.com/registry/packages/gcp/api-docs/serviceaccount/iambinding/
class IamBinding(ResourceOptions):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: IamBindingArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.iam_member = serviceaccount.IAMBinding(
            resource_name=args.name,
            service_account_id=args.serviceaccount.id,
            role=args.role,
            member=args.members
        )

        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/serviceaccount/iammember/
class IamMember(ResourceOptions):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: IamMemberArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.iam_member = serviceaccount.IAMMember(
            resource_name=args.name,
            role=args.role,
            member="serviceAccount:" + args.serviceaccount.email
        )

        self.register_outputs({})

# https://www.pulumi.com/registry/packages/gcp/api-docs/serviceaccount/account/
class ServiceAccount(ResourceOptions):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: ServiceAccountArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.service_account = serviceaccount.Account(
            resource_name=args.name,
            account_id=args.account_id,
        )

        self.register_outputs({})