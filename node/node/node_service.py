from urllib.parse import urlparse


class NodeService:
    def __init__(self):
        self.nodes = set()

    def add_nodes(self, nodes):
        # TODO: Implement if needed
        raise NotImplementedError()

    def add_node(self, node_address):
        """
        Add a new node to the set of nodes
        :param node_address: <str> Address of node, e.g. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(node_address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts a URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")
