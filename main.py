import aiohttp
import asyncio
import os
import random
import binascii
import base64
import json

headers = {
        "authority": "www.binance.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.6",
        "cache-control": "no-cache",
        "clienttype": "web",
        "content-type": "application/json",
        "lang": "en",
        "origin": "https://www.binance.com",
        "pragma": "no-cache",
        "referer": "https://www.binance.com/en/game/tg/moon-bix",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Brave\";v=\"128\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "android",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/124.0.2478.50 Version/17.0 Mobile/15E148 Safari/604.1",
}

query_id = "query_id=xxxx"

def generate_random_hex_payload(length):
    # Generate random bytes
    random_bytes = os.urandom(length)
    # Convert bytes to hexadecimal string
    hex_payload = binascii.hexlify(random_bytes).decode('utf-8')
    return hex_payload

def random_int(min_int, max_int):
    return random.randint(min_int, max_int)

async def auth_token():
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken"
    payload = {
  "queryString": query_id,
  "socialType": "telegram"
}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    response_json = await response.json()
                    print("Authentication successful")
                    access_token = response_json.get('data', {}).get('accessToken')
                    return access_token
                else:
                    print("Authentication failed")
                    response_text = await response.text()
                    print(f"Response: {response_text}")
    except Exception as e:
        print(f"Error: {e}")

async def get_user_info(id,access_token):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info"
    payload = {
        "resourceId": id,
    }
    headers["x-growth-token"]= f"{access_token}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if data.get("success"):
                            balance = data.get("data", {}).get("metaInfo", {}).get("totalGrade")
                            totalAttempts = data.get("data", {}).get("metaInfo", {}).get("totalAttempts")
                            consumedAttempts = data.get("data", {}).get("metaInfo", {}).get("consumedAttempts")
                            remainingAttempts = totalAttempts - consumedAttempts
                            print(f"remaining Attempts: {remainingAttempts}")
                            print(f"Balance: {balance}")
                            return remainingAttempts
                            
                        else:
                            print("Request was not successful")
                    except aiohttp.ContentTypeError:
                        response_text = await response.text()
                        print(f"Unexpected content type: {response_text}")
                else:
                    print("Failed to get user info")
                    response_text = await response.text()
                    print(response_text)
                
    except Exception as e:
        print(f"Error: {e}")
        
async def get_list_tasks(access_token, id):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list"
    payload = {
        "resourceId": id,
    }
    
    headers["x-growth-token"]= f"{access_token}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    try:
                        tasks = await response.json()
                        return tasks
                                        
                        
                    except aiohttp.ContentTypeError:
                        response_text = await response.text()
                        print(f"Unexpected content type: {response_text}")
                else:
                    print("Failed to get user info")
                    response_text = await response.text()
                    print(response_text)
                
    except Exception as e:
        print(f"Error: {e}")
        
async def complete_task(access_token, resource_id,amount):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete"
    payload = {
        "resourceIdList": [resource_id],
        "refferalCode": "",
    }
    headers["x-growth-token"]= f"{access_token}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    print(f"Task with Resource ID {resource_id} completed successfully.Reward: {amount}")
                else:
                    print(f"Failed to complete task with Resource ID {resource_id}")
                    response_text = await response.text()
                    print(response_text)
    except Exception as e:
        print(f"Error: {e}")
        
        
async def play_game(access_token, resource_id):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start"
    payload = {
        "resourceId": resource_id,
    }
    headers["x-growth-token"]= f"{access_token}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    print("Game started successfully")
                    await get_user_info("2056", access_token)
                    data = await response.json()
                    
                    json_payload = json.dumps(data)

                    # Encode the JSON string to a base64 string
                    encoded_payload = base64.b64encode(json_payload.encode()).decode()
                    print("Playing game for 45 seconds")
                    await asyncio.sleep(45)
                    await game_complete(access_token, resource_id,encoded_payload)
                else:
                    print("Failed to play game")
                    response_text = await response.text()
                    print(response_text)
    except Exception as e:
        print(f"Error: {e}")
        
async def game_complete(access_token, resource_id,encoded_payload):
    url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete"
    payload = {
                "resourceId": resource_id,
                "payload": encoded_payload,
                "log": 120
                }
    
    headers["x-growth-token"]= f"{access_token}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    print("Game complete successfully")
                    data = await response.json()
                    print(data)
                    await get_user_info("2056", access_token)
                else:
                    print("Failed to play game")
                    response_text = await response.text()
                    print(response_text)
    except Exception as e:
        print(f"Error: {e}")
    
    
        
    
async def main():
    
    access_token = await auth_token()
    if access_token:
        await get_user_info("2056", access_token)
        tasks = await get_list_tasks(access_token, "2056")
        if tasks:
            if tasks.get("success"):
                            print("Finding Available Tasks")
                            for task in tasks.get("data", {}).get("data", []):
                                
                                for sub_task in task.get("taskList", {}).get("data", []):
                                    if sub_task.get("status") == "COMPLETED":
                                        print("Task already completed")
                                        continue
                                    if sub_task.get("type") == "THIRD_PARTY_BIND":
                                        continue
                                    resource_id = sub_task.get("resourceId")
                                    amount = sub_task.get("rewardList", [{}])[0].get("amount")
                                    await complete_task(access_token, resource_id,amount)
        else:
            print("No task available")
            
        await play_game(access_token, "2056")
# To run the main function
asyncio.run(main())