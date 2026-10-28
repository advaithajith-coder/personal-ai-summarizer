import os
import unittest
from unittest.mock import patch, Mock
import providers

class ProviderTests(unittest.TestCase):
    def test_private_uses_only_local(self):
        reply = Mock()
        reply.json.return_value = {'response': 'local summary'}
        with patch('providers.httpx.post', return_value=reply) as post:
            self.assertEqual(providers.generate({'model':'local','provider':'local'}, 'private text'), 'local summary')
            self.assertNotIn('groq.com', post.call_args.args[0])
            self.assertNotIn('headers', post.call_args.kwargs)

    def test_groq_missing_key_never_sends(self):
        with patch.dict(os.environ, {'GROQ_API_KEY':''}), patch('providers.httpx.post') as post:
            with self.assertRaises(ValueError):
                providers.generate({'model':'cloud','provider':'groq'}, 'text')
            post.assert_not_called()

    def test_explicit_cloud_routes_summary_and_schema(self):
        reply = Mock()
        reply.json.return_value = {'choices':[{'message':{'content':'{"tasks":[]}'}}]}
        with patch.dict(os.environ, {'GROQ_API_KEY':'test-only'}), patch('providers.httpx.post', return_value=reply) as post:
            result=providers.generate({'model':'cloud','provider':'groq'}, 'text', {'type':'object'})
            self.assertEqual(result, '{"tasks":[]}')
            self.assertEqual(post.call_args.args[0], 'https://api.groq.com/openai/v1/chat/completions')
            self.assertTrue(post.call_args.kwargs['json']['response_format']['json_schema']['strict'])

if __name__ == '__main__':
    unittest.main()
