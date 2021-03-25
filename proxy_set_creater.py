import json


files = ['message.txt', 'message_2.txt']
pr_list = list()
for one in files:
    f = open(one)
    proxies = f.read().split('\n')
    for proxy in proxies:
        pr_list.append(proxy)

final = {'PROXIES': pr_list}
final_file = open('pr.json', 'w')
json.dump(final, final_file)
