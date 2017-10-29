#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import urllib2
import logging
import json
import codecs
import os
import time
import sys
from config import config
import re
import string

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


# 去除句子标点
def wipe_punctuation(sentence):
    table = string.maketrans("", "")
    return sentence.translate(table, string.punctuation+"‘’“”")


# 匹配单词与例句
def mapping_sentence(word_list):
    word_sentence_dict = dict()
    sentenceEnders = re.compile('[.!?]')
    # 遍历每个文件
    for file in os.listdir(config["data_source_folder"]):
        with codecs.open(os.path.join(config["data_source_folder"], file), 'r') as f:
            lines = f.readlines()
        # 对每一行进行处理，切分出句子
        for line in lines:
            sentence_list = sentenceEnders.split(line)
            for raw_sentence in sentence_list:
                sentence = wipe_punctuation(raw_sentence.strip())
                if len(sentence) < 2:
                    continue
                word_set = set(sentence.split(' '))
                # 判断单词表中的词是否存在于句子中
                for word in word_list:
                    if word in word_set:
                        # 更新例句对应字典
                        if word in word_sentence_dict:
                            if len(raw_sentence) > word_sentence_dict[word]:
                                word_sentence_dict[word] = raw_sentence.strip()
                        else:
                            word_sentence_dict[word] = raw_sentence.strip()
    return word_sentence_dict


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
        file_writer.write("##### 例句\n")
        file_writer.write(">"+word_detail["sentence"]+"\n")
        file_writer.write("```\n")
        file_writer.write("//笔记区\n")
        file_writer.write("-\n")
        file_writer.write("-\n")
        file_writer.write("```\n")

if __name__ == "__main__":
    word_list = []
    with codecs.open(config["vocabulary_file_path"], 'r') as f:
        word_list = f.readlines()

    words = []
    for line in word_list:
        content = line.split(',')
        words.append(content[0].strip())
    word_sentence_dict = mapping_sentence(words)

    with codecs.open(config["output_file_name"], 'w', encoding="utf-8") as f:
        f.write("# " + config["outpuf_file_title"] + "\n")
        for line in word_list:
            content = line.split(',')
            word_detail = search_word(content[0].strip())
            word_detail["frequency"] = content[2].strip()
            if content[0].strip() in word_sentence_dict:
                word_detail["sentence"] = word_sentence_dict[content[0].strip()]
            else:
                word_detail["sentence"] = "暂无例句"
            if "word_name" in word_detail:
                format_word(f, word_detail)
            else:
                continue

