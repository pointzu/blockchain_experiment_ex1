import runtime_setup
from decimal import Decimal
from pathlib import Path
import re
import requests

from bitcoin.core import b2x, b2lx, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import *
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH


def send_from_custom_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        txin_scriptPubKey, txin_scriptSig, txout_scriptPubKey):
    txout = create_txout(amount_to_send, txout_scriptPubKey)
    txin = create_txin(txid_to_spend, utxo_index)
    new_tx = create_signed_transaction(txin, txout, txin_scriptPubKey,
                                       txin_scriptSig)
    return broadcast_transaction(new_tx)


def create_txin(txid, utxo_index):
    return CMutableTxIn(COutPoint(lx(txid), utxo_index))


def create_txout(amount, scriptPubKey):
    satoshis = Decimal(str(amount)) * COIN
    if not satoshis.is_finite() or satoshis != satoshis.to_integral_value():
        raise ValueError('输出金额必须为整数 satoshi。')
    if not 0 < satoshis <= 21_000_000 * COIN:
        raise ValueError('输出金额超出有效范围。')
    return CMutableTxOut(int(satoshis), CScript(scriptPubKey))


def create_OP_CHECKSIG_signature(txin, txout, txin_scriptPubKey, seckey):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx,
                            0, SIGHASH_ALL)
    sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
    return sig


def create_signed_transaction(txin, txout, txin_scriptPubKey,
                              txin_scriptSig):
    tx = CMutableTransaction([txin], [txout])
    txin.scriptSig = CScript(txin_scriptSig)
    VerifyScript(txin.scriptSig, CScript(txin_scriptPubKey),
                 tx, 0, (SCRIPT_VERIFY_P2SH,))
    return tx


def broadcast_transaction(tx):
    raw_transaction = b2x(tx.serialize())
    return requests.post(
        'https://blockstream.info/testnet/api/tx',
        headers={'Content-Type': 'text/plain'},
        data=raw_transaction, timeout=30)


API = 'https://blockstream.info/testnet/api'
ROOT = Path(__file__).resolve().parent


def get_json(path):
    response = requests.get(API + path, timeout=30)
    if not response.ok:
        raise ValueError(f'链上查询失败 HTTP {response.status_code}: {response.text[:300]}')
    return response.json()


def validate_input(txid, index, address):
    if not isinstance(txid, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', txid):
        raise ValueError('交易哈希必须为 64 位十六进制字符串。')
    data = get_json('/tx/' + txid)
    if not data['status']['confirmed']:
        raise ValueError('请等输入所在的上一笔交易确认后再运行。')
    if not isinstance(index, int) or not 0 <= index < len(data['vout']):
        raise ValueError('输出编号无效。')
    output = data['vout'][index]
    if output['scriptpubkey'] != address.to_scriptPubKey().hex():
        raise ValueError('该输出不属于 config.py 中的地址。')
    if get_json(f'/tx/{txid}/outspend/{index}')['spent']:
        raise ValueError('这个输出已花费，请检查交易记录，不要重复运行。')
    return output['value']


def save_txid(kind, txid):
    import ast
    path = ROOT / 'transactions.py'
    values = {'faucet_txid': '0d9b2e7b232bc18f54d3c86a77cf1900c3cf544f83c0610b083fc69490345560',
              'split_txid': None, 'ex1_txid': None}
    if path.exists():
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in values:
                    values[target.id] = ast.literal_eval(node.value)
    values[kind + '_txid'] = txid
    temp = path.with_suffix('.tmp')
    temp.write_text('# 实际广播成功的交易哈希；链上确认另行检查。\n' +
                    ''.join(f'{key} = {value!r}\n' for key, value in values.items()), encoding='utf-8')
    temp.replace(path)


def finish_transaction(tx, input_value, kind, should_broadcast):
    output_total = sum(output.nValue for output in tx.vout)
    fee = input_value - output_total
    size = len(tx.serialize())
    if fee <= 0:
        raise ValueError('输出总额必须小于输入金额，留出手续费。')
    print('Network: Bitcoin testnet3')
    print(f'Input: {input_value} sat')
    print(f'Outputs: {len(tx.vout)}; total: {output_total} sat')
    for index, output in enumerate(tx.vout):
        print(f'  output[{index}]: {output.nValue} sat')
    print(f'Fee: {fee} sat; size: {size} bytes; fee rate: {fee / size:.2f} sat/vB')
    txid = b2lx(tx.GetTxid())
    print('Local txid:', txid)
    print('VerifyScript: PASS')
    if not should_broadcast:
        print('PREVIEW ONLY: no transaction broadcast. Add --broadcast to submit.')
        return None
    try:
        response = broadcast_transaction(tx)
    except requests.RequestException:
        print('请求异常，广播状态不确定。先用上面的 Local txid 或地址查询，勿盲目重跑。')
        raise
    print('HTTP:', response.status_code, response.reason)
    print(response.text)
    if not response.ok:
        raise ValueError('广播未成功，请先检查响应及链上状态。')
    if response.text.strip() != txid:
        raise ValueError('响应哈希与本地交易不一致，请查链上状态后再继续。')
    save_txid(kind, txid)
    print('Saved:', str(ROOT / 'transactions.py'))
    print('Explorer: https://blockstream.info/testnet/tx/' + txid)
    print('Broadcast accepted. Wait for Confirmed before taking the final explorer screenshot.')
    return response
