import json
import requests
import hmac
import time
import hashlib
import math
import websocket #pip install websocket-client

class BitmaniaApi:
    def __init__(self):
        self.api_key = 'YOUR API KEY'
        self.api_secret = 'YOUR API SECRET'
        self.api_endpoint = 'https://api.bitmania-ex.com'
        self.websocket_endpoint = 'wss://socket.bitmania-ex.com/'
        self.account_id = 'YOUR ACCOUNT ID'

    def call_public_get_api(self,path):
        response = requests.get(self.api_endpoint + path, headers = { 'Content-Type': 'application/json' })
        return response

    def call_private_get_api(self,path):
        api_expires = str(math.floor(time.time() + 60))
        method = 'GET'
        sign_target = method + path + api_expires
        secret_bytes = bytes(self.api_secret.encode('utf-8'))
        sign_bytes = bytes(sign_target.encode('utf-8'))
        signature = hmac.new(secret_bytes, sign_bytes, hashlib.sha256).hexdigest()
        response = requests.get(
            self.api_endpoint + path
            ,headers = {
                'api-key': self.api_key,
                'api-expires': api_expires,
                'api-signature': signature,
                'Content-Type': 'application/json'
            })
        return response

    def call_post_api(self,path,param):
        api_expires = str(math.floor(time.time() + 60))
        body = json.dumps(param)
        method = 'POST'
        sign_target = method + path + api_expires + body
        secret_bytes = bytes(self.api_secret.encode('utf-8'))
        sign_bytes = bytes(sign_target.encode('utf-8'))
        signature = hmac.new(secret_bytes, sign_bytes, hashlib.sha256).hexdigest()
        response = requests.post(
            self.api_endpoint + path
            ,data = body
            ,headers = {
                'api-key': self.api_key,
                'api-expires': api_expires,
                'api-signature': signature,
                'Content-Type': 'application/json'
            })
        return response

    def connect_web_socket(self):
        self.websocket = websocket.WebSocketApp(
            self.websocket_endpoint,
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)

        try:
            self.websocket.run_forever()
        except KeyboardInterrupt:
            self.websocket.close()

    def on_message(self, message):
        print ('received message:' + message)

    def on_error(self, error):
        print (error)

    def on_close(self, ws):
        print ('disconnected websocket')

    def on_open(self):
        print ('connected websocket')
        # public message
        self.subscribe_public_message('exe:BTCJPY') # execution
        self.subscribe_public_message('ob:BTCJPY') # order book
        self.subscribe_public_message('idx:IBTC') # index price
        # private message
        self.subscribe_private_message('p_ord') # order
        self.subscribe_private_message('p_exe') # execution
        self.subscribe_private_message('p_pos') # position
        self.subscribe_private_message('p_col') # collateral
        self.subscribe_private_message('p_los') # loscutt

    def subscribe_private_message(self, subscribe_type):
        api_expires = str(math.floor(time.time() + 60))
        param = subscribe_type + ':' + self.account_id
        sign_target = "subscribe" + param + api_expires
        secret_bytes = bytes(self.api_secret.encode('utf-8'))
        sign_bytes = bytes(sign_target.encode('utf-8'))
        signature = hmac.new(secret_bytes, sign_bytes, hashlib.sha256).hexdigest()
        message = {
            'type': 'subscribe',
            'param': param,
            'api-key': self.api_key,
            'api-expires': api_expires,
            'api-signature': signature
        }
        self.websocket.send(json.dumps(message))

    def subscribe_public_message(self, subscribe_param):
        message = {
            'type': 'subscribe',
            'param': subscribe_param
        }
        self.websocket.send(json.dumps(message))
        
    def get_active_orders(self):
        response = self.call_private_get_api('/api/v1/order/active_orders?symbol=BTCJPY')
        print(response.text)

    def get_public_executions(self):
        response = self.call_private_get_api('/api/v1/public_execution/public_executions?symbol=BTCJPY')
        print(response.text)

    def post_new_order(self):
        order_param = {
            'buy_sell': 1, # 1:Buy, 2:Sell
            'symbol': 'BTCJPY',
            'price': 900000,
            'price_type': 1, # 1:Limit, 2:Market
            'size': 1,
            'time_in_force': 1, # 1:GTC, 2:IOC, 3:FOK
            'trigger_type': 1, # 1:None, 2:LTP, 3:INDEX
            'trigger_price': 0, 
            'is_post_only': 0 # 0:false, 1:true
        }
        response = self.call_post_api('/api/v1/order/new_order', order_param)
        print(response)
        print(response.text)



api = BitmaniaApi()
api.get_public_executions()
api.post_new_order()
api.get_active_orders()
api.connect_web_socket()