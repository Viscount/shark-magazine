# shark-magazine
用于从单词列表中生成完整的资源包，包括查词、查例句、规范格式等功能。

## 安装
环境为Python 2.7.13，无需安装任何其他依赖

## 使用方法
1. 将单词表放入data文件夹
2. 修改config.py中对应参数的信息
3. 运行main.py

## 附：金山词霸接口返回数据说明

本项目中使用了金山词霸的接口进行查询，相关文档：[http://open.iciba.com/?c=wiki&t=cc](http://open.iciba.com/?c=wiki&t=cc)
返回的JSON数据格式如下：
```
JSON 字段解释(英文)
    {
        'word_name':'' #单词
        'exchange': '' #单词的各种时态
        'symbols':'' #单词各种信息 下面字段都是这个字段下面的
            'ph_en': '' #英式音标
            'ph_am': '' #美式音标
            'ph_en_mp3':'' #英式发音
            'ph_am_mp3': '' #美式发音
            'ph_tts_mp3': '' #TTS发音
            'parts':'' #词的各种意思
    }
```