import base64
import os
import shutil

import requests


BASE_URL = os.environ["BASE_URL"]
params = {
    "u": os.environ["USERNAME"],
    "t": os.environ["TOKEN"],
    "s": os.environ["SALT"],
    "v": "1.16.1",
    "c": "github-readme",
    "f": "json",
}
with open("template/now-playing.svg", "r") as f:
    template = f.read()


def _parse_track_info(track_info):
    return {
        "title": track_info["title"],
        "album": track_info["album"],
        "artist": track_info["artist"],
        "coverArt": track_info["coverArt"],
    }


def get_now_playing(params=params):
    r = requests.get(f"{BASE_URL}/rest/getNowPlaying", params=params).json()

    try:
        r = r["subsonic-response"]["nowPlaying"]["entry"][0]

        return _parse_track_info(r)
    except KeyError:
        return None


def get_random_albums(params=params):
    params["type"] = "random"
    params["size"] = 5

    r = requests.get(f"{BASE_URL}/rest/getAlbumList", params=params).json()
    r = r["subsonic-response"]["albumList"]["album"]

    return [_parse_track_info(i) for i in r]


def get_cover_art(covert_art_id: str, params=params):
    params["id"] = covert_art_id
    params["size"] = 48

    r = requests.get(f"{BASE_URL}/rest/getCoverArt", params=params)

    return base64.b64encode(r.content).decode("utf-8")


def _generate_svg(track_info, cover_art: str, out_filename: str, template=template):
    template = (
        template.replace("TITLE", track_info["title"].replace("&", "&amp;"))
        .replace("ARTIST", track_info["artist"].replace("&", "&amp;"))
        .replace("BASE64_IMAGE_STRING", cover_art)
    )

    with open(f"./output/{out_filename}.svg", "w") as f:
        f.write(template)


if __name__ == "__main__":
    ### now_playing
    if now_playing := get_now_playing():
        cover_art = get_cover_art(now_playing["coverArt"])
        _generate_svg(now_playing, cover_art, "now-playing")
    else:
        shutil.copy("template/now-playing-null.svg", "./output/now-playing.svg")

    ### random_songs
    random_songs = get_random_albums()
    for index, track_info in enumerate(random_songs):
        cover_art = get_cover_art(track_info["coverArt"])
        _generate_svg(track_info, cover_art, f"random-album-{index}")
