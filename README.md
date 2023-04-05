<p align="center">
  <img src="imgs/logo.png" width=400px/>
  <br/>
  <img src="https://img.shields.io/badge/Version-0.0.1--alpha-brightgreen">
  <br/>
  <a href="https://xionghonglin.github.io/DoctorGLM/">[Project Page]</a>
</p>




# DoctorGLM
基于 ChatGLM-6B的中文问诊模型
## 训练数据
| Dataset    | Department                | Language | Q&A  | Chat | Number | Syn. | Size  | Weight |
|------------|--------------------------|----------|------|------|--------|------|-------|-------|
| CMD.       | Surgical                 | CN       | ✔    | ×    | 116K   | ×    | 52MB  |       |
|            | Obstetrics and Gynecology| CN       | ✔    | ×    | 229K   | ×    | 78MB  |       |
|            | Pediatrics               | CN       | ✔    | ×    | 117K   | ×    | 47MB  |       |
|            | Internal Medicine        | CN       | ✔    | ×    | 307K   | ×    | 102MB |       |
|            | Andriatria               | CN       | ✔    | ×    | 113K   | ×    | 44MB  |       |
|            | Merged                   | CN       | ✔    | ×    | 1.9M   | ×    |       |Doctor_GLM/ckpt|
| MedDialog  | Multiple                 | CN&EN    | ✔    | ✔    | 3.4M   | ×    | 1.5GB |Coming soon    |
| ChatDoctor | Multiple                 | EN       | ✔    | ×    | 5.4K   | ✔    | 2.9MB |Coming soon    |
| HearlthcareMagic| Multiple            | EN       | ✔    | ×    | 200K   | ×    | 216MB |Coming soon    |



https://github.com/Toyhom/Chinese-medical-dialogue-data
## 准备
- 显存 >= 13G
- pip install deep_training cpm_kernels icetk transformers>=4.26.1 
- torch >= 1.12.0 (icetk依赖cpu版torch, 建议先安装icetk后安装gpu版torch)
- finetune代码来自 https://github.com/ssbuild/chatglm_finetuning
## 使用
直接使用Doctor_GLM/chat.ipynb

## 即将到来的更新 <img src="https://img.shields.io/badge/Version-0.0.2--alpha-brightgreen">
- training iter影响的对比实验，选一个更好的fp16模型
- INT8，INT4的模型（已经有INT4模型，性能下降非常严重，将尝试INT8）

## 即将到来的更新 <img src="https://img.shields.io/badge/Version-0.0.3--alpha-brightgreen">
- LoRA weight的影响的对比实验
- 多轮对话数据集训练的新模型

第一次运行会下载chatGLM-6B权重, 如果已有chatGLM-6B权重可以将data_utils.py里的路径修改为自己的权重目录
## 结果示例
<p align="center">
  <img src="imgs/3_ret.png" width=1300px/>
  <br/>
</p>
我们随机跑了100个结果，在 ./results目录下，两份json文件分别为由ChatGLM, DoctorGLM得到的结果，目前存在大量复读机。

## 引用
```
@article{xiong2023doctorglm,
      title={DoctorGLM: Fine-tuning your Chinese Doctor is not a Herculean Task}, 
      author={Honglin Xiong and Sheng Wang and Yitao Zhu and Zihao Zhao and Yuxiao Liu and Qian Wang and Dinggang Shen},
}
```

