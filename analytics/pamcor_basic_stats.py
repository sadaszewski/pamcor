#
# Copyright (C) Stanislaw Adaszewski, 2016
#


import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import re
from scipy.io import savemat
from PIL import Image, ImageDraw


exclude_names = ['Stan', 'Subject 1', 'AMPAC_001']
	# 'AMPAC_006', 'AMPAC_002-v2']


maze_px_width = 512
maze_px_height = 512


def process_form_replies(data):
	# player = data['player']

	min_date = datetime(9999, 9, 9)
	max_date = datetime(1000, 1, 1)

	uids = []
	names = []

	for (uid, forms) in data['formReply'].items():
		player = data['player'][uid]
		if player['nickname'] in exclude_names:
			continue
		uids.append(uid)
		names.append(player['nickname'])
		print('Player:', player['nickname'])
		for (date, reply) in forms.items():
			# print 'On', date, 'replies were:', reply
			date = list(map(int, date.split('_')))
			date = datetime(date[0], date[1], date[2])
			if date < min_date:
				min_date = date
			if date > max_date:
				max_date = date

	nsubjects = len(uids)
	nquestions = 2
	ndays = (max_date - min_date).days
	idx = np.argsort(names)
	uids = np.array(uids)[idx]

	print('min_date:', min_date)
	print('max_date:', max_date)
	print('nsubjects:', nsubjects)
	print('nquestions:', nquestions)
	print('ndays:', ndays)

	replies = np.zeros((nsubjects, ndays, nquestions), dtype=np.uint8)

	for i in range(nsubjects):
		uid = uids[i]
		for day in range(ndays):
			date = min_date + timedelta(day)
			k = '%d_%d_%d' % (date.year, date.month, date.day)
			form = data['formReply'][uid]
			if k in form:
				reply = form[k]
				if reply != '':
					reply = list(map(int, reply.split(',')))
					replies[i, day, :] = np.array(reply)+1


	savemat('pamcor_form_replies.mat', {'replies': replies})

	ind = np.arange(ndays) #

	fig, axes = plt.subplots(nsubjects, sharex=True)

	# print replies
	for i in range(nsubjects):
		uid = uids[i]
		# plt.subplot(nsubjects, 1, i + 1)
		ax = axes[i]
		width = 0.35
		ans1 = ax.bar(ind, replies[i, :, 0].squeeze(), width, color='r')
		ans2 = ax.bar(ind + width, replies[i, :, 1].squeeze(), width, color='g')
		ax.set_ylabel('Answers')
		ax.set_title('%s: answers by date' % data['player'][uid]['nickname'])
		plt.xticks(ind + width,
			['%04d-%02d-%02d' % (y.year, y.month, y.day) for y in [min_date + timedelta(x) for x in range(ndays)]],
			rotation='vertical')
		ax.legend((ans1[0], ans2[0]), ('Question 1', 'Question 2'))

	# plt.show()
	fig.set_size_inches(2048/96., 1024/96.)
	plt.savefig('form_replies.png', bbox_inches='tight', dpi=96)


def get_fill(idx):
	idx = idx % 1024

	if idx < 256:
		return (idx, 255, 0)
	elif idx < 512:
		return (255, 512 - idx, 0)
	elif idx < 768:
		return (255, 0, idx - 512)
	elif idx < 1024:
		return (1024 - idx, 0, 255)

def parse_log(text, gen_path_im=False):

	if gen_path_im:
		path_im = Image.new('RGB', (maze_px_width, maze_px_height))
		draw = ImageDraw.Draw(path_im)
		pass_cnt = defaultdict(lambda: defaultdict(lambda: 0))
		step_cnt = 0

	rxs = [
		'Starting game, level: ([0-9]+), score: ([0-9]+), hiscore: ([0-9]+)',
		'Background: ([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+(\\.[0-9]+)?)',
		'Ch 1: ([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+(\\.[0-9]+)?)',
		'Ch 2: ([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+(\\.[0-9]+)?)',
		'Bigger: (True|False)',
		'Shift: ([0-9]+(\\.[0-9]+)?)',
		'Screen size: ([0-9]+), ([0-9]+)',
		'Difficulty: ([0-9]+)',
		'Red/Blue Flip: ([0-9]+)',
		'Contrast: ([0-9]+(\\.[0-9]+)?)',
		'Weaker: (0|1)',
		'Creating maze, level: ([0-9]+)',
		'Placed ghost: ([0-9]+) at x: ([0-9]+), y: ([0-9]+), delay: ([0-9]+(\\.[0-9]+)?)',
		'Placed player at x: ([0-9]+), y: ([0-9]+), delay: ([0-9]+(\\.[0-9]+)?)',
		'Game started',
		'Automatic contrast decreased to: ([0-9]+(\\.[0-9]+)?)',
		'No wins, more than five fails, starting calibration procedure from contrast: ([0-9]+(\\.[0-9]+)?)',
		'Touch event began',
		'Player swiped: (left|right|down|up)',
		'Application moving to foreground, UTC date/time is: [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{7}Z',
		'Application moving to background',
	]

	hdr_matches = [None] * len(rxs)

	rxs = list(map(re.compile, rxs))

	magic = re.compile('[0-9]\\.[0-9]{6} ')
	# magic = re.compile('0.000000 ')


	# text.index('Placed player')
	# text.index('Game started')

	pos = 0

	# first parse a bit of header treating 0.000000 value as magic

	line_starts = []

	while True:
		match = magic.search(text, pos)
		if match is None:
			# raise ValueError('Early timestamp expected but not found')
			return None
		# print match.group(0)
		line_starts.append(match.start(0))
		# print pos
		pos = match.end(0)
		msg = text[pos:pos+12]
		# print msg
		if msg == 'Game started':
			# print 'OK, got to game started'
			break

	# print 'line_starts:', line_starts

	for i in range(len(line_starts) - 1):
		for k in range(len(rxs)):
			rx = rxs[k]
			match = rx.search(text, line_starts[i] + 9, line_starts[i + 1])
			if match is not None:
				# print 'Got a match:', match.group(0)
				hdr_matches[k] = match
				break
		if match is None:
			raise ValueError('Unrecognized log entry: %s' % text[line_starts[i]+9:line_starts[i+1]])

	# print 'Changing parsing mechanism...'

	rxs = [
		'Game started',
		'Ghost: ([0-9]+) moves from x: ([0-9]+), y: ([0-9]+), dx: (0|1|-1), dy: (0|1|-1)',
		'Player moving from x: ([0-9]+), y: ([0-9]+), dx: (0|1|-1), dy: (0|1|-1)',
		'Player ate a pill, score increase: (10|20|30)',
		'Touch event began',
		'Player swiped: (left|right|down|up)',
		'Player was killed by ghost: ([0-9]+) at x: ([0-9]+(\\.[0-9]+)?), y: ([0-9]+([\\.0-9]+)?)',
		'Game over, score: ([0-9]+), hiscore: ([0-9]+)',
		'Player passed to next level: ([0-9]+), score: ([0-9]+), hiscore: ([0-9]+)',
		'Player ate a power pill, bonus: (50)',
		'Gained bonus: (50|100|200|400|800|1600|3200|6400|12800|25600)',
		'Gained bonus: (75|150|300|600|1200|2400|4800|9600|19200)',
		'Power pill effect ended',
		'Application quit',
		'Application moving to foreground, UTC date/time is: [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{7}Z',
		'Application moving to background',
		'Player warped to x: ([0-9]+([\\.0-9]+)?)',
		'Ghost: ([0-9]+) warped to x: ([0-9]+([\\.0-9]+)?)'
	]

	rxs = list(map(re.compile, rxs))
	pos = line_starts[-1]

	magic = re.compile('[0-9]+\\.[0-9]{6} ')

	win = False
	loss = False
	score = -1

	while pos < len(text):
		match = magic.search(text, pos)
		if match is None or match.start(0) != pos:
			# raise ValueError('Timestamp expected but not found')
			print('Timestamp expected but not found')
			break
		# print 'magic found, len:', len(match.group(0)), 'match:', match.group(0)
		magic_match = match
		pos += len(match.group(0))
		ok = False
		for rx in rxs:
			match = rx.search(text, pos)
			if match is not None and match.start(0) == pos:
				# found

				# print magic_match.group(0), match.group(0)
				base_match = match

				if rx.groups > 0:
					last_grp = match.group(rx.groups)
					# print 'last_grp:', last_grp
					if last_grp[0] != '-' and len(last_grp) > 1 and \
						ord(last_grp[-1]) >= ord('0') and ord(last_grp[-1]) <= ord('9') and \
						match.end(0) < len(text):
						if match.group(0).startswith('Player was killed by ghost') or \
							match.group(0).startswith('Player warped to') or \
							(match.group(0).startswith('Ghost:') and 'warped to' in match.group(0)):

							match = rx.search(text, pos, match.end(0) - len(magic_match.group(0)) + 1)
							# match = rx.search(text, pos, match.end(0) - 1)
						elif match.group(0).startswith('Player ate a pill') or \
							match.group(0).startswith('Player ate a power pill') or \
							match.group(0).startswith('Gained bonus'):

							pass # match = rx.search(text, pos, match.end(0) - magic_match.group(0).index('.'))
						else:
							match = rx.search(text, pos, match.end(0) - magic_match.group(0).index('.'))
						# pos -= 1

				if match.group(0).startswith('Player moving') and gen_path_im:
					x1 = int(match.group(1))
					y1 = int(match.group(2))
					x2 = x1 + int(match.group(3))
					y2 = y1 + int(match.group(4))
					cnt1 = pass_cnt[x1][y1]
					cnt2 = pass_cnt[x2][y2]
					pass_cnt[x1][y1] += 1
					# pass_cnt[x2][y2] += 1

					draw.line([x1 * 16 + cnt1 * 4, y1 * 16 + cnt1 * 4,
						x2 * 16 + cnt2 * 4, y2 * 16 + cnt2 * 4], fill=get_fill(step_cnt), width=1)

					step_cnt += 1
				if match.group(0).startswith('Player passed to next level'):
					win = True
				elif match.group(0).startswith('Player was killed by ghost'):
					loss = True
				elif match.group(0).startswith('Game over'):
					score = int(match.group(1))
				#elif match.group(0).startswith('Player ate a pill'):
				#	score += int(match.group(1))
					# print magic_match.group(0), base_match.group(0)
					# print match.group(0), match.group(1)
					# import sys
					# if int(match.group(1)) != 10: sys.exit(-1)
				#elif match.group(0).startswith('Player ate a power pill'):
				#	score += int(match.group(1))
					# print match.group(0)
				#elif match.group(0).startswith('Gained bonus'):
				#	score += int(match.group(1))
					# print match.group(0)


				# print 'found match:', match.group(0)

				pos += len(match.group(0))
				ok = True
				break
		if not ok:
			raise ValueError('Unrecognized log entry encountered at pos: %d ... %s ...' % (pos, text[pos:pos+50]))

	ret = {}
	ret['hdr_matches'] = hdr_matches
	ret['duration'] = float(magic_match.group(0))
	ret['win'] = win
	ret['loss'] = loss
	ret['score'] = score
	ret['path_im'] = path_im if gen_path_im else None

	# import sys
	# if win:
		# path_im.save('test_path_im.png')
		# sys.exit(-1)

	return ret


def save_mosaic(fname, dic):
	print('save_mosaic(), fname:', fname)

	K = sorted(dic.keys())
	images = [dic[k] for k in K]
	print('K:', K)

	nx = ny = int(np.ceil(len(images) ** 0.5))
	print('nx:', nx, 'ny:', ny)

	mosaic = Image.new('RGB', (maze_px_width * nx, maze_px_height * ny))
	draw = ImageDraw.Draw(mosaic)

	cnt = 0
	for y in range(ny):
		for x in range(nx):
			# images[cnt].save(fname + '%d.png' % cnt)
			mosaic.paste(images[cnt], (x * maze_px_width, y * maze_px_height))
			draw.text((x * maze_px_width + 16, y * maze_px_height + 16),
				K[cnt].isoformat()[:10], fill=(255, 255, 255))
			cnt += 1
			if cnt == len(images):
				mosaic.save(fname)
				return


def process_play_time(data):
	uids = []
	names = []

	for (uid, logs) in data['logs'].items():
		player = data['player'][uid]
		if player['nickname'] in exclude_names:
			continue
		uids.append(uid)
		names.append(player['nickname'])

	idx = np.argsort(names)
	uids = np.array(uids)[idx]

	defaultdict_x2 = lambda fn: defaultdict(lambda: defaultdict(fn))

	duration = defaultdict_x2(lambda: 0)
	nwins = defaultdict_x2(lambda: 0)
	nlosses = defaultdict_x2(lambda: 0)
	scores = defaultdict_x2(lambda: [])
	best_path_im = defaultdict_x2(lambda: None)
	max_score = defaultdict_x2(lambda: 0)

	min_date = datetime(9999, 9, 9)
	max_date = datetime(1000, 1, 1)

	for i in range(len(uids)):
		uid = uids[i]
		print('Parsing log for:', data['player'][uid]['nickname'])
		for (date, text) in data['logs'][uid].items():
			print('Date:', date)
			date = date.split('T')[0].split('_')
			date = datetime(int(date[0]), int(date[1]), int(date[2]))
			if date < min_date:
				min_date = date
			if date > max_date:
				max_date = date
			log = parse_log(text)
			if log is not None:
				duration[uid][date] += log['duration']
				if log['win']: nwins[uid][date] += 1
				if log['loss']: nlosses[uid][date] += 1
				if log['score'] != -1: scores[uid][date].append(log['score'])
				if log['score'] > max_score[uid][date]:
					max_score[uid][date] = log['score']
					log = parse_log(text, True)
					best_path_im[uid][date] = log['path_im']

	nsubjects = len(uids)
	ndays = (max_date - min_date).days


	DURATION = 0
	NWINS = 1
	NLOSSES = 2
	MIN_SCORE = 3
	MED_SCORE = 4
	MAX_SCORE = 5

	ary = np.zeros((nsubjects, ndays, 6))

	for i in range(nsubjects):
		uid = uids[i]
		save_mosaic('best_path_%s.png' % data['player'][uid]['nickname'], best_path_im[uid])
		for day in range(ndays):
			date = min_date + timedelta(day)
			ary[i, day, DURATION] = duration[uid][date]
			ary[i, day, NWINS] = nwins[uid][date]
			ary[i, day, NLOSSES] = nlosses[uid][date]
			ary[i, day, MIN_SCORE] = np.min(scores[uid][date]) if len(scores[uid][date]) > 0 else 0
			ary[i, day, MED_SCORE] = np.median(scores[uid][date]) if len(scores[uid][date]) > 0 else 0
			ary[i, day, MAX_SCORE] = np.max(scores[uid][date]) if len(scores[uid][date]) > 0 else 0


	savemat('pamcor_log_parsing_results.mat', {'results': ary})

	ind = np.arange(ndays)
	fig, axes = plt.subplots(nsubjects, sharex=True)
	# DURATION
	for i in range(nsubjects):
		uid = uids[i]
		# plt.subplot(nsubjects, 1, i + 1)
		ax = axes[i]
		width = 0.35
		ans1 = ax.bar(ind, ary[i, :, DURATION].squeeze(), width, color='r')
		ax.set_ylabel('Seconds')
		ax.set_title('%s: Gameplay duration by date' % data['player'][uid]['nickname'])
		plt.xticks(ind + width,
			['%04d-%02d-%02d' % (y.year, y.month, y.day) for y in [min_date + timedelta(x) for x in range(ndays)]],
			rotation='vertical')

	# plt.show()
	fig.set_size_inches(2048/96., 1024/96.)
	plt.savefig('duration.png', bbox_inches='tight', dpi=96)

	fig, axes = plt.subplots(nsubjects, sharex=True)
	# WINS/LOSSES
	for i in range(nsubjects):
		uid = uids[i]
		# plt.subplot(nsubjects, 1, i + 1)
		ax = axes[i]
		width = 0.35
		win_bar = ax.bar(ind, ary[i, :, NWINS].squeeze(), width, color='g')
		loss_bar = ax.bar(ind + width, ary[i, :, NLOSSES].squeeze(), width, color='r')
		ax.set_ylabel('Count')
		ax.set_title('%s: Wins/Losses by date' % data['player'][uid]['nickname'])
		plt.xticks(ind + width,
			['%04d-%02d-%02d' % (y.year, y.month, y.day) for y in [min_date + timedelta(x) for x in range(ndays)]],
			rotation='vertical')

	# plt.show()
	fig.set_size_inches(2048/96., 1024/96.)
	plt.savefig('win_loss.png', bbox_inches='tight', dpi=96)

	fig, axes = plt.subplots(nsubjects, sharex=True)
	# SCORES
	for i in range(nsubjects):
		uid = uids[i]
		# plt.subplot(nsubjects, 1, i + 1)
		ax = axes[i]
		width = 0.35
		min_bar = ax.bar(ind - width, ary[i, :, MIN_SCORE].squeeze(), width, color='g')
		med_bar = ax.bar(ind, ary[i, :, MED_SCORE].squeeze(), width, color='y')
		max_bar = ax.bar(ind + width, ary[i, :, MAX_SCORE].squeeze(), width, color='r')
		ax.set_ylabel('Score')
		ax.set_title('%s: Min/Med/Max score by date' % data['player'][uid]['nickname'])
		plt.xticks(ind + width,
			['%04d-%02d-%02d' % (y.year, y.month, y.day) for y in [min_date + timedelta(x) for x in range(ndays)]],
			rotation='vertical')

	# plt.show()
	fig.set_size_inches(2048/96., 1024/96.)
	plt.savefig('scores.png', bbox_inches='tight', dpi=96)


def main():
	with open('data/pamcor-export.json') as f:
		data = json.loads(f.read())

	process_form_replies(data)
	process_play_time(data)


if __name__ == '__main__':
	main()
