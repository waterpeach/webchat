# -*- coding:utf8 -*-
import time
from flask import Flask, request, make_response, render_template
import hashlib
import xml.etree.ElementTree as xmlET
import function
from WXBizMsgCrypt import WXBizMsgCrypt
app = Flask(__name__)
app.secret_key = 's3cr3t'
token = 'xxxxxxxxxxx'
encodingAESKey = "g8GOIrBU1tQV3ffEeRCT6XQmFles5gPE4v3m2P41nTm"
appid = "wx655f65e156f0267e"
AppSecret = "bd2a709f79131738da4d342d1ac3d810"
encryp_test = WXBizMsgCrypt(token, encodingAESKey, appid)


@app.route('/', methods=['GET', 'POST'])
def wechat_auth():
    if request.method == 'GET':
        query = request.args  # GET 方法附上的参数
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')
        s = sorted([timestamp, nonce, token])
        s = ''.join(s)
        if hashlib.sha1(s).hexdigest() == signature:
            return make_response(echostr)
        else:
            return "False"
    if request.method == "POST":
        text = request.data
        params = request.args
        timestamp = params.get("timestamp")
        msg_sign = params.get("msg_signature")
        nonce = params.get("nonce")
        ret, xml = encryp_test.DecryptMsg(text, msg_sign, timestamp, nonce)
        if ret != 0:
            return "False"
        xml_recv = xmlET.fromstring(xml)
        msg_type = xml_recv.find("MsgType").text
        from_user = xml_recv.find("FromUserName").text
        to_user = xml_recv.find("ToUserName").text
        if msg_type == 'text':
            content = xml_recv.find("Content").text
            program = function.Program(
                touser=to_user,
                fromuser=from_user,
                content=content)
            response_type, message = program.type_text()
            if response_type == "text":
                to_xml = render_template(
                    "reply_text.xml",
                    fromUser=to_user,
                    toUser=from_user,
                    CreateTime=(
                        time.time()),
                    content=message,
                    msgType='text')
                return return_xml(function.change_utf(to_xml), nonce)
            if response_type == "music":
                song_name = message[0]
                song_singer = message[1]
                song_url = message[2]
                to_xml = render_template(
                    "reply_music.xml",
                    fromUser=to_user,
                    toUser=from_user,
                    createTime=(
                        time.time()),
                    msgType='music',
                    TITLE=song_name,
                    DESCRIPTION=song_singer,
                    MUSIC_Url=song_url,
                    HQ_MUSIC_Url=song_url)
                return return_xml(function.change_utf(to_xml), nonce)
        elif msg_type == "location":
            program = function.Program(
                touser=to_user, fromuser=from_user, content=None)
            label = xml_recv.find("Label").text
            message = program.type_location(label)
            to_xml = render_template(
                "reply_text.xml",
                fromUser=to_user,
                toUser=from_user,
                CreateTime=(
                    time.time()),
                content=message,
                msgType="text")
            return return_xml(function.change_utf(to_xml), nonce)
        elif msg_type == "event" and xml_recv.find("Event").text == "subscribe":
            message = u"感谢关注本公众号，本公众号暂时只做功能测试。\n" \
                      u"目前实现文本消息原文返回，定位消息返回天气查询\n" \
                      u"发送\"天气洛阳、洛阳的天气、洛阳 天气、洛阳天气\"等信息可回复该地天气情况\n" \
                      u"发送\"点歌 歌名，歌手\"可以点歌,逗号中英文都可以。\n" \
                      u"发送\"笑话\"，\"冷笑话\"可以随机发送近期糗百的热点笑话"

            to_xml = render_template(
                "reply_text.xml",
                fromUser=to_user,
                toUser=from_user,
                CreateTime=(
                    time.time()),
                content=message,
                msgType="text")
            return return_xml(function.change_utf(to_xml), nonce)
        elif msg_type == "event" and xml_recv.find("Event").text == "ENTER":
            message = u"打开对话"
            to_xml = render_template(
                "reply_text.xml",
                fromUser=to_user,
                toUser=from_user,
                CreateTime=(
                    time.time()),
                content=message,
                msgType="text")
            return return_xml(function.change_utf(to_xml), nonce)
        elif msg_type == "image" or msg_type == "voice":
            xml_filename = "reply_%s.xml" % msg_type
            media_id = xml_recv.find("MediaId").text
            to_xml = render_template(
                xml_filename,
                fromUser=to_user,
                toUser=from_user,
                createTime=(
                    time.time()),
                media_id=media_id,
                msgType=msg_type,
                title="a",
                description="a")
            return return_xml(function.change_utf(to_xml), nonce)
        elif msg_type == "video" or msg_type == "shortvideo":
            media_id = xml_recv.find("MediaId").text
            xml_filename = "reply_video.xml"
            to_xml = render_template(
                xml_filename,
                fromUser=to_user,
                toUser=from_user,
                createTime=(
                    time.time()),
                media_id=media_id,
                msgType="video")
            return return_xml(function.change_utf(to_xml), nonce)
        else:
            # print xml
            # text = xml.replace(fromUser,"%s")
            # text=text.replace(toUser,"%s")
            # text=text.replace(timestamp,str(time.time()))
            #
            # to_xml = text%(fromUser,toUser)
            # print to_xml
            message = u"该类型服务暂时未部署。" \
                      u"目前实现文本消息原文返回，定位消息返回天气查询\n" \
                      u"发送\"天气洛阳、洛阳的天气、洛阳 天气、洛阳天气\"等信息可回复该地天气情况\n" \
                      u"发送\"点歌 歌名，歌手\"可以点歌,逗号中英文都可以。\n" \
                      u"发送\"笑话\"，\"冷笑话\"可以随机发送近期糗百的热点笑话"
            to_xml = render_template(
                "reply_text.xml",
                fromUser=to_user,
                toUser=from_user,
                CreateTime=(
                    time.time()),
                content=message,
                msgType="text")
            return return_xml(function.change_utf(to_xml), nonce)


@app.route('/test', methods=['GET', 'POST'])
def test_index():
    program = function.Program(
        touser="a",
        fromuser="b",
        content=u"笑话")
    text, message = program.type_text()
    return function.change_utf(message)


def return_xml(to_xml, nonce):
    ret, encrypt_xml = encryp_test.EncryptMsg(to_xml, nonce)
    if ret == 0:
        return encrypt_xml
    else:
        return "False"


if __name__ == "__main__":
    app.run()
