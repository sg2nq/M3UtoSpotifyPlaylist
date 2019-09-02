# Siddhant Goel
# Tool to convert m3u playlist to a spotify playlist for people who don't want to give edit access to their spotify profile to internet tools
# Create your own Spotify API access token, and keep all access rights reserved to yourself
# To obtain Spotify API access token go to https://developer.spotify.com/console/get-current-user/

import os, re, requests, json, argparse


def get_user_info(args):
	req_Headers = {
		"Accept": "application/json",
		"Authorization": "Bearer " + args.auth
	}
	result = requests.get(url='https://api.spotify.com/v1/me', headers=req_Headers)
	return result.json()['id']


def create_playlist(args, user_id):
	post_req_Headers = {
		"Accept": "application/json",
		"Authorization": "Bearer " + args.auth
	}

	playlist_URL = "https://api.spotify.com/v1/users/" + user_id + "/playlists"
	playlist_DATA = {
		'name': args.pl_name,
		'public': 'false'
	}

	create_playlist_result = requests.post(url=playlist_URL, data=json.dumps(playlist_DATA), headers=post_req_Headers)
	print("------Empty Playlist Created------")
	print("Playlist details(raw):")
	print(create_playlist_result, )
	print(json.dumps(create_playlist_result.json(), indent=4))

	return create_playlist_result.json()['id']


def parse_m3u(args):
	"""
	I recommend modifying this function to meet the needs of your playlist, based on whether
	it is a plain text list or an m3u.
	"""
	file = os.path.join(args.file_location)

	f = open(file, 'r')
	f.readline()
	line = f.readline()
	song_list = []

	while line:
		if line:
			song = line[line.find(',') + 1:]
			song = song.replace('-', ' ')
			song = re.sub(r" ?\([^)]+\)", "", song)
			song = re.sub(r" ?\[[^)]+\]", "", song)
			if 'feat' in song:
				song = song.split('feat')[0]
			if 'ft' in song:
				song = song.split('ft')[0]
			song = ' '.join(song.split())
			song_list.append(song)
		f.readline()
		line = f.readline()

	print("------M3u parsed------")
	print("Number of songs:", len(song_list))
	print("List of searches that will be made:")
	for song in song_list:
		print(song)
	return song_list


def populate_playlist(args, playlist_id, song_list):
	req_Headers = {
		"Authorization": "Bearer " + args.auth
	}
	search_URL = 'https://api.spotify.com/v1/search'
	add_tracks_URL = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
	fail_list = []
	print('------Adding songs------')
	for song in song_list:
		search_PARAMS = {'q': song, 'type': 'track'}

		result = requests.get(url=search_URL, params=search_PARAMS, headers=req_Headers)
		if len(result.json()['tracks']['items']) == 0:
			fail_list.append(song)
			continue
		track_name = result.json()['tracks']['items'][0]['name']
		trackURI = str(result.json()['tracks']['items'][0]['uri'])
		track_PARAMS = {'uris': trackURI}
		add_track_result = requests.post(url=add_tracks_URL, params=track_PARAMS, headers=req_Headers)
		if(add_track_result.status_code == 201):
			print("Success:", song, "added as", track_name)
	print("------The following songs failed to be found------")
	for song in fail_list:
		print(song)

def get_arguments():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--auth', type=str, required=True,
					help='Authorization token from Spotify. Can be obtained at https://developer.spotify.com/console/get-current-user/')
	parser.add_argument('--pl_name', type=str, required=True,
					help='Name of the playlist to be created')

	parser.add_argument('--file_location', type=str, required=True,
					help='Location of the m3u playlist file')

	return parser.parse_args()


def main():
	print("------------------------")
	args = get_arguments()
	user_id = get_user_info(args)
	playlist_id = create_playlist(args, user_id)
	song_list = parse_m3u(args)
	populate_playlist(args, playlist_id, song_list)


if __name__ == '__main__':
	main()



