import os
from pathlib import Path
_local_key_file = Path(__file__).resolve().with_name('private_key.local.txt')
import runtime_setup
from bitcoin import SelectParams
from bitcoin.base58 import decode
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress


SelectParams('testnet')

# TODO: Fill this in with your private key.
PRIVATE_KEY_WIF = os.environ.get('BITCOIN_TESTNET_PRIVATE_KEY', '').strip()
if not PRIVATE_KEY_WIF and _local_key_file.is_file():
    PRIVATE_KEY_WIF = _local_key_file.read_text(encoding='utf-8').strip()
if not PRIVATE_KEY_WIF or set(PRIVATE_KEY_WIF) == {'X'}:
    raise ValueError('请设置 BITCOIN_TESTNET_PRIVATE_KEY，或在本地 private_key.local.txt 中保存原私钥。')
try:
    my_private_key = CBitcoinSecret(PRIVATE_KEY_WIF.strip())
except Exception:
    raise ValueError('私钥格式不正确，请在本地检查完整的 testnet WIF 私钥。') from None
my_public_key = my_private_key.pub
my_address = P2PKHBitcoinAddress.from_pubkey(my_public_key)
if str(my_address) != 'mzT3NxNH1iGLvKiHDzJyN4NtLogEFLv3A2':
    raise ValueError('该私钥推导出的地址与领取地址不一致，请使用原来的私钥。')

faucet_address = CBitcoinAddress('mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB')
