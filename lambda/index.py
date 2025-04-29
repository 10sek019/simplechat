# lambda/index.py
import json
import os
import re  # 正規表現モジュールをインポート
import urllib.request

model_url = 'https://86d9-34-125-105-210.ngrok-free.app/generate'

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        message = event['prompt']
        print("Processing message:", message)
        
        # # 会話履歴を使用
        # messages = conversation_history.copy()
        
        # # ユーザーメッセージを追加
        # messages.append({
        #     "role": "user",
        #     "content": message
        # })
        
        # リクエストペイロード
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
            }
        
        print("payload:", json.dumps(request_payload))
        
        # APIを呼び出し
        data = json.dumps(request_payload).encode("utf-8")
        req = urllib.request.Request(
             url=model_url,
             data=data,
             headers={"Content-Type": "application/json"},
             method="POST",
             )

        with urllib.request.urlopen(req) as res:
             response = json.loads(res.read().decode("utf-8"))
        
        # 応答の検証
        if not response.get('generated_text'):
            raise Exception("No response content from the model")
        
        # アシスタントの応答を取得
        assistant_response = response["generated_text"]
        
        # # アシスタントの応答を会話履歴に追加
        # messages.append({
        #     "role": "assistant",
        #     "content": assistant_response
        # })
        
        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
