from flask.blueprints import Blueprint
from flask import request, jsonify

from node.node.node_service import NodeService


nodes = Blueprint("nodes", __name__)

nodeService = NodeService()


@nodes.route('/', methods=["GET"])
def get_nodes():
    nodes = list(nodeService.nodes)
    response = {"nodes": nodes}

    return jsonify(response), 200


@nodes.route('/', methods=["POST"])
def add_nodes():
    node = request.get_json()["node"]
    nodeService.add_node(node)

    return '', 204

