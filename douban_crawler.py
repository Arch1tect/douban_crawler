import requests
import json
import sys
import random
print(sys.version)
from lxml import etree


local_nodebb = False

nodebb_url = "https://catlog.club"
user_token = "7d5b0649-c3a1-4ab0-a1f0-db16335be838"
if local_nodebb:
	nodebb_url = "http://localhost:4567"
	user_token = "60687271-a626-423d-a923-9491c980a3fd"


print('requesting ...')
resp = requests.get("https://www.douban.com/group/topic/125239946/")
print('request returned')
html_str = resp.text
# print(html_str)
elm_tree = etree.HTML(html_str)
title = elm_tree.xpath('//title')[0].text
print(title)
images = elm_tree.xpath('//div[@id="link-report"]/div//img[@src]')
print(images)
img_markdowns = []
for img in images:
	img_src = img.attrib['src']
	img_name = img_src.split('/')[-1]
	print(img_src)
	img_resp = requests.get(img_src, allow_redirects=True)
	open(img_name, 'wb').write(img_resp.content)

	files = {'files[]': open(img_name, 'rb')}
	headers = {
	    'Authorization': "Bearer " + user_token,
	}
	img_upload_resp = requests.post(nodebb_url+"/api/v2//util/upload", headers=headers, files=files)
	print(img_upload_resp.json()[0]['url'])

	markdown = "![]({})".format(img_upload_resp.json()[0]['url'])
	img_markdowns.append(markdown)

# content = etree.tostring(elm_tree.xpath('//div[@id="link-report"]/div')[0], encoding='utf-8').decode('utf-8')
content=''.join(elm_tree.xpath('//div[@id="link-report"]/div//text()'))
content='\n'.join(elm_tree.xpath('//div[@id="link-report"]/div//text()'))
content+='\n'+'\n\n'.join(img_markdowns)
print(content)

payload = {
	'cid': 2,
	'title': title,
	'content': content
}
payload = json.dumps(payload)
# print(payload)


headers = {
    'Content-Type': "application/json",
    'Authorization': "Bearer " + user_token,
}
catlog_resp = requests.post(nodebb_url+"/api/v2/topics", data=payload, headers=headers)
print(catlog_resp.status_code)



