from urllib.parse import urlparse


class NodeService:
    nodes = set()

    @staticmethod
    def add_nodes(nodes):
        """
        Adds new nodes to the set of nodes
        :param nodes: <List[str]> addresses of the nods
        :return: None
        """
        for node in nodes:
            NodeService.add_node(node)

    @staticmethod
    def add_node(node_address):
        """
        Add a new node to the set of nodes
        :param node_address: <str> Address of node, e.g. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(node_address)
        if parsed_url.netloc:
            NodeService.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts a URL without scheme like '192.168.0.5:5000'.
            NodeService.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")
