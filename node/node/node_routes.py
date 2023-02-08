from flask.blueprints import Blueprint
from flask import request, jsonify

from node.node.node_service import NodeService


nodes = Blueprint("nodes", __name__)


@nodes.route('/', methods=["GET"])
def get_nodes():
    nodes = list(NodeService.nodes)
    response = {"nodes": nodes}

    return jsonify(response), 200


@nodes.route('/', methods=["POST"])
def add_nodes():
    node = request.get_json().get("node")
    if node is not None:
        NodeService.add_node(node)
        return '', 204

    nodes = request.get_json().get("nodes")
    if nodes is not None:
        NodeService.add_nodes(nodes)
        return '', 204

    response = {"message": "You must set either 'node' or 'nodes'."}
    return jsonify(response), 400


