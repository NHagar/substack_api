from substack_api.user import User

test = User("5thingsyoushouldbuy")

print(test.get_raw_data()["handle"])
