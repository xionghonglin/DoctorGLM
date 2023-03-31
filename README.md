<p align="center">
  <img src="imgs/logo.png" width=400px/>
  <br/>
  <img src="https://img.shields.io/badge/Version-0.0.1--alpha-brightgreen">
</p>


# DoctorGLM
中文问诊模型， 基于 ChatGLM-6B + lora 进行finetune

finetune代码来自 https://github.com/ssbuild/chatglm_finetuning
## 训练数据
https://github.com/Toyhom/Chinese-medical-dialogue-data
## 准备
- 显存 >= 13G
- pip install deep_training cpm_kernels icetk transformers>=4.26.1 
- torch >= 1.12.0 (icetk依赖cpu版torch, 建议先安装icetk后安装gpu版torch)
## 使用
Doctor_GLM/chat.ipynb

第一次运行会下载chatGLM-6B权重
## 对话示例

# TODO
- 降低显存使用
- 多轮对话
