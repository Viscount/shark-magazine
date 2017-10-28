#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import codecs


if __name__ == "__main__":
    content = []
    with codecs.open("CET6.txt", 'r') as f:
        for line in f.readlines():
            format_line = line.strip(' \n\xe3\x80').split(" ")
            if len(format_line) < 2:
                continue
            content.append(format_line[0]+"\n")
    with codecs.open("CET6-re.txt", 'w') as file:
        file.writelines(content)
