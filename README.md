<p align="center">
  <img src="imgs/logo.png" width=400px/>
  <br/>
  <img src="https://img.shields.io/badge/Version-0.0.2--alpha-brightgreen">
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

## 使用
- 显存 >= 13G
- pip install deep_training cpm_kernels icetk transformers>=4.26.1 
- torch >= 1.12.0 (icetk依赖cpu版torch, 建议先安装icetk后安装gpu版torch)
- finetune代码来自 https://github.com/ssbuild/chatglm_finetuning

对于fp16模型，直接使用Doctor_GLM/chat.ipynb，由于官方更新了chatglm的权重，我们将老权重放在了  
链接：https://pan.baidu.com/s/1vuoBbOQVPJPAcurEfVRn7A?pwd=ahwc   
提取码：ahwc   
可以下载后解压到old_pretrain_model目录

量化的模型我们打了个包，使用方便，但是效果目前来看很成问题：INT4需要大约6G显存，INT8需要大约8G显存
``` python
from load_quantization import load_int
tokenizer, model = load_int('DoctorGLM-6B-INT8-6merge-int8.pt',8)
response, history = model.chat(tokenizer,
                               "我爷爷高血压可以喝咖啡吗",
                               history=[],
                               max_length=2048)
print(response)
```
模型下载链接：
[INT4](https://pan.baidu.com/s/1nHQ1EQ2OBuWCyBZKBnBHYw?pwd=x6l4) [INT8](https://pan.baidu.com/s/1v2hWl1dPnh8xoJzxtpbugw?pwd=y4hu)
量化方法均为分层的线性量化。
目前量化模型的性能**仍有较大问题**，后期我们会对量化方法和模型进行更新

## 模型在线部署

为了方便部署并随时调整模型生成回答时的参数，我们提供了基于 `Gradio` 库的部署代码，路径为 `Doctor_GLM/gradio.ipynb`。运行之后，访问本机的7860或者代码声明的其他端口即可以运行Demo，模型在生成回答时的参数可以由用户自由调控。若想让部署的模型可以被局域网之外的其他用户访问，需要将sharing设置为 `True`（默认为`False`）。部署之后运行效果如下所示：

<p align="center">
  <img src="imgs/gradio_demo.gif" width=1300px/>
  <br/>
</p>

## 最近更新
- <img src="https://img.shields.io/badge/Version-0.0.1--alpha-brightgreen"> (2023.4.3) 初版的权重，来自LoRA SFT 1 epcoh
- <img src="https://img.shields.io/badge/Version-0.0.2--alpha-brightgreen"> (2023.4.13) LoRA-INT4/8量化权重，以及我们实验发现LoRA一直会丢失对话能力，放弃该方式，转向P-Tuning

## 即将到来的更新 
- [ ] <img src="https://img.shields.io/badge/Version-0.0.3--alpha-brightgreen"> (2023.4.17) P-Tuning 多轮对话数据集训练的新权重和arxiv，预实验表明对话能力相比LoRA模型提升很多
- [ ] <img src="https://img.shields.io/badge/Version-0.0.4--alpha-brightgreen"> 对话中加入参考文献
- [ ] Huggingface

第一次运行会下载chatGLM-6B权重, 如果已有chatGLM-6B权重可以将data_utils.py里的路径修改为自己的权重目录
## 结果示例
<p align="center">
  <img src="imgs/3_ret.png" width=1300px/>
  <br/>
</p>
我们随机跑了100个结果，在 ./results目录下，两份json文件分别为由ChatGLM, DoctorGLM得到的结果，目前存在大量复读机。

## 开发者群

<p align="left">
  <img src="imgs/group_qrcode.png" width=200px/>
</p>
DoctorGLM开发者群，如果你也对基于ChatGLM的应用开发感兴趣，欢迎加入我们的讨论组。

## 引用
```
@article{xiong2023doctorglm,
      title={DoctorGLM: Fine-tuning your Chinese Doctor is not a Herculean Task}, 
      author={Honglin Xiong and Sheng Wang and Yitao Zhu and Zihao Zhao and Yuxiao Liu and Qian Wang and Dinggang Shen},
}
```

