"""Split the faucet output into ten independently spendable P2PKH outputs."""
import runtime_setup
import argparse
from decimal import Decimal
from bitcoin.core.script import *
from utils import *


def split_coins(amount_to_send, txid_to_spend, utxo_index, n, should_broadcast=False):
    from config import my_private_key, my_public_key, my_address
    if not isinstance(n, int) or n < 3:
        raise ValueError('分币份数必须为至少 3 的整数。')
    input_value = validate_input(txid_to_spend, utxo_index, my_address)
    txin_scriptPubKey = my_address.to_scriptPubKey()
    txin = create_txin(txid_to_spend, utxo_index)
    each_amount = Decimal(str(amount_to_send)) / n
    tx = CMutableTransaction([txin], [create_txout(each_amount, txin_scriptPubKey)
                                     for _ in range(n)])
    sighash = SignatureHash(txin_scriptPubKey, tx, 0, SIGHASH_ALL)
    txin.scriptSig = CScript([my_private_key.sign(sighash) + bytes([SIGHASH_ALL]),
                              my_public_key])
    VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))
    return finish_transaction(tx, input_value, 'split', should_broadcast)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--broadcast', action='store_true', help='实际广播交易')
    args = parser.parse_args()
    from config import my_address
    amount_to_send = Decimal('0.00149')  # Total outputs, not the fee.
    txid_to_spend = '0d9b2e7b232bc18f54d3c86a77cf1900c3cf544f83c0610b083fc69490345560'
    utxo_index = 1  # Your address is the second faucet output.
    n = 10
    print('My address:', my_address)
    print('Spending:', txid_to_spend, 'vout=', utxo_index)
    split_coins(amount_to_send, txid_to_spend, utxo_index, n, args.broadcast)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, requests.RequestException) as error:
        print('ERROR:', error)
        raise SystemExit(1)
