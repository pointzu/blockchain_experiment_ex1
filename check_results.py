"""Print transaction status and screenshot links; does not require a private key."""
import requests
from transactions import faucet_txid, split_txid, ex1_txid

API = 'https://blockstream.info/testnet/api'


def main():
    for label, txid in [('领取 / faucet', faucet_txid),
                        ('分币 / split', split_txid), ('发币 / Ex1', ex1_txid)]:
        print('\n===', label, '===')
        if not txid:
            print('尚未记录成功广播的交易。')
            continue
        response = requests.get(API + '/tx/' + txid, timeout=30)
        response.raise_for_status()
        data = response.json()
        print('TXID:', txid)
        print('Status:', 'Confirmed' if data['status']['confirmed'] else 'Unconfirmed')
        if data['status']['confirmed']:
            print('Block height:', data['status']['block_height'])
        print('Fee:', data['fee'], 'sat')
        print('Inputs:')
        for item in data['vin']:
            print(' ', item['txid'], 'vout=', item['vout'])
        print('Outputs:')
        for index, output in enumerate(data['vout']):
            print(f"  [{index}] {output.get('scriptpubkey_address', '(no address)')}: {output['value']} sat")
        print('Screenshot URL: https://blockstream.info/testnet/tx/' + txid)
        print('Alternative: https://mempool.space/testnet/tx/' + txid)


if __name__ == '__main__':
    try:
        main()
    except (requests.RequestException, ValueError) as error:
        print('查询失败:', error)
        raise SystemExit(1)
