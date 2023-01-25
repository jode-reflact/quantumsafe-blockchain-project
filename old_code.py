aciclient = ContainerInstanceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["SUBSCRIPTION_ID"],
    )
resclient = ResourceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["SUBSCRIPTION_ID"],
    )

def create_container_group(aci_client, resource_group,
                           container_group_name, container_image_name):
    print("Creating container group '{0}'...".format(container_group_name))

    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)
    container = Container(name=container_group_name,
                          image=container_image_name,
                          
                          resources=container_resource_requirements,
                          ports=[ContainerPort(port=80)])

    # Configure the container group
    ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=80)]
    group_ip_address = IpAddress(ports=ports,
                                 dns_name_label=container_group_name,
                                 type="Public")
    image_registry_credentials = ImageRegistryCredential(
        server=os.environ['RG_SERVER'],
        username=os.environ['RG_USR'],
        password=os.environ['RG_PWD'],
    )
    group = ContainerGroup(location=resource_group.location,
                           containers=[container],
                           os_type=OperatingSystemTypes.linux,
                           ip_address=group_ip_address,
                           restart_policy="Never",
                           image_registry_credentials=image_registry_credentials
                           )

    # Create the container group
    aci_client.container_groups.begin_create_or_update(resource_group.name,
                                                 container_group_name,
                                                 group)

    # Get the created container group
    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)

    print("Once DNS has propagated, container group '{0}' will be reachable at"
          " http://{1}".format(container_group_name, container_group.ip_address.fqdn))

resource_group_name = 'quantumsafe_blockchain'
container_group_name = 'my-name'
container_image_app = "quantumsafeblockchain.azurecr.io/blockchain-server:v2"
resource_group = resclient.resource_groups.get(resource_group_name)
create_container_group(aciclient, resource_group, container_group_name,
                           container_image_app)
quit()