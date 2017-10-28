#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import urllib2
import logging
import json
import codecs
import os
import time
import sys

logger = logging.getLogger("logger")

reload(sys)
sys.setdefaultencoding("utf-8")


# 发起请求
def request_api(url):
    try:
        time.sleep(1)
        logger.info("Requesting url: " + url)
        response = urllib2.urlopen(url, timeout=10)
        logger.info("Response: " + str(response.code))
        return response.read()
    except Exception as e:
        print type(e), e


# 查词功能
def search_word(word):
    parameters = {
        "w": word,
        "type": 'json',
        "key": '1A31B2EAF9F46AD6A631204EFE7DBF7C'
    }
    web_dict_url = "http://dict-co.iciba.com/api/dictionary.php?"
    para_string = "&".join(key + "=" + str(parameters[key]) for key in parameters)
    raw_content = request_api(web_dict_url + para_string)
    result_dict = json.loads(raw_content)
    return result_dict


# 格式化输出到文件
def format_word(file_writer, word_detail):
    file_writer.write("### " + word_detail["word_name"] + '\n')
    for symbol in word_detail["symbols"]:
        if "ph_en" in symbol and symbol["ph_en"] is not None:
            file_writer.write("**英音** " + '/' + symbol["ph_en"] + '/ ')
        if "ph_am" in symbol and symbol["ph_am"] is not None:
            file_writer.write("**美音** " + '/' + symbol["ph_am"] + '/ ')
        file_writer.write("**词频**: 前 " + word_detail["frequency"] + '%  \n')
        file_writer.write("##### 释义\n")
        for part in symbol["parts"]:
            meaning = ";".join(mean for mean in part["means"])
            file_writer.write("- " + part["part"] + meaning + '\n')


if __name__ == "__main__":
    # JSON 字段解释(英文)
    # {
    #     'word_name':'' #单词
    #     'exchange': '' #单词的各种时态
    #     'symbols':'' #单词各种信息 下面字段都是这个字段下面的
    #         'ph_en': '' #英式音标
    #         'ph_am': '' #美式音标
    #         'ph_en_mp3':'' #英式发音
    #         'ph_am_mp3': '' #美式发音
    #         'ph_tts_mp3': '' #TTS发音
    #         'parts':'' #词的各种意思
    # }

    word_list = []
    with codecs.open(os.path.join("data", "other-1587-80%-去cet6.csv"), 'r') as f:
        word_list = f.readlines()

    with codecs.open("Economist.md", 'w', encoding="utf-8") as f:
        f.write("# Economist Word List\n")
        for line in word_list:
            content = line.split(',')
            word_detail = search_word(content[0].strip())
            word_detail["frequency"] = content[2].strip()
            if "word_name" in word_detail:
                format_word(f, word_detail)
            else:
                continue

