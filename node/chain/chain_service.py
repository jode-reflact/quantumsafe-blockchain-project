import time
import os
import requests
from node.block.block_model import Block
from node.chain.chain_model import Chain
from node.database import db
from node.node.node_service import NodeService
from node.transaction.pending_transaction_model import PendingTransaction

TEST_CONFIG = {
    "CIPHER": os.environ['CIPHER'],
    "TEST_ID": os.environ['TEST_ID'],
    "TEST_TRANSACTION_COUNT": int(os.environ['TEST_TRANSACTION_COUNT']),
    "TEST_DATE": os.environ['TEST_DATE'],
    "TEST_NODE_COUNT": int(os.environ['TEST_NODE_COUNT']),
    "TEST_CLIENT_COUNT": int(os.environ['TEST_CLIENT_COUNT']),
    "HOST": os.environ['HOST'],
    }

TEST_COMPLETED = False

class ChainService:
    @staticmethod
    def set_initial_chain():
        genesis_block = Block(index=0,
                    timestamp=str(time.time()),
                    previous_hash="",
                    nonce=0,
                    transactions=[],
                    )
        initialChain = Chain([genesis_block])
        db.session.add(initialChain)
        db.session.commit()
    @staticmethod
    def get_chain() -> Chain:
        return db.session.query(Chain).first()

    @staticmethod
    def resolve_conflicts(other_chain):
        own_chain = ChainService.get_chain()

        # save computational cost and create instance after this check
        if own_chain is not None and len(own_chain.blocks) >= len(other_chain["blocks"]):
            return

        # create instances of class Chain
        other_chain = Chain.from_json(other_chain)

        try:
            other_chain.validate()
        except Exception:
            print("Other Chain is not valid")
            return

        # replace chain
        if own_chain is not None:
            db.session.delete(own_chain)
            db.session.query(Block).delete() #for testing
        db.session.add(other_chain)
        ChainService.__remove_confirmed_transactions_from_pending_transactions(new_chain=other_chain)
        db.session.commit()
        ChainService.check_test_completion()

    @staticmethod
    def __remove_confirmed_transactions_from_pending_transactions(new_chain):
        confirmed_transactions = set()
        for block in new_chain.blocks:
            confirmed_transactions.update(block.transactions)

        # remove confirmed tx from pending tx
        confirmed_transactions_timestamps = set(
            map(lambda t: t.timestamp, confirmed_transactions)
        )
        db.session\
            .query(PendingTransaction)\
            .filter(PendingTransaction.timestamp.in_(confirmed_transactions_timestamps))\
            .delete(synchronize_session=False)

    @staticmethod
    def distribute_chain():
        nodes = NodeService.nodes.copy()
        chain: Chain = ChainService.get_chain()
        for node in nodes:
            requests.post(f"http://{node}/chain",
                          json={"chain": chain.to_dict()},
                          headers={"Access-Control-Allow-Origin": "*"}
                          )
    
    @staticmethod
    def check_test_completion():
        print("check_test_completion")
        global TEST_COMPLETED
        global TEST_CONFIG
        if not TEST_COMPLETED:
            chain: Chain = ChainService.get_chain()
            print("TRANSACTION COUNT", chain.transaction_count)
            print("TEST TRANSACTION COUNT", TEST_CONFIG["TEST_TRANSACTION_COUNT"])
            if chain.transaction_count >= TEST_CONFIG["TEST_TRANSACTION_COUNT"]:
                TEST_CONFIG["CHAIN"] = chain.to_dict()
                requests.post(f"http://{TEST_CONFIG['HOST']}/completed_test",
                    json=TEST_CONFIG,
                    headers={"Access-Control-Allow-Origin": "*"}
                )
                TEST_COMPLETED = True