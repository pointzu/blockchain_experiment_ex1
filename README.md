# 区块链基础及应用 · Ex1

邹俊轩，学号 2412592。使用 Bitcoin testnet3 完成十输出分币和 P2PKH 发币实验。

- [实验报告 PDF](报告/main.pdf)
- [LaTeX 源码](报告/main.tex)，截图位于 `报告/assets/`
- `split_output.txt`、`ex1_output.txt`：实际广播输出
- `transactions.py`、`chain_status.txt`：真实交易哈希与确认结果

## 实验结果

分币交易已确认于区块 5151331：输入 150524 sat，输出十份各 14900 sat，手续费 1524 sat。

Ex1 发币交易已确认于区块 5151332：花费分币的 0 号输出，向课程地址发送 13900 sat，手续费 1000 sat。

## 环境与配置

使用 Python 3 和 `python -m pip install -r requirements.txt` 安装依赖。Windows 下 `runtime_setup.py` 优先使用本地预备实验目录的 DLL；若该目录不存在，则使用仓库 `助教提示/` 中的同位数 DLL。

私钥不包含在公开仓库中。仅在本机设置环境变量 `BITCOIN_TESTNET_PRIVATE_KEY`，或在 `config.py` 同目录的 `private_key.local.txt` 中保存本人原测试网私钥。该文件被 Git 忽略，已有本地配置已迁移至此。脚本会核对领取地址，不要用其他人的私钥。

默认运行仅预览；显式 `--broadcast` 才提交交易。本仓库的领取输出和 Ex1 使用的分币输出已经花费，不能重复广播历史实验。`python check_results.py` 可进行只读查询。

## 编译报告

在 `报告/` 中使用 XeLaTeX（TeX Live、Windows 中文字体）编译 `main.tex` 两次。公开报告包含项目链接、关键代码、真实截图及金额分析，不包含私钥截图或编译缓存。
