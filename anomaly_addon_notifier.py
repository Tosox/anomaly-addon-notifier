import datetime
import json
import re
import schedule
import time
import toml
from curl_cffi import requests
from dataclasses import dataclass
from string import Template
from typing import List, Optional
from xml.etree import ElementTree

CONFIG = toml.load('config.toml')
MESSAGE_TEMPLATE = Template(open('message.json', 'r', encoding='utf-8').read())
LAST_CHECKED_FILENAME = 'last_update.txt'
NAMESPACES = { 'media': 'http://search.yahoo.com/mrss/' }

SCHEDULE_INTERVAL = CONFIG['schedule']['interval']
WEBHOOK_URLS = CONFIG['webhook']['urls']
RSS_FEED_URL = CONFIG['rss_feed']['url']

session = requests.Session()

@dataclass
class AddonData:
	title: str
	desc: str
	timestamp: str
	img: str
	url: str

def format_rfc2822_to_datetime(timestamp: str) -> datetime.datetime:
	return datetime.datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')

def datetime_to_iso8601(dt: datetime.datetime) -> str:
	return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def fix_broken_xml_entities(text: str) -> str:
	# Replace only broken named entities (anything that starts with & and ends with ; but isn't standard)
	known_entities = { 'amp', 'lt', 'gt', 'apos', 'quot' }
	return re.sub(
		r'&([a-zA-Z0-9]+);',
		lambda m: m.group(0) if m.group(1) in known_entities else f'&amp;{m.group(1)};',
		text
	)

def save_last_checked(timestamp: int):
	with open(LAST_CHECKED_FILENAME, 'w') as file:
		file.write(f'{timestamp}\n')

def get_last_checked() -> int:
	try:
		with open(LAST_CHECKED_FILENAME, 'r') as file:
			return int(file.readline())
	except:
		return 0

def create_embed(addon: AddonData, formatted_ts: str) -> dict:
	safe_desc = addon.desc.replace('\n', ' ').replace('"', '\\"')
	embed = MESSAGE_TEMPLATE.substitute(
		title=addon.title,
		description=safe_desc,
		timestamp=formatted_ts,
		url=addon.url,
		image_url=addon.img
	)
	return json.loads(embed)

def fetch_rss_feed() -> Optional[str]:
	try:
		response = session.get(RSS_FEED_URL, impersonate='firefox')
		if response.status_code == 200:
			return fix_broken_xml_entities(response.text)
		print(f'Error fetching feed: {response.status_code} {response.text}')
	except Exception as e:
		print(f'Exception fetching feed: {e}')
	return None

def parse_rss_feed(xml_data: str) -> List[AddonData]:
	addons = []
	try:
		root = ElementTree.fromstring(xml_data)
		for item in root.findall('.//item'):
			addons.append(AddonData(
				title=item.findtext('title'),
				timestamp=item.findtext('pubDate'),
				url=item.findtext('link'),
				img=item.find('media:content', NAMESPACES).attrib.get('url', ''),
				desc=item.find('media:content/media:description', NAMESPACES).text or ''
			))
	except Exception as e:
		print(f'Error parsing RSS feed: {e}')
	return addons

def post_webhook_message(addon: AddonData, iso_timestamp: str):
	embed = create_embed(addon, iso_timestamp)
	for webhook_url in WEBHOOK_URLS:
		response = requests.post(webhook_url, json=embed)
		if response.status_code != 204:
			print(f'Webhook error ({response.status_code}): {response.text}')

def main():
	now = datetime.datetime.now()
	print(f'Running at {now:%d. %B %Y %H:%M:%S}')

	last_checked_ts = get_last_checked()
	xml_data = fetch_rss_feed()
	if not xml_data:
		return

	addons = parse_rss_feed(xml_data)
	addons.reverse()

	new_timestamp = last_checked_ts
	for addon in addons:
		addon_dt = format_rfc2822_to_datetime(addon.timestamp)
		addon_ts = int(addon_dt.timestamp())

		if addon_ts <= last_checked_ts:
			continue

		iso_timestamp = datetime_to_iso8601(addon_dt)
		post_webhook_message(addon, iso_timestamp)
		print(f' New addon found: {addon.title}')
		new_timestamp = max(new_timestamp, addon_ts)

	if new_timestamp > last_checked_ts:
		save_last_checked(new_timestamp)

	print('Loop finished')

if __name__ == '__main__':
	main()
	schedule.every(SCHEDULE_INTERVAL).minutes.do(main)
	while True:
		schedule.run_pending()
		time.sleep(1)
