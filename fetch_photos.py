import vk_auth
import json
import urllib2
from urllib import urlencode
import json
import os
import os.path
import getpass
import sys

def call_api(method, params, token):
    if isinstance(params, list):
        params_list = [kv for kv in params]
    elif isinstance(params, dict):
        params_list = params.items()
    else:
        params_list = [params]
    params_list.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params_list)) 
    return json.loads(urllib2.urlopen(url).read())["response"]

def get_albums(user_id, token):
    return call_api("photos.getAlbums", ("uid", user_id), token)

def get_photos_urls(user_id, album_id, token):
    photos_list = call_api("photos.get", [("uid", user_id), ("aid", album_id)], token)
    result = []
    for photo in photos_list:
        #Choose photo with largest resolution
        if "src_xxbig" in photo:
            url = photo["src_xxbig"]
        elif "src_xbig" in photo:
            url = photo["src_xbig"]
        else:
            url = photo["src_big"]
        result.append(url)
    return result

def save_photos(urls, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    names_pattern = "%%0%dd.jpg" % len(str(len(urls)))
    for num, url in enumerate(urls):
        filename = os.path.join(directory, names_pattern % (num + 1))
        print "Downloading %s" % filename
        open(filename, "w").write(urllib2.urlopen(url).read())

if len(sys.argv) != 2:
   print "Usage: %s destination" % sys.argv[0]
   sys.exit(1)

directory = sys.argv[1]
email = raw_input("Email: ")
password = getpass.getpass()
token, user_id = vk_auth.auth(email, password, "2951857", "photos")
albums = get_albums(user_id, token)
print "\n".join("%d. %s" % (num + 1, album["title"]) for num, album in enumerate(albums))
choise = -1
while choise not in xrange(len(albums)):
    choise = int(raw_input("Choose album number: ")) - 1
photos_urls = get_photos_urls(user_id, albums[choise]["aid"], token)
save_photos(photos_urls, directory)
