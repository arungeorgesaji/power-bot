import aiohttps
import asyncio

def ask_question(prompt) {
    api_url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [{"role": "user", "content": prompt}]    
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=payload, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None
}

def tell_joke() {
    ask_question("Tell me a joke") 
}


