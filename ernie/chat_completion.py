import requests
import json
from .utils import get_access_token
from .api_exception import APIException

#Those two are used to be able to compitable with the openai
class Message():
    def __init__(self, role, raw_content) -> None:
        self.message = {'role': role, 'content': raw_content['result']}
        self.raw_content = raw_content
class Response():
    def __init__(self, message) -> None:
        self.choices=[message]

model_list = {
    'ernie-bot-4':'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=',
    'ernie-bot':'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=',
    'llama_2_7b':'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_7b?access_token=',
    'llama_2_13b':'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_13b?access_token=',
    'llama_2_70b':'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_70b?access_token='
}

class ChatCompletion():
    @classmethod
    def create(cls, *args, **kwargs):
        messages = kwargs.pop("messages")
        model = kwargs.pop("model")
        temperature = kwargs.pop("temperature")
        complete_uri = model_list[model]
        if messages is None or messages ==[]:
            raise Exception("messages can not be empty")
        if model is None:
            raise Exception("model can not be empty")
        
        messange_to_send = []
        system_message = ''
        for message in messages:
            if message['role'] == 'system':
                system_message += message['content'] + '\n'
            else:
                messange_to_send.append(message)
        
        access_token = get_access_token()
        url = complete_uri+access_token
        
        data = {
            "messages": messange_to_send
        }
        if temperature is not None:
            data['temperature'] = temperature
        if system_message != '':
            data['system'] = system_message

        payload = json.dumps(data)
        
        
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_obj = response.json()
        if 'error_code' in response_obj:
            raise APIException(response_obj['error_code'], response_obj['error_msg'])
        return Response(Message("assistant", response_obj))
