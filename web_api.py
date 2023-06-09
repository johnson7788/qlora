#!/usr/bin/env python

# Load the model.
# Note: It can take a while to download LLaMA and add the adapter modules.
# You can also use the 13B model by loading in 4bits.
import datetime
import argparse
import os
from threading import Event, Thread
from uuid import uuid4
import requests
import torch
import logging
from peft import PeftModel    
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
# 日志保存的路径，保存到当前目录下的logs文件夹中
log_path = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_path):
    os.makedirs(log_path)
logfile = os.path.join(log_path, "api.log")
# 日志的格式
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s -  %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(logfile, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_id in stop_token_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


def convert_history_to_text(history):
    text = start_message + "".join(
        [
            "".join(
                [
                    f"### Human: {item[0]}\n",
                    f"### Assistant: {item[1]}\n",
                ]
            )
            for item in history[:-1]
        ]
    )
    text += "".join(
        [
            "".join(
                [
                    f"### Human: {history[-1][0]}\n",
                    f"### Assistant: {history[-1][1]}\n",
                ]
            )
        ]
    )
    return text


def log_conversation(conversation_id, history, messages, generate_kwargs):
    logging_url = os.getenv("LOGGING_URL", None)
    if logging_url is None:
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    data = {
        "conversation_id": conversation_id,
        "timestamp": timestamp,
        "history": history,
        "messages": messages,
        "generate_kwargs": generate_kwargs,
    }

    try:
        requests.post(logging_url, json=data)
    except requests.exceptions.RequestException as e:
        print(f"Error logging conversation: {e}")


def user(message, history):
    # Append the user's message to the conversation history
    return "", history + [[message, ""]]


def bot(history, temperature, top_p, top_k, repetition_penalty, conversation_id):
    print(f"history: {history}")
    # Initialize a StopOnTokens object
    stop = StopOnTokens()

    # Construct the input message string for the model by concatenating the current system message and conversation history
    messages = convert_history_to_text(history)

    # Tokenize the messages string
    input_ids = tok(messages, return_tensors="pt").input_ids
    input_ids = input_ids.to(m.device)
    streamer = TextIteratorStreamer(tok, timeout=10.0, skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0.0,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        streamer=streamer,
        stopping_criteria=StoppingCriteriaList([stop]),
    )

    stream_complete = Event()

    def generate_and_signal_complete():
        m.generate(**generate_kwargs)
        stream_complete.set()

    def log_after_stream_complete():
        stream_complete.wait()
        log_conversation(
            conversation_id,
            history,
            messages,
            {
                "top_k": top_k,
                "top_p": top_p,
                "temperature": temperature,
                "repetition_penalty": repetition_penalty,
            },
        )

    t1 = Thread(target=generate_and_signal_complete)
    t1.start()

    t2 = Thread(target=log_after_stream_complete)
    t2.start()

    # Initialize an empty string to store the generated text
    partial_text = ""
    for new_text in streamer:
        partial_text += new_text
        history[-1][1] = partial_text
        yield history


def get_uuid():
    return str(uuid4())

def webui():
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=".disclaimer {font-variant-caps: all-small-caps;}",
    ) as demo:
        conversation_id = gr.State(get_uuid)
        gr.Markdown(
            """<h1><center>Demo Chat</center></h1>
    """
        )
        chatbot = gr.Chatbot().style(height=500)
        with gr.Row():
            with gr.Column():
                msg = gr.Textbox(
                    label="Chat Message Box",
                    placeholder="Chat Message Box",
                    show_label=False,
                ).style(container=False)
            with gr.Column():
                with gr.Row():
                    submit = gr.Button("Submit")
                    stop = gr.Button("Stop")
                    clear = gr.Button("Clear")
        with gr.Row():
            with gr.Accordion("Advanced Options:", open=False):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            temperature = gr.Slider(
                                label="Temperature",
                                value=0.7,
                                minimum=0.0,
                                maximum=1.0,
                                step=0.1,
                                interactive=True,
                                info="Higher values produce more diverse outputs",
                            )
                    with gr.Column():
                        with gr.Row():
                            top_p = gr.Slider(
                                label="Top-p (nucleus sampling)",
                                value=0.9,
                                minimum=0.0,
                                maximum=1,
                                step=0.01,
                                interactive=True,
                                info=(
                                    "Sample from the smallest possible set of tokens whose cumulative probability "
                                    "exceeds top_p. Set to 1 to disable and sample from all tokens."
                                ),
                            )
                    with gr.Column():
                        with gr.Row():
                            top_k = gr.Slider(
                                label="Top-k",
                                value=0,
                                minimum=0.0,
                                maximum=200,
                                step=1,
                                interactive=True,
                                info="Sample from a shortlist of top-k tokens — 0 to disable and sample from all tokens.",
                            )
                    with gr.Column():
                        with gr.Row():
                            repetition_penalty = gr.Slider(
                                label="Repetition Penalty",
                                value=1.0,
                                minimum=1.0,
                                maximum=2.0,
                                step=0.1,
                                interactive=True,
                                info="Penalize repetition — 1.0 to disable.",
                            )
        # with gr.Row():
        #     gr.Markdown(
        #         "Disclaimer: The model can produce factually incorrect output, and should not be relied on to produce "
        #         "factually accurate information. The model was trained on various public datasets; while great efforts "
        #         "have been taken to clean the pretraining data, it is possible that this model could generate lewd, "
        #         "biased, or otherwise offensive outputs.",
        #         elem_classes=["disclaimer"],
        #     )
        # with gr.Row():
        #     gr.Markdown(
        #         "[Privacy policy](https://gist.github.com/samhavens/c29c68cdcd420a9aa0202d0839876dac)",
        #         elem_classes=["disclaimer"],
        #     )

        submit_event = msg.submit(
            fn=user,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=bot,
            inputs=[
                chatbot,
                temperature,
                top_p,
                top_k,
                repetition_penalty,
                conversation_id,
            ],
            outputs=chatbot,
            queue=True,
        )
        submit_click_event = submit.click(
            fn=user,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=bot,
            inputs=[
                chatbot,
                temperature,
                top_p,
                top_k,
                repetition_penalty,
                conversation_id,
            ],
            outputs=chatbot,
            queue=True,
        )
        stop.click(
            fn=None,
            inputs=None,
            outputs=None,
            cancels=[submit_event, submit_click_event],
            queue=False,
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    demo.queue(max_size=128, concurrency_count=2)
    demo.launch(server_name="0.0.0.0")

def get_response(input,history,temperature=0.7, top_p=0.9, top_k=0, repetition_penalty=1.0):
    """
    获取回复
    """
    conversation_id = "api"
    history = history + [[input, ""]]
    # Initialize a StopOnTokens object
    stop = StopOnTokens()

    # Construct the input message string for the model by concatenating the current system message and conversation history
    messages = convert_history_to_text(history)

    # Tokenize the messages string
    input_ids = tok(messages, return_tensors="pt").input_ids
    input_ids = input_ids.to(m.device)
    streamer = TextIteratorStreamer(tok, timeout=10.0, skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0.0,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        streamer=streamer,
        stopping_criteria=StoppingCriteriaList([stop]),
    )

    stream_complete = Event()

    def generate_and_signal_complete():
        m.generate(**generate_kwargs)
        stream_complete.set()

    def log_after_stream_complete():
        stream_complete.wait()
        log_conversation(
            conversation_id,
            history,
            messages,
            {
                "top_k": top_k,
                "top_p": top_p,
                "temperature": temperature,
                "repetition_penalty": repetition_penalty,
            },
        )

    t1 = Thread(target=generate_and_signal_complete)
    t1.start()

    t2 = Thread(target=log_after_stream_complete)
    t2.start()
    input_length = len(messages) # 用于判断哪些是新生成的
    # Initialize an empty string to store the generated text
    partial_text = ""
    total = 0
    for new_text in streamer:
        total += 1
        logging.info(f"生成的新的内容是: {new_text}")
        partial_text += new_text
    history[-1][1] = partial_text
    return partial_text, history


@app.route("/api/chat", methods=['POST'])
def chat():
    """
    Args: 基于aspect的情感分析，给定实体，判断实体在句子中的情感
    """
    jsonres = request.get_json()
    # 可以预测多条数据
    data = jsonres.get('data', None)
    if not data:
        return jsonify({"code": 400, "msg": "data不能为空"}), 400
    logging.info(f"数据分别是: {data}")
    input = data.get('text', '')
    history = data.get('history', [])
    response, history = get_response(input, history)
    result = {"response": response}
    logging.info(f"返回的结果是: {result}")
    return jsonify(result)

@app.route("/ping", methods=['GET', 'POST'])
def ping():
    """
    测试
    :return:
    :rtype:
    """
    return jsonify("Pong")

def parse_args():
    """
    返回arg变量和help
    :return:
    """
    parser = argparse.ArgumentParser(description="加载模型",formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--device', type=str, default="cuda", choices=("cuda","cpu"), help='使用的设备')
    parser.add_argument('-m', '--model_name_or_path', type=str, default="vicuna-13b", help='使用的base模型')
    parser.add_argument('-e', "--enable_lora", action='store_true', help="是否开启lora模型")
    parser.add_argument('-lr', "--lora_rank", type=int, default=32, help="lora的秩")
    parser.add_argument('-l', '--lora_path', type=str, default="output/checkpoint-30/adapter_model",  help='使用的lora模型')
    return parser.parse_args(), parser.print_help

if __name__ == '__main__':
    args, helpmsg = parse_args()
    enable_lora = args.enable_lora
    model_name2path = {
        "vicuna-7b": "/home/wac/johnson/project/model/vicuna-7b",
        "vicuna-13b": "/home/wac/johnson/project/model/vicuna-13b",
    }
    belong_lamma_model = ["vicuna-7b", "vicuna-13b"]
    # model_name = "THUDM/chatglm-6b"
    model_name = model_name2path.get(args.model_name_or_path) if model_name2path.get(args.model_name_or_path) else args.model_name_or_path
    if model_name in belong_lamma_model or os.path.basename(model_name) in belong_lamma_model:
        # 用于确定tokenizer
        is_lambda_model = True
    else:
        is_lambda_model = False
    adapters_name = args.lora_path
    if enable_lora:
        assert os.path.exists(adapters_name), f"lora模型不存在: {adapters_name}"

    print(f"开始加载模型 {model_name} 到内存中")

    m = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_4bit=True,
        torch_dtype=torch.bfloat16,
        device_map={"": 0},
        trust_remote_code=True,
    )
    # 如果使用lora模型，需要开启下面2行
    if enable_lora:
        print(f"使用lora模型，加载的模型是: {adapters_name}")
        m = PeftModel.from_pretrained(m, adapters_name)
        m = m.merge_and_unload()
    else:
        print(f"使用原始模型，不使用lora模型")
    if is_lambda_model:
        tok = LlamaTokenizer.from_pretrained(model_name)
        tok.bos_token_id = 1
    else:
        tok = AutoTokenizer.from_pretrained(model_name)
    stop_token_ids = [0,2]  # 0: pad, 2: eos??

    print(f"成功加载模型 {model_name}到内存")

    max_new_tokens = 1536
    start_message = "A chat between a curious human and an artificial intelligence assistant. \nThe assistant gives helpful, detailed, and polite answers to the human's questions."
    app.run(host='0.0.0.0', port=7087, debug=False, threaded=True)
