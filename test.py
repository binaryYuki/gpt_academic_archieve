import json


def process_request(input_data):
    # 解析 JSON 字符串并加载为 Python 字典
    parsed_data = json.loads(input_data['text'])

    # 获取 data 字段
    data = parsed_data.get("data", [])

    # 在 data 中查找需要插入 HTML 代码的嵌套列表
    for i, item in enumerate(data):
        if isinstance(item, list):
            # 添加会话到期的 HTML 说明
            session_expired_html = [
                "<div class=\"markdown-body\"><p>Session expired</p></div>",
                "<div class=\"markdown-body\"><p>Please refresh the page and try again.</p></div>"
            ]
            item.append(session_expired_html)
            break  # 假设只有一个嵌套列表需要处理，找到后立即退出循环

    # 准备生成的响应数据
    output_data = {
        "msg": "process_generating",
        "output": {
            "data": data,
            "is_generating": True,
            "duration": 0.0004470348358154297,
            "average_duration": 0.2541402578353882
        },
        "success": True
    }

    # 返回处理后的数据
    return output_data


# 示例请求数据
input_data = {
    'type': 'websocket.receive',
    'text': '{"data":[null,4096,"gpt-4o","test","",1,1,[["<div class=\\"markdown-body\\"><p>hi</p></div>","<div class=\\"markdown-body\\"><p>Hello! How can I assist you today?</p></div>"],["<div class=\\"markdown-body\\"><p>1+1</p></div>","<div class=\\"markdown-body\\"><p>1 + 1 equals 2. How can I assist you further?</p></div>"],["<div class=\\"markdown-body\\"><p>wow</p></div>","<div class=\\"markdown-body\\"><p>I\'m glad you found that helpful! Is there anything else you need assistance with, whether it\'s writing, programming, or something else?</p></div>"]],null,"Serve me as a writing and programming assistant.","",null],"event_data":null,"fn_index":16,"session_hash":"3ofslul7chl"}'
}

# 调用函数并打印返回值
result = process_request(input_data)
print(result)
