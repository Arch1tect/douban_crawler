import requests
import json
from time import sleep



douban_url = 'https://api.douban.com/v2/group/634017/topics'
nodebb_url = 'https://catlog.club'
nodebb_user_token = "b4579b30-322c-4dcb-9413-f2cf89c6e835"


existing_topics = []
def get_existing_topics():
	print('getting existing topics...')
	global existing_topics
	next_page = 'page=1'
	while next_page:
		print(next_page)
		resp = requests.get(nodebb_url+'/api/category/2/?'+next_page).json()
		topics = resp['topics']
		existing_topics += [topic['title'] for topic in topics]
		next_page = resp['pagination']['next']['qs'] if resp['pagination']['next']['active'] else None
	print(existing_topics)
def get_douban_topics():
	resp = requests.get(douban_url)
	topics = resp.json()['topics']
	print('done getting douban topics')
	return topics


def download_upload_img(img_src):
	img_name = img_src.split('/')[-1]
	img_resp = requests.get(img_src, allow_redirects=True)
	open(img_name, 'wb').write(img_resp.content)

	files = {'files[]': open(img_name, 'rb')}
	headers = {
		'Authorization': "Bearer " + nodebb_user_token,
	}
	img_upload_resp = requests.post(nodebb_url+"/api/v2//util/upload", headers=headers, files=files)
	print('img {} uploaded'.format(img_name))
	return img_upload_resp.json()[0]['url']


def create_topic(title, content):
	payload = {
		'cid': 2,
		'title': title,
		'content': content
	}
	payload = json.dumps(payload)
	headers = {
		'Content-Type': "application/json",
		'Authorization': "Bearer " + nodebb_user_token,
	}
	catlog_resp = requests.post(nodebb_url+"/api/v2/topics", data=payload, headers=headers)
	print('{} created: {}'.format(title, str(catlog_resp.ok)))
	if not catlog_resp.ok:
		print(catlog_resp.json())


def do_it():
	get_existing_topics()
	topics = get_douban_topics()
	count = 0
	for topic in topics:
		title = topic['title']
		content = topic['content']
		print(title)
		# check if topic title already in catlog
		if title in existing_topics:
			print('{} existed in catlog'.format(title))
			continue
		for photo in topic['photos']:
			photo_douban_src = photo['alt']
			tag = '<图片{}>'.format(photo['seq_id'])
			markdown = "\n\n![]({})".format(download_upload_img(photo_douban_src))
			content = content.replace(tag, markdown)

		create_topic(title, content)
		count = count + 1
		sleep(10)
	print('all done, created {} topics'.format(count))
	'养猫和住哪真的有关系'


if __name__ == "__main__":
	do_it()