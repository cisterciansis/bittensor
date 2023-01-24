#!/bin/bash
export TOKENIZERS_PARALLELISM=true
export NCCL_P2P_DISABLE=1
~/.local/bin/deepspeed --include localhost:3,5 ./bittensor/_neuron/text/core_server/main.py --deepspeed_config ./bittensor/_neuron/text/core_server/ds_config.json --wallet.name default3 --logging.debug True --neuron.model_name EleutherAI/gpt-neo-2.7B --neuron.use_deepspeed
