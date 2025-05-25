from substack_api.auth import SubstackAuth

auth = SubstackAuth("substack.com_cookies.json")
print(auth.get("https://substack.com"))
