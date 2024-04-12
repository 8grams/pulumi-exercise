from pulumi import ResourceOptions
from pulumi_gcp import compute
from variables import zone

class DiskArgs:
    def __init__(self,
                 name,
                 zone=zone,
                 size: int=10,
                 physical_block_size_bytes: int=4096,
                 ):
        self.name = name
        self.zone = zone
        self.size = size
        self.physical_block_size_bytes = physical_block_size_bytes

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/disk/
class Disk:
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: DiskArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.disk = compute.Disk(
            resource_name=name,
            zone=args.zone,
            size=args.size,
            physical_block_size_bytes=args.physical_block_size_bytes,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})
    