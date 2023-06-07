QLoRA: Efficient Finetuning of Quantized LLMs
QLoRA：量化 LLM 的高效微调

| Paper | Adapter Weights | Demo |
|纸张 |适配器重量 |演示 |

This repo supports the paper "QLoRA: Efficient Finetuning of Quantized LLMs", an effort to democratize access to LLM research.
此 repo 支持论文“QLoRA：量化 LLM 的高效微调”，旨在使对 LLM 研究的访问民主化。

QLoRA uses bitsandbytes for quantization and is integrated with Hugging Face's PEFT and transformers libraries. QLoRA was developed by members of the University of Washington's UW NLP group.
QLoRA 使用 bitsandbytes 进行量化，并与 Hugging Face 的 PEFT 和 transformers 库集成。 QLoRA 由华盛顿大学 UW NLP 小组的成员开发。
Overview 概述

We present QLoRA, an efficient finetuning approach that reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance. QLoRA backpropagates gradients through a frozen, 4-bit quantized pretrained language model into Low Rank Adapters (LoRA). Our best model family, which we name Guanaco, outperforms all previous openly released models on the Vicuna benchmark, reaching 99.3% of the performance level of ChatGPT while only requiring 24 hours of finetuning on a single GPU. QLoRA introduces a number of innovations to save memory without sacrificing performance: (a) 4-bit NormalFloat (NF4), a new data type that is information theoretically optimal for normally distributed weights (b) Double Quantization to reduce the average memory footprint by quantizing the quantization constants, and (c) Paged Optimizers to manage memory spikes. We use QLoRA to finetune more than 1,000 models, providing a detailed analysis of instruction following and chatbot performance across 8 instruction datasets, multiple model types (LLaMA, T5), and model scales that would be infeasible to run with regular finetuning (e.g. 33B and 65B parameter models). Our results show that QLoRA finetuning on a small high-quality dataset leads to state-of-the-art results, even when using smaller models than the previous SoTA. We provide a detailed analysis of chatbot performance based on both human and GPT-4 evaluations showing that GPT-4 evaluations are a cheap and reasonable alternative to human evaluation. Furthermore, we find that current chatbot benchmarks are not trustworthy to accurately evaluate the performance levels of chatbots. We release all of our models and code, including CUDA kernels for 4-bit training.
我们介绍了 QLoRA，这是一种有效的微调方法，可以减少内存使用量，足以在单个 48GB GPU 上微调 65B 参数模型，同时保留完整的 16 位微调任务性能。 QLoRA 通过冻结的 4 位量化预训练语言模型将梯度反向传播到低阶适配器 (LoRA)。我们最好的模型系列，我们命名为 Guanaco，在 Vicuna 基准测试中优于所有以前公开发布的模型，达到 ChatGPT 性能水平的 99.3%，同时只需要在单个 GPU 上进行 24 小时的微调。 QLoRA 引入了许多创新来节省内存而不牺牲性能：(a) 4 位 NormalFloat (NF4)，一种新的数据类型，理论上是正态分布权重的最佳信息 (b) 双量化通过量化减少平均内存占用量化常数，以及 (c) 用于管理内存峰值的分页优化器。我们使用 QLoRA 对 1,000 多个模型进行微调，提供跨 8 个指令数据集、多种模型类型（LLaMA、T5）和无法通过常规微调运行的模型规模（例如 33B 和65B参数模型）。我们的结果表明，即使使用比以前的 SoTA 更小的模型，QLoRA 对小型高质量数据集的微调也会产生最先进的结果。我们提供了基于人类和 GPT-4 评估的聊天机器人性能的详细分析，表明 GPT-4 评估是人类评估的廉价且合理的替代方案。此外，我们发现当前的聊天机器人基准测试无法准确评估聊天机器人的性能水平。我们发布了所有模型和代码，包括用于 4 位训练的 CUDA 内核。
License and Intended Use
许可和预期用途

We release the resources associated with QLoRA finetuning in this repository under MIT license. In addition, we release the Guanaco model family for base LLaMA model sizes of 7B, 13B, 33B, and 65B. These models are intended for purposes in line with the LLaMA license and require access to the LLaMA models.
我们根据 MIT 许可在此存储库中发布与 QLoRA 微调相关的资源。此外，我们还发布了用于 7B、13B、33B 和 65B 基本 LLaMA 模型尺寸的 Guanaco 模型系列。这些模型旨在用于符合 LLaMA 许可证的目的，并且需要访问 LLaMA 模型。
Demo 演示

Guanaco is a system purely intended for research purposes and could produce problematic outputs.
Guanaco 是一个纯粹用于研究目的的系统，可能会产生有问题的输出。

    Access the live demo here. Note this is the 33B model, the 65B model demo will come later.
    在此处访问现场演示。注意这里是33B型号，65B型号的demo稍后会有。

    Or host your own Guanaco gradio demo directly in Colab with this notebook. Works with free GPUs for 7B and 13B models.
    或者使用此笔记本直接在 Colab 中托管您自己的 Guanaco gradio 演示。适用于 7B 和 13B 型号的免费 G​​PU。

    Alternatively, can you distinguish ChatGPT from Guanaco? Give it a try! You can access the model response Colab here comparing ChatGPT and Guanaco 65B on Vicuna prompts.
    或者，您能区分 ChatGPT 和 Guanaco 吗？试一试！您可以在此处访问模型响应 Colab，在 Vicuna 提示上比较 ChatGPT 和 Guanaco 65B。

Installation 安装

To load models in 4bits with transformers and bitsandbytes, you have to install accelerate and transformers from source and make sure you have the latest version of the bitsandbytes library (0.39.0). After installing PyTorch (follow instructions here), you can achieve the above with the following command:
要使用 transformers 和 bitsandbytes 加载 4 位模型，您必须从源代码安装加速器和 transformers，并确保您拥有最新版本的 bitsandbytes 库 (0.39.0)。安装 PyTorch 后（按照此处的说明进行操作），您可以使用以下命令实现上述目的：

pip install -U -r requirements.txt

Getting Started 入门

The qlora.py code is a starting point for finetuning and inference on various datasets. Basic command for finetuning a baseline model on the Alpaca dataset:
qlora.py 代码是对各种数据集进行微调和推理的起点。在羊驼数据集上微调基线模型的基本命令：

python qlora.py --model_name_or_path <path_or_name>

For models larger than 13B, we recommend adjusting the learning rate:
对于大于 13B 的模型，我们建议调整学习率：

python qlora.py –learning_rate 0.0001 --model_name_or_path <path_or_name>

To replicate our Guanaco models see below.
要复制我们的 Guanaco 模型，请参见下文。
Tutorials and Demonstrations
教程和演示

Here is a blog discussing 4-bit quantization, QLoRA, and how they are integrated in transformers.
这是一篇讨论 4 位量化、QLoRA 以及它们如何集成到转换器中的博客。

You can host your own gradio Guanaco demo directly in Colab following this notebook. In addition, here are Colab notebooks with examples for inference and finetuning using QLoRA:
您可以按照本笔记本直接在 Colab 中托管自己的 gradio Guanaco 演示。此外，以下是 Colab 笔记本，其中包含使用 QLoRA 进行推理和微调的示例：

    Inference notebook  推理笔记本
    Finetuning notebook  微调笔记本

Other examples are found under the examples/ folder.
其他示例位于 examples/ 文件夹下。
Quantization 量化

Quantization parameters are controlled from the BitsandbytesConfig (see HF documenation) as follows:
量化参数由 BitsandbytesConfig 控制（参见 HF 文档），如下所示：

    Loading in 4 bits is activated through load_in_4bit
    通过 load_in_4bit 激活加载4位
    The datatype used for the linear layer computations with bnb_4bit_compute_dtype
    用于线性层计算的数据类型 bnb_4bit_compute_dtype
    Nested quantization is activated through bnb_4bit_use_double_quant
    通过 bnb_4bit_use_double_quant 激活嵌套量化
    The datatype used for qunatization is specified with bnb_4bit_quant_type. Note that there are two supported quantization datatypes fp4 (four bit float) and nf4 (normal four bit float). The latter is theoretically optimal for normally distributed weights and we recommend using nf4.
    用于量化的数据类型用 bnb_4bit_quant_type 指定。请注意，有两种支持的量化数据类型 fp4 （四位浮点数）和 nf4 （普通四位浮点数）。后者在理论上对于正态分布的权重是最优的，我们建议使用 nf4 。

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path='/name/or/path/to/your/model',
        load_in_4bit=True,
        device_map='auto',
        max_memory=max_memory,
        torch_dtype=torch.bfloat16,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='nf4'
        ),
    )

Paged Optimizer 分页优化器

You can access the paged optimizer with the argument --optim paged_adamw_32bit
您可以使用参数 --optim paged_adamw_32bit 访问分页优化器
Guanaco Finetuning 原驼微调

You can select --dataset oasst1 to load the OpenAssistant dataset that was used to train Guanaco. You can also find it on HF at timdettmers/openassistant-guanaco.
您可以选择 --dataset oasst1 来加载用于训练 Guanaco 的 OpenAssistant 数据集。您还可以在 HF 上的 timdettmers/openassistant-guanaco 找到它。

We include scripts to reproduce the hyperparameters of Guanaco model training for various sizes at ./scripts/finetune_guanaco*.sh. Make sure to adjust per_device_train_batch_size and gradient_accumulation_steps so that their product is 16 and training fits on your GPUs.
我们在 ./scripts/finetune_guanaco*.sh 包含了用于重现各种尺寸的 Guanaco 模型训练的超参数的脚本。确保调整 per_device_train_batch_size 和 gradient_accumulation_steps ，使它们的乘积为 16 并且训练适合您的 GPU。
Using Local Datasets 使用本地数据集

You can specify the path to your dataset using the --dataset argument. If the --dataset_format argument is not set, it will default to the Alpaca format. Here are a few examples:
您可以使用 --dataset 参数指定数据集的路径。如果未设置 --dataset_format 参数，它将默认为羊驼格式。这里有一些例子：

    Training with an alpaca format dataset:
    使用羊驼格式数据集进行训练：

    python qlora.py --dataset="path/to/your/dataset"

    Training with a self-instruct format dataset:
    使用自指导格式数据集进行训练：

    python qlora.py --dataset="path/to/your/dataset" --dataset_format="self-instruct"

Multi GPU 多GPU

Multi GPU training and inference work out-of-the-box with Hugging Face's Accelerate. Note that the per_device_train_batch_size and per_device_eval_batch_size arguments are global batch sizes unlike what their name suggest.
多 GPU 训练和推理通过 Hugging Face 的 Accelerate 开箱即用。请注意， per_device_train_batch_size 和 per_device_eval_batch_size 参数是全局批量大小，与其名称所暗示的不同。

When loading a model for training or inference on multiple GPUs you should pass something like the following to AutoModelForCausalLM.from_pretrained():
在多个 GPU 上加载模型进行训练或推理时，您应该将类​​似以下的内容传递给 AutoModelForCausalLM.from_pretrained() ：

device_map = "auto"
max_memory = {i: '46000MB' for i in range(torch.cuda.device_count())}

Sample Outputs 示例输出

We provide generations for the models described in the paper for both OA and Vicuna queries in the eval/generations folder. These are intended to foster further research on model evaluation and analysis.
我们为 eval/generations 文件夹中的 OA 和 Vicuna 查询的论文中描述的模型提供生成。这些旨在促进对模型评估和分析的进一步研究。

Can you distinguish ChatGPT from Guanaco? Give it a try! You can access the model response Colab here comparing ChatGPT and Guanaco 65B on Vicuna prompts.
你能区分 ChatGPT 和 Guanaco 吗？试一试！您可以在此处访问模型响应 Colab，在 Vicuna 提示上比较 ChatGPT 和 Guanaco 65B。
Evaluation 评估

We include scripts adapted from the FastChat repo to automatically evaluate model generations using GPT-4. We include script for comparisons relative to ChatGPT with scores out of 10 as well as "pairwise comparisons" with three class labeling (win, loose, or tie). These are found in the eval folder.
我们包括改编自 FastChat 存储库的脚本，以使用 GPT-4 自动评估模型生成。我们包括用于与 ChatGPT 进行比较的脚本，得分为 10 分，以及带有三类标签（赢、输或平）的“成对比较”。这些位于 eval 文件夹中。

To facilitate the replication of our evaluation and future work in this area, we release GPT-4 and human ratings of our systems. These are found under eval/ratings-human and eval/ratings-gpt4.
为了促进我们在该领域的评估和未来工作的复制，我们发布了 GPT-4 和我们系统的人工评级。这些位于 eval/ratings-human 和 eval/ratings-gpt4 下。

More details can be found at eval/EVAL_README.md.
可以在 eval/EVAL_README.md 找到更多详细信息。
Known Issues and Limitations
已知问题和限制

Here a list of known issues and bugs. If your issue is not reported here, please open a new issue and describe the problem.
这里是已知问题和错误的列表。如果您的问题未在此处报告，请打开一个新问题并描述问题。

    4-bit inference is slow. Currently, our 4-bit inference implementation is not yet integrated with the 4-bit matrix multiplication
    4 位推理很慢。目前，我们的 4 位推理实现尚未与 4 位矩阵乘法集成
    Resuming a LoRA training run with the Trainer currently not supported by HF.
    使用 HF 当前不支持的训练器恢复 LoRA 训练运行。
    Currently, using bnb_4bit_compute_type='fp16' can lead to instabilities. For 7B LLaMA, only 80% of finetuning runs complete without error. We have solutions, but they are not integrated yet into bitsandbytes.
    目前，使用 bnb_4bit_compute_type='fp16' 会导致不稳定。对于 7B LLaMA，只有 80% 的微调运行完成且没有错误。我们有解决方案，但它们尚未集成到 bitsandbytes 中。
    Make sure that tokenizer.bos_token_id = 1 to avoid generation issues.
    确保 tokenizer.bos_token_id = 1 以避免生成问题。
    If you get an this issue ("illegal memory access") then you should use a newer HF LLaMA conversion or downgrade your PyTorch version.
    如果遇到此问题（“非法内存访问”），则应使用更新的 HF LLaMA 转换或降级 PyTorch 版本。
