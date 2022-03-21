# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor

import json
import random
import re


class WeiXinMPVideoIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?mp\.weixin\.qq\.com/s/(?P<id>[^/?#&]+)'
    _TEST = {
        'url': 'https://mp.weixin.qq.com/s/VEAgEYqEpM7HL99RK4XAxQ',
        'md5': '2874f05c144374831caa6818fce4005e',  # 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': 'VEAgEYqEpM7HL99RK4XAxQ',
            'ext': 'mp4',
            'title': 'Video title goes here',
            # 'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # TODO more code goes here, for example ...
        # title = self._html_search_regex(r'<meta property="twitter:title" content="(.*?)"', webpage, 'title')
        try:
            vid = self._html_search_regex(r'<iframe.*?data-mpvid="(.*?)"', webpage, 'vid')
        except:
            print("Search Vid in another way...")
            vid = self._html_search_regex(r"""'(wxv_\d+)'""", webpage, 'vid')

        title = self._og_search_title(webpage)
        play_url_info = self._download_json(
            'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_play_url&preview=0&vid=%s' % (vid,),
            video_id, note='Downloading video info page')
        formats_arr = None
        if 'url_info' in play_url_info:
            formats_arr = play_url_info['url_info']
        return {
            'id': video_id,
            'title': title,
            'description': self._og_search_description(webpage),
            #'uploader': self._og_search_property('article:author', webpage), #self._search_regex(r'<div[^>]+id="uploader"[^>]*>([^<]+)<', webpage, 'uploader', fatal=False),
            # TODO more properties (see youtube_dl/extractor/common.py)
            'formats':formats_arr#[{'url':'https://mpvideo.qpic.cn/0bc3waaaoaaakiaipv7bcnqvbmgda6yaabya.f10002.mp4?dis_k=3950381ba909e4f46718d0aabaf8178d&dis_t=1642245194&vid=wxv_2224260817737285633&format_id=10002&support_redirect=0&mmversion=false','ext':'mp4'}],
        }
"""
from ..compat import (
    compat_parse_qs,
    compat_str,
)
from ..utils import (
    js_to_json,
    strip_jsonp,
    urlencode_postdata,
)


class WeiboIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?weibo\.com/[0-9]+/(?P<id>[a-zA-Z0-9]+)'
    _TEST = {
        'url': 'https://weibo.com/6275294458/Fp6RGfbff?type=comment',
        'info_dict': {
            'id': 'Fp6RGfbff',
            'ext': 'mp4',
            'title': 'You should have servants to massage you,... 来自Hosico_猫 - 微博',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # to get Referer url for genvisitor
        webpage, urlh = self._download_webpage_handle(url, video_id)

        visitor_url = urlh.geturl()

        if 'passport.weibo.com' in visitor_url:
            # first visit
            visitor_data = self._download_json(
                'https://passport.weibo.com/visitor/genvisitor', video_id,
                note='Generating first-visit data',
                transform_source=strip_jsonp,
                headers={'Referer': visitor_url},
                data=urlencode_postdata({
                    'cb': 'gen_callback',
                    'fp': json.dumps({
                        'os': '2',
                        'browser': 'Gecko57,0,0,0',
                        'fonts': 'undefined',
                        'screenInfo': '1440*900*24',
                        'plugins': '',
                    }),
                }))

            tid = visitor_data['data']['tid']
            cnfd = '%03d' % visitor_data['data']['confidence']

            self._download_webpage(
                'https://passport.weibo.com/visitor/visitor', video_id,
                note='Running first-visit callback',
                query={
                    'a': 'incarnate',
                    't': tid,
                    'w': 2,
                    'c': cnfd,
                    'cb': 'cross_domain',
                    'from': 'weibo',
                    '_rand': random.random(),
                })

            webpage = self._download_webpage(
                url, video_id, note='Revisiting webpage')

        title = self._html_search_regex(
            r'<title>(.+?)</title>', webpage, 'title')

        video_formats = compat_parse_qs(self._search_regex(
            r'video-sources=\\\"(.+?)\"', webpage, 'video_sources'))

        formats = []
        supported_resolutions = (480, 720)
        for res in supported_resolutions:
            vid_urls = video_formats.get(compat_str(res))
            if not vid_urls or not isinstance(vid_urls, list):
                continue

            vid_url = vid_urls[0]
            formats.append({
                'url': vid_url,
                'height': res,
            })

        self._sort_formats(formats)

        uploader = self._og_search_property(
            'nick-name', webpage, 'uploader', default=None)

        return {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'formats': formats
        }


class WeiboMobileIE(InfoExtractor):
    _VALID_URL = r'https?://m\.weibo\.cn/status/(?P<id>[0-9]+)(\?.+)?'
    _TEST = {
        'url': 'https://m.weibo.cn/status/4189191225395228?wm=3333_2001&sourcetype=weixin&featurecode=newtitle&from=singlemessage&isappinstalled=0',
        'info_dict': {
            'id': '4189191225395228',
            'ext': 'mp4',
            'title': '午睡当然是要甜甜蜜蜜的啦',
            'uploader': '柴犬柴犬'
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # to get Referer url for genvisitor
        webpage = self._download_webpage(url, video_id, note='visit the page')

        weibo_info = self._parse_json(self._search_regex(
            r'var\s+\$render_data\s*=\s*\[({.*})\]\[0\]\s*\|\|\s*{};',
            webpage, 'js_code', flags=re.DOTALL),
            video_id, transform_source=js_to_json)

        status_data = weibo_info.get('status', {})
        page_info = status_data.get('page_info')
        title = status_data['status_title']
        uploader = status_data.get('user', {}).get('screen_name')

        return {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'url': page_info['media_info']['stream_url']
        }
"""