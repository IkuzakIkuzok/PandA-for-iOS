
# (c) 2020 __guanine

import appex
import json
import os
import re
import requests
import ui
from datetime import datetime, timedelta
from credential import *
from html import unescape
from objc_util import ObjCInstance

LOGIN_URL = 'https://cas.ecs.kyoto-u.ac.jp/cas/login?service=https%3A%2F%2Fpanda.ecs.kyoto-u.ac.jp%2Fsakai-login-tool%2Fcontainer'
JSON_URL = 'https://panda.ecs.kyoto-u.ac.jp/direct/assignment/my.json'


class TableSource():
	def __init__(self, data):
		self.data = data
		self.danger = timedelta(days=1)
		self.warning = timedelta(days=5)
		self.success = timedelta(days=14)

	def tableview_number_of_rows(self, tv, s):
		return len(self.data)

	def tableview_cell_for_row(self, tv, s, r):
		cell = ui.TableViewCell('subtitle')
		ObjCInstance(cell.text_label).setAdjustsFontSizeToFitWidth_(True)
		remain = self.data[r][2]
		if remain < self.danger:
			cell.bg_color = '#f1cdcd'
			cell.border_color = '#e85555'
		elif remain < self.warning:
			cell.bg_color = '#d7aa57'
			cell.border_color = '#e2d4bf'
		elif remain < self.success:
			cell.bg_color = '#62b665'
			cell.border_color = '#cce6cf'
		else:
			cell.bg_color = '#777777'
			cell.border_color = '#dad6d6'

		cell.text_label.text = self.data[r][0]
		cell.detail_text_label.text = self.data[r][1]
		cell.border_width = 1
		return cell


class ComfortablePandA(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.bounds = (0, 0, 350, 500)
		self.btn = ui.Button(title='Load', action=self.load,
			background_color=(0, 0, 0, .1), tint_color='black',
			font=('HelveticaNeue-Light', 24), corner_radius=3
		)
		self.add_subview(self.btn)
		self.btn.frame = (100, 10, 150, 30)
		self.list = ui.TableView(frame=(20, 50, 310, 440), hidden=True)
		self.add_subview(self.list)
		self.status = ui.Label(frame=(20, 50, 310, 30), hidden=True)
		self.add_subview(self.status)

	def set_status(self, message):
		self.status.text = message

	def get_lectures(self, tabs):
		lectures = {}
		for tab in tabs:
			try:
				id = re.search(r'href="(.+?)"', tab).group(1)[-17:]
				name = unescape(re.search(r'title="(.+?)"', tab).group(1).split(']')[1])
				lectures[id] = name
			except:
				pass
		return lectures

	def get_assignments(self, items):
		assignments = []
		for item in items:
			if item['status'] != '公開':
				continue
			lecture = item['context']
			title = item['title']
			due = datetime.fromtimestamp(item['dueTime']['time'] // 1000)
			dueStr = item['dueTime']['display']
			assignments.append({
				'lecture_id': lecture,
				'title': title,
				'due': due,
				'dueStr': dueStr
			})
		return assignments

	def make_list_data(self, assignments, lectures):
		now = datetime.now()
		assignments = sorted(assignments, key=lambda x: x['due'])
		list_data = []
		for assignment in assignments:
			remain = assignment['due'] - now
			lecture = lectures[assignment['lecture_id']]
			title = assignment['title']
			due = assignment['dueStr']
			list_data.append((f'{lecture}\t{title}', f'{due} ({remain})', remain))
		return list_data

	@ui.in_background
	def load(self, sender):
		try:
			data = self.load_assignments()
			self.list.data_source = TableSource(data)
			self.list.reload()
			self.status.hidden = True
			self.list.hidden = False
		except RuntimeError as e:
			self.status.text_color = 'red'
			self.set_status(str(e))

	def download_content(self, url, method, data=None):
		try:
			if method == 'post':
				res = self.session.post(url, data=data)
			else:
				res = self.session.get(url)
			res.raise_for_status()
		except HTTPError:
			raise RuntimeError('Could not access to PandA.')
		except Timeout:
			raise RuntimeError('Connection timed out.')
		except ConnectionError:
			raise RuntimeError('A network error occurred.')
		else:
			return res

	def load_assignments(self):
		self.list.hidden = True
		self.status.text_color = 'black'
		self.set_status('Logging in ...')
		self.status.hidden = False
		self.session = requests.session()
		res = self.download_content(LOGIN_URL, 'get')
		lt = re.search(r'<input type="hidden" name="lt" value="(.+?)".*>', res.text).group(1)

		login_info = {
			'username': USERNAME,
			'password': PASSWORD,
			'warn': 'true',
			'lt': lt,
			'execution': 'e1s1',
			'_eventId': 'submit'
		}

		res = self.download_content(LOGIN_URL, 'post', data=login_info)

		self.set_status('Collecting lectures\' information ...')
		text = res.text.replace('\n', '')  # Regular expression does not work as expected on multi-line string
		tabs = re.findall(r'<li class=".*?nav-menu.*?>.+?</li>', text)[1:]
		try:
			otherSiteList = re.search(r'<ul id="otherSiteList".*>.+?</ul>', text).group()
		except AttributeError:
			raise RuntimeError('Failed to log in to PandA.')
		tabs += re.findall(r'<li.*?>.+?</li>', otherSiteList)
		lectures = self.get_lectures(tabs)

		self.set_status('Downloading data ...')
		json_str = self.download_content(JSON_URL, 'get').text
		assignment_collection = json.loads(json_str)['assignment_collection']
		self.set_status('Parsing data ...')
		assignments = self.get_assignments(assignment_collection)
		return self.make_list_data(assignments, lectures)


def main():
	widget_name = __file__ + str(os.stat(__file__).st_mtime)
	widget_view = appex.get_widget_view()
	if widget_view is None or widget_view.name != widget_name:
		widget_view = ComfortablePandA()
		widget_view.name = widget_name
		appex.set_widget_view(widget_view)

if __name__ == '__main__':
	main()
