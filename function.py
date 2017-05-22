# -*- coding: utf-8 -*-
import requests
from xml.etree import ElementTree
import json
import re
import sys
import random


def change_un(input_data):
    if isinstance(input_data, unicode):
        return input_data
    if isinstance(input_data, str):
        try:
            a = input_data.decode("gbk")
            return a
        except UnicodeDecodeError:
            a = input_data.decode("utf-8")
            return a
    return unicode(input_data)


def change_utf(input_data):
    if isinstance(input_data, unicode):
        return input_data.encode("utf-8")
    if isinstance(input_data, str):
        try:
            a = input_data.decode("gbk")
            return a.encode("utf-8")
        except UnicodeDecodeError:
            return input_data
    else:
        return str(input_data)


def get_city_id():
    try:
        xml_recv = ElementTree.parse("CityID.xml")
    except IOError:
        path = sys.path[0]
        xml_recv = ElementTree.parse(path + "\\CityID.xml")
    root = xml_recv.getroot()
    city_dict = {}
    for province_of_root in root:
        for city in province_of_root:
            for town in city:
                dic = town.attrib
                city_dict[change_un(dic["name"])] = dic["weatherCode"]
    return city_dict


def get_joke(num, joke_list):
    url = r"https://www.qiushibaike.com/hot/page/%s" % num
    s = requests.get(url)
    text = s.content
    p = "<span>.*</span>"
    lis = re.findall(p, text)
    for i in range(0, len(lis) - 7):
        str_temp = lis[i]
        str_temp = str_temp[6:-7]
        str_temp = str_temp.replace("<br/>", "")
        if "img" in str_temp or "src" in str_temp or "alt" in str_temp or "<h1>" in str_temp or len(
                str_temp) < 40:
            pass
        else:
            if str_temp not in joke_list:
                joke_list.append(str_temp)


def get_joke_list():
    import time
    global joke
    global joke_list
    joke_list = []
    while True:
        for i in range(1, 50):
            get_joke(str(i), joke_list)
            time.sleep(2)
        joke = joke_list[:]
        time.sleep(43200)


def get_data_run():
    import threading
    joke = threading.Thread(target=get_joke_list)
    joke.start()


city_id_dict = get_city_id()
get_data_run()


def get_key():
    get_key_url = "http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?" \
        "json=3&loginUin=530168033&format=jsonp&inCharset=GB2312&" \
        "outCharset=GB2312&notice=0&platform=yqq&needNewCode=0"
    r = requests.get(get_key_url)
    json_str = r.content.strip("jsonCallback(").strip(");")
    dic = json.loads(json_str)
    key = dic.get("key")
    return key


class Program:
    def __init__(self, touser, fromuser, content):
        self.touser = touser
        self.fromuser = fromuser
        self.content = change_un(content)
        self.city_id_dict = get_city_id()

    def type_text(self):
        text = self.content
        if u"天气" in text:
            text = text.strip(u"天气")
            text = text.strip()
            if u"的" in text:
                text = text.strip(u"的")
            if u"地" in text:
                text = text.strip(u"的")
            if u"得" in text:
                text = text.strip(u"的")
            city_id = self.city_id_dict.get(text, None)
            if city_id is None:
                return "text", u"请检查您的输入是否有误。"
            weather_content = text + "\n" + get_weather(city_id)
            return "text", weather_content
        if u"点歌" in text:
            if u"点歌" == text:
                message = u"点歌的话，\n请输入 ‘点歌 歌名,歌手’ ，\n中间逗号可以为中文或者英文。"
                return "text", message
            song_text = text.strip(u"点歌")
            song_text = song_text.strip()
            if u"," in song_text:
                song_list = song_text.split(u",")
            elif u"，" in song_text:
                song_list = song_text.split(u"，")
            else:
                return "text", u"输入有误。"
            song_name = song_list[0]
            song_singer = song_list[1]
            song_message = get_song(song_name, song_singer)
            if song_message is None:
                message = u"歌曲信息未找到，换一首试试看。"
                return "text", message
            song_url = song_message[0]
            return "music", [song_name, song_singer, song_url]
        if u"笑话" in text:
            joke_len = len(joke)
            k = 0
            message = ""
            while k == 0:
                num = random.randint(0, joke_len - 1)
                message = joke[num]
                if message != "\n":
                    k = 1
            return "text", message
        else:
            return "text", text

    def type_location(self, label):
        text = change_un(label)
        num = text.find(u"市")
        city = text[:num]
        text_1 = text[num + 1:]
        if u"县" in text_1:
            num2 = text_1.find(u"县")
            town = text_1[:num2]
            if len(town) == 1:
                town += u"县"
            town_id = self.city_id_dict.get(town, None)
            if town_id is not None:
                message = town + "\n" + get_weather(town_id)
                return message
        if u"市" in text_1:
            num2 = text_1.find(u"市")
            town = text_1[:num2]
            if len(town) == 1:
                town += u"市"
            town_id = self.city_id_dict.get(town, None)
            if town_id is not None:
                message = town + "\n" + get_weather(town_id)
                return message
        else:
            city_id = self.city_id_dict.get(city, None)
            if city_id is None:
                return u"信息有误。"
            else:
                weather_message = city + "\n" + get_weather(city_id)
                return weather_message


def get_life_index(text):
    text = text.split("\n")
    project = text[1].strip("<em>").strip("</em>")
    index = text[0].strip("<span>").strip("</span>")
    advice = text[2].strip("<p>").strip("</p>")
    message = "\n" + project + ":" + "\n" + index + "\n" + advice
    return message


def get_weather(city_id):
    import re
    url = "http://www.weather.com.cn/weather1d/%s.shtml" % city_id
    r = requests.get(url)
    shtml = r.content
    weather_pattern = "<input.type=\"hidden\".id=\"hidden_title\".value=.* />"
    weather_html = re.findall(weather_pattern, shtml)[0]
    weather_value = re.findall("value=.*", weather_html)[0]
    weather = weather_value.split("=")[-1].strip("/>")
    weather = weather.strip("\"")
    weather = weather.rstrip("\" ")

    half_day_pattern = "<h1>.*日.*</h1>"
    half_day_list = re.findall(half_day_pattern, shtml)
    half_day_list = [i.strip("<h1>").strip("</h1>") for i in half_day_list]
    half_day_wea_pattern = "<p class=\"wea\" title=.*>.*</p>"
    half_day_wea_html = re.findall(half_day_wea_pattern, shtml)
    half_day_wea_list = []
    for value in half_day_wea_html:
        wea_html = re.findall(">.*<", value)[0]
        wae_value = wea_html.strip(">").strip("<")
        half_day_wea_list.append(wae_value)
    half_day_temp_pattern = "<span>.*</span><em>°C</em>"
    half_day_temp_html = re.findall(half_day_temp_pattern, shtml)
    half_day_temp_list = []
    for value in half_day_temp_html:
        temp = value.strip("<span>")
        temp = temp.replace("</span><em>", " ")
        temp = temp.strip("</em>")
        half_day_temp_list.append(temp)
    half_day_wind_pattern = "<span class=\"\" title=.*>.*</span>"
    half_day_wind_html = re.findall(half_day_wind_pattern, shtml)
    half_day_wind_list = []
    for value in half_day_wind_html:
        wind_html = re.findall("\"\S*\">.*<", value)[0]
        wind_list = wind_html.strip("<").split(">")
        wind = wind_list[0].strip("\"") + "," + wind_list[1]
        half_day_wind_list.append(wind)
    half_day_sun_pattern = "<span>日.*</span>"
    half_day_sun_html = re.findall(half_day_sun_pattern, shtml)
    half_day_sun_list = [i.strip("<span>").strip("</span>")
                         for i in half_day_sun_html]

    life_index_pattern = "<span>.*</span>[.\n]<em>.*</em>[.\n]<p>.*</p>"
    life_index_html = re.findall(life_index_pattern, shtml)
    life_index_message = ""
    for value in life_index_html:
        message = get_life_index(value)
        life_index_message += message
    half_day_message_list = []
    for num in range(2):
        temp_message = half_day_list[num] + "\n" + half_day_wea_list[num] + "\n" + \
            half_day_temp_list[num] + "\n" + half_day_wind_list[num] + "\n" + half_day_sun_list[num]
        half_day_message_list.append(temp_message)
    weather_message = weather + "\n" + \
        half_day_message_list[0] + "\n\n" + half_day_message_list[1] + "\n" + life_index_message
    return weather_message


def get_song(song_name, song_singer):
    url = "http://s.music.qq.com/fcgi-bin/music_search_new_platform?t=0&n=50&aggr=1&" \
          "cr=1&loginUin=530168033&format=json&inCharset=GB2312&outCharset=utf-8&notice=0&" \
          "platform=jqminiframe.json&needNewCode=0&p=1&catZhida=0&" \
          "remoteplace=sizer.newclient.next_song&w=%s" % song_name
    r = requests.get(url)
    text = r.content
    r_dict = json.loads(text)
    data = r_dict.get("data", None)
    if data is None:
        return None

    song = data.get("song", None)
    if song is None:
        return None

    song_list = song.get("list", None)
    if song_list is None:
        return None
    for text in song_list:
        song_text = text.get("f", None)
        if song_text is None:
            return None
        per_song_list = song_text.split("|")
        per_song_singer = per_song_list[3]
        if per_song_singer == song_singer:
            song_id = per_song_list[-5]
            img_id = per_song_list[-3]
            music_key = get_key()
            song_api = r"http://cc.stream.qqmusic.qq.com/C100%s.m4a?vkey=%s&fromtag=0" % (
                song_id, music_key)
            image_api = r"http://imgcache.qq.com/music/photo/mid_album_90/%s/%s/%s.jpg" % (
                img_id[-2], img_id[-1], img_id)
            return [song_api, image_api]
    return None
