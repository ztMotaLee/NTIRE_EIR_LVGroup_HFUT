# NTIRE Challenge 2023 Team LVGroup_HFUT

> This repository is the official [NTIRE Challenge 2023](https://cvlai.net/ntire/2023/#) implementation of Team LVGroup_HFUT in [Image Super-Resolution (x4) Challenge](https://codalab.lisn.upsaclay.fr/competitions/10251).
> The restoration results of the tesing images can be downloaded from [here](https://pan.baidu.com/s/1p7SofDAIdL6VcpuEHOsiig?pwd=r8lp).
Our pretrained models can be downloaded from [here](https://pan.baidu.com/s/19JgYIaNSaF-b7mweqlb9rg?pwd=p5u8).
## Usage
### Train
```
./train.sh
```
Attention that you should change the path of datasets.
### Test
```
python main_test_swinir.py --task classical_sr --scale 4 --training_patch_size 48 --model_path your path --folder_lq your low-resolution image path --folder_gt your high-resolution image path
```
