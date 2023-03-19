from flask import jsonify
from sqlalchemy import exc

from node.block.block_model import Block
from node.database import db


class BlockService:
    @staticmethod
    def get_blocks():
        return db.session.query(Block).all()
