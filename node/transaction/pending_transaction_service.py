import requests
from sqlalchemy import exc

from node.database import db
from node.node.node_service import NodeService
from node.transaction.transaction_model import PendingTransaction


class TransactionService:
    @staticmethod
    def get_pending_transactions():
        return db.session.query(PendingTransaction).all()

    @staticmethod
    def add_transaction(sender, receiver, amount, timestamp, signature):
        transaction = PendingTransaction(timestamp=timestamp,
                                         sender=sender,
                                         receiver=receiver,
                                         amount=amount,
                                         signature=signature
                                         )
        transaction.verify()

        # insert transaction in db
        try:
            db.session.add(transaction)
            db.session.commit()

            # only distribute transaction if transaction is unknown yet
            TransactionService.__distribute_transaction(transaction)
        except exc.IntegrityError:
            # transaction already known
            db.session.rollback()

    @staticmethod
    def __distribute_transaction(transaction):
        nodes = NodeService.nodes.copy()
        for node in nodes:
            requests.post(f"http://{node}/transactions",
                          json=transaction.to_dict(),
                          headers={"Access-Control-Allow-Origin": "*"}
                          )