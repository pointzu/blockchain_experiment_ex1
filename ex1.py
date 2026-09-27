"""Spend one split output using explicit P2PKH scripts."""
import runtime_setup
import argparse
from decimal import Decimal
from bitcoin.wallet import P2PKHBitcoinAddress
from bitcoin.core.script import *
from utils import *


def P2PKH_scriptPubKey(address):
    if not isinstance(address, P2PKHBitcoinAddress):
        raise ValueError('本实验的输出脚本仅支持 P2PKH 地址。')
    return [OP_DUP, OP_HASH160, bytes(address), OP_EQUALVERIFY, OP_CHECKSIG]


def P2PKH_scriptSig(txin, txout, txin_scriptPubKey):
    from config import my_private_key, my_public_key
    signature = create_OP_CHECKSIG_signature(
        txin, txout, txin_scriptPubKey, my_private_key)
    return [signature, my_public_key]


def send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index,
                                txout_scriptPubKey, should_broadcast=False):
    from config import my_address
    input_value = validate_input(txid_to_spend, utxo_index, my_address)
    txout = create_txout(amount_to_send, txout_scriptPubKey)
    txin_scriptPubKey = P2PKH_scriptPubKey(my_address)
    txin = create_txin(txid_to_spend, utxo_index)
    txin_scriptSig = P2PKH_scriptSig(txin, txout, txin_scriptPubKey)
    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey, txin_scriptSig)
    return finish_transaction(new_tx, input_value, 'ex1', should_broadcast)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--broadcast', action='store_true', help='实际广播交易')
    parser.add_argument('--txid', help='分币交易哈希，默认读取 transactions.py')
    args = parser.parse_args()
    from config import my_address, faucet_address
    from transactions import split_txid
    txid_to_spend = args.txid or split_txid
    if not txid_to_spend:
        raise ValueError('请先成功广播分币交易；也可用 --txid 指定实际分币哈希。')
    amount_to_send = Decimal('0.000139')
    utxo_index = 0  # Output 0 of the NEW split transaction.
    print('My address:', my_address)
    print('Recipient:', faucet_address)
    print('Spending:', txid_to_spend, 'vout=', utxo_index)
    send_from_P2PKH_transaction(amount_to_send, txid_to_spend, utxo_index,
                               P2PKH_scriptPubKey(faucet_address), args.broadcast)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, requests.RequestException) as error:
        print('ERROR:', error)
        raise SystemExit(1)
