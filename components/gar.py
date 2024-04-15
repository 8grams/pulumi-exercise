from pulumi import ResourceOptions
from pulumi_gcp import artifactregistry

class ArtifactRegistryArgs:
    def __init__(self,
                 repository_id: str,
                 location: str,
                 format):
        self.repository_id = repository_id
        self.location = location
        self.format = format

# https://www.pulumi.com/registry/packages/gcp/api-docs/artifactregistry/repository/
class ArtifactRegistry:
    def __init__(self, 
                 name: str, 
                 label: str,
                 args: ArtifactRegistryArgs, 
                 opts: ResourceOptions = None):
        super().__init__(label, name, {}, opts)

        self.artifact_registry = artifactregistry.Repository(
            resource_name=name,
            location=args.location,
            repository_id=args.repository_id,
            format=args.format,
            opts=ResourceOptions(parent=self))
        self.register_outputs({})