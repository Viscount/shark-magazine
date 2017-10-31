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
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from urllib2 import URLError
from socket import timeout
from ssl import SSLError

logger = logging.getLogger("logger")

reload(sys)
sys.setdefaultencoding("utf-8")


# 发起请求
@retry(retry=retry_if_exception_type(URLError) | retry_if_exception_type(timeout) | retry_if_exception_type(SSLError),
       stop=stop_after_attempt(3), wait=wait_fixed(1))
def request_api(url):
    try:
        time.sleep(0.5)
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


# 重新排序
def shuffle_words(lines):
    new_lines = []
    index = 0
    back_index = len(lines)-1
    while True:
        flag = False
        for count in range(0, 5):
            new_lines.append(lines[index])
            index += 1
            if index >= back_index:
                flag = True
                break
        if flag:
            break
        for count in range(0, 5):
            new_lines.append(lines[back_index])
            back_index -= 1
            if back_index <= index:
                flag = True
                break
        if flag:
            break
    return new_lines


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
    if os.path.exists(os.path.join(config["local_dictionary"], word + ".json")):
        with codecs.open(os.path.join(config["local_dictionary"], word + ".json"), 'r') as f:
            lines = f.readlines()
        content = "".join(lines)
        result_dict = json.loads(content)
        return result_dict
    parameters = {
        "w": word,
        "type": 'json',
        "key": '1A31B2EAF9F46AD6A631204EFE7DBF7C'
    }
    web_dict_url = "http://dict-co.iciba.com/api/dictionary.php?"
    para_string = "&".join(key + "=" + str(parameters[key]) for key in parameters)
    raw_content = request_api(web_dict_url + para_string)
    with codecs.open(os.path.join(config["local_dictionary"], word + ".json"), 'w') as f:
        f.write(raw_content)
    result_dict = json.loads(raw_content)
    return result_dict


# 格式化输出到文件
def format_word(file_writer, word_detail):
    file_writer.write("### " + word_detail["word_name"] + '\n')
    file_writer.write("\n")
    for symbol in word_detail["symbols"]:
        if "ph_en" in symbol and symbol["ph_en"] is not None:
            file_writer.write("**英音** " + '/' + symbol["ph_en"] + '/ ')
        if "ph_am" in symbol and symbol["ph_am"] is not None:
            file_writer.write("**美音** " + '/' + symbol["ph_am"] + '/ ')
        file_writer.write("**词频**: 前 " + word_detail["frequency"] + '%  \n')
        file_writer.write("\n")
        file_writer.write("##### 释义\n")
        file_writer.write("\n")
        for part in symbol["parts"]:
            meaning = ";".join(mean for mean in part["means"])
            file_writer.write("- " + part["part"] + meaning + '\n')
        file_writer.write("\n")
        file_writer.write("##### 例句\n")
        file_writer.write("\n")
        file_writer.write(">"+word_detail["sentence"]+"\n")
        file_writer.write("```\n")
        file_writer.write("//笔记区\n")
        file_writer.write("*\n")
        file_writer.write("*\n")
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

    word_list = shuffle_words(word_list)

    with codecs.open(config["output_file_name"], 'w', encoding="utf-8") as f:
        f.write("# " + config["outpuf_file_title"] + "\n")
        f.write("## Section 1\n")
        count = 0
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
                count += 1
                if count % 10 == 0:
                    f.write("***\n")
                    f.write("## Section " + str(count / 10 + 1) + "\n")
            else:
                continue

