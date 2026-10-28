"""Explicit provider routing. Never switch a private job to a cloud service."""
import os
import httpx

def validate(provider):
    if provider not in ('local', 'groq'):
        raise ValueError('Choose Private meeting or Groq.')
    if provider == 'groq' and not os.getenv('GROQ_API_KEY', '').strip():
        raise ValueError('Add GROQ_API_KEY to your laptop’s .env file and restart to enable Groq.')

def generate(job, prompt, schema=None):
    provider = job.get('provider', 'local')
    validate(provider)
    if provider == 'local':
        body = {'model': job['model'], 'stream': False, 'options': {'temperature': 0}, 'prompt': prompt}
        if schema:
            body['format'] = schema
        response = httpx.post(os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434') + '/api/generate', json=body, timeout=600)
        response.raise_for_status()
        return response.json()['response']
    body = {'model': job['model'], 'stream': False, 'temperature': 0, 'messages': [{'role': 'user', 'content': prompt}], 'reasoning_effort': 'low'}
    if schema:
        body['response_format'] = {'type': 'json_schema', 'json_schema': {'name': 'meeting_tasks', 'strict': True, 'schema': schema}}
    try:
        response = httpx.post('https://api.groq.com/openai/v1/chat/completions', headers={'Authorization': 'Bearer ' + os.environ['GROQ_API_KEY']}, json=body, timeout=600)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        raise ValueError(f'Groq request failed ({code}). Check your API key, account limits, and connection. No other provider was used.') from None
    except httpx.RequestError:
        raise ValueError('Could not reach Groq. Check your internet connection. No other provider was used.') from None
