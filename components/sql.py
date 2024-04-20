from pulumi import ComponentResource, ResourceOptions
from pulumi_gcp import sql
from components.variables import region

class DbInstanceArgs:
    def __init__(self,
                 name: str,
                 database_version,
                 settings: sql.DatabaseInstanceSettingsArgs,
                 region=region,
                 depends_on=None
                 ) -> None:
        self.name = name
        self.region = region
        self.database_version = database_version
        self.settings = settings
        self.depends_on = depends_on

# DB instance
# https://www.pulumi.com/registry/packages/gcp/api-docs/sql/databaseinstance/
class DbInstance(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: DbInstanceArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.database_instance = sql.DatabaseInstance(
            resource_name=name,
            region=args.region,
            database_version=args.database_version,
            settings=args.settings,
            deletion_protection=args.settings.deletion_protection_enabled,
            opts=ResourceOptions(parent=self, depends_on=args.depends_on))
        self.register_outputs({})

class DbArgs:
    def __init__(self,
                 name: str,
                 instance: sql.DatabaseInstance
                 ) -> None:
        self.name = name
        self.instance = instance

# Database
# https://www.pulumi.com/registry/packages/gcp/api-docs/sql/database/
class Db(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: DbArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.database = sql.Database(
            resource_name=name,
            name=args.name,
            instance=args.instance,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})

# Database User
# https://www.pulumi.com/registry/packages/gcp/api-docs/sql/user/
class DbUserArgs:
    def __init__(self,
                 name: str,
                 password,
                 instance: sql.DatabaseInstance
                 ) -> None:
        self.name = name
        self.password = password
        self.instance = instance

class DbUser(ComponentResource):
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: DbUserArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.database = sql.User(
            resource_name=name,
            name=args.name,
            password=args.password,
            instance=args.instance,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})
