import scrapy
import json
import time
from bs4 import BeautifulSoup
from zhihu_user.items import UserInfoItem
from zhihu_user.items import UserActionItem
import datetime
from zhihu_user.settings import DATETIME_FORMAT, DATE_FORMAT


class ZhihuUserspiderSpider(scrapy.Spider):
    name = 'zhihu_userSpider'
    allowed_domains = ["www.zhihu.com", "api.zhihu.com"]
    # 起始用户id
    start_user = 'wangyizhi'
    # 用户信息的url
    user_url = 'https://api.zhihu.com/people/{user}'
    # 关注列表的url
    followees_url = "https://www.zhihu.com/people/{user}/following?page={page}"
    # 粉丝列表的url
    followers_url = 'https://www.zhihu.com/people/{user}/followers?page={page}'
    # 用户动态的url
    user_action_url = "https://www.zhihu.com/api/v3/moments/{user}/activities?"

    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user), headers={
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'},
                             callback=self.parse_user)
        time.sleep(1)

    def parse_user(self, response):
        """
        爬取用户基本信息；
        调用parse_followees和parse_followers爬取关注者和粉丝列表
        :param response:
        :return:
        """
        result = json.loads(response.text)
        # 提取用户基本信息
        userinfo_item = UserInfoItem()

        userinfo_item['id'] = result['id']
        userinfo_item['url_token'] = result['url_token']
        userinfo_item['url'] = result['url']
        userinfo_item['type'] = result['type']
        userinfo_item['name'] = result['name']
        userinfo_item['gender'] = result['gender']
        userinfo_item['headline'] = result['headline']
        try:
            userinfo_item['locations'] = []
            userinfo_item['locations'] = [location['name'] for location in result['location']]
            # userInfo_item['locations'] = []
            # for location in result['location']:
            #     userInfo_item['locations'].append(location['name'])
        except:
            userinfo_item['locations'] = ""
        userinfo_item['business'] = []
        userinfo_item['business'] = result['business'].get('name')
        try:
            userinfo_item['employments'] = []
            userinfo_item['employments'] = [(employment[0]['name'] + employment[1]['name']) for employment in
                                            result['employment']]
        except:
            userinfo_item['employments'] = ""
        try:
            userinfo_item['educations'] = []
            userinfo_item['educations'] = [education['name'] for education in result['education']]
        except:
            userinfo_item['educations'] = ""
        userinfo_item['description'] = result['description']
        userinfo_item['exp'] = result['level_info']['exp']
        userinfo_item['level'] = result['level_info']['level']
        try:
            userinfo_item['identity'] = []
            userinfo_item['best_answerer'] = []
            userinfo_item['best_topics'] = []
            for obj in result['badge']:
                if obj['type'] == "identity":
                    userinfo_item['identity'].append(obj['description'])
                if obj['type'] == "best_answerer":
                    userinfo_item['best_answerer'].append(obj['description'])
                    userinfo_item['best_topics'] = [topics['name'] for topics in obj['topics']]
        except:
            userinfo_item['identity'] = ""
            userinfo_item['best_answerer'] = ""
            userinfo_item['best_topics'] = ""
        userinfo_item['follower_count'] = result['follower_count']
        userinfo_item['following_count'] = result['following_count']
        userinfo_item['answer_count'] = result['answer_count']
        userinfo_item['question_count'] = result['question_count']
        userinfo_item['articles_count'] = result['articles_count']
        userinfo_item['columns_count'] = result['columns_count']
        userinfo_item['zvideo_count'] = result['zvideo_count']
        userinfo_item['favorite_count'] = result['favorite_count']
        userinfo_item['favorited_count'] = result['favorited_count']
        userinfo_item['voteup_count'] = result['voteup_count']
        userinfo_item['thanked_count'] = result['thanked_count']
        userinfo_item['live_count'] = result['live_count']
        userinfo_item['hosted_live_count'] = result['hosted_live_count']
        userinfo_item['participated_live_count'] = result['participated_live_count']
        userinfo_item['included_answers_count'] = result['included_answers_count']
        userinfo_item['included_articles_count'] = result['included_articles_count']
        userinfo_item['following_columns_count'] = result['following_columns_count']
        userinfo_item['following_topic_count'] = result['following_topic_count']
        userinfo_item['following_question_count'] = result['following_question_count']
        userinfo_item['following_favlists_count'] = result['following_favlists_count']
        userinfo_item['recognized_count'] = result['recognized_count']
        userinfo_item['crawl_time'] = datetime.datetime.now().strftime(DATETIME_FORMAT)

        yield userinfo_item

        # 判断关注者列表是否为空
        if result["following_count"] > 0:
            yield scrapy.Request(self.followees_url.format(user=result.get("url_token"), page=1),
                                 callback=self.parse_followees)
            time.sleep(1)

        # 判断粉丝列表是否为空
        if result["follower_count"] > 0:
            yield scrapy.Request(self.followers_url.format(user=result.get("url_token"), page=1),
                                 callback=self.parse_followers)
            time.sleep(1)

    def parse_action(self, response):
        """
        爬取用户动态
        :param response:
        :return:
        """
        action_json = json.loads(response.text)
        is_end = action_json['paging']['is_end']
        # 判断用户是否有动态
        if not is_end:
            next_url = action_json['paging']['next']

            # 提取用户动态
            for action in action_json['data']:
                useraction_item = UserActionItem()
                useraction_item['action_id'] = action['id']
                useraction_item['actor_name'] = action['actor']['name']
                useraction_item['actor_url'] = action['actor']['url']
                useraction_item['action_text'] = action['action_text']
                useraction_item['verb'] = action['verb']

                # 只爬取“赞同回答”、“回答问题”、“添加问题”、“关注问题”四种情形，其余情形跳过循环
                if useraction_item['verb'] == "ANSWER_VOTE_UP" or useraction_item['verb'] == "ANSWER_CREATE":
                    # “赞同回答”与“回答问题”的数据爬取方式相同，“问题提出者信息”+“问题信息”
                    # 内容的创作时间
                    useraction_item['target_created_time'] = datetime.datetime.fromtimestamp(
                        action['target']['created_time']).strftime(DATETIME_FORMAT)
                    useraction_item['target_question_author_name'] = action['target']['question']['author']['name']
                    useraction_item['target_question_author_url'] = action['target']['question']['author']['url']
                    useraction_item['target_question_title'] = action['target']['question']['title']
                    useraction_item['target_question_url'] = action['target']['question']['url']
                elif useraction_item['verb'] == "QUESTION_FOLLOW" or useraction_item['verb'] == "QUESTION_CREATE":
                    # “添加问题”与“关注问题”的数据爬取方式相同，target_question的信息=target本身
                    # 内容的创作时间
                    useraction_item['target_created_time'] = datetime.datetime.fromtimestamp(
                        action['target']['created']).strftime(DATETIME_FORMAT)
                    # target（问题）的信息就是target_question的信息
                    useraction_item['target_question_author_name'] = action['target']['author']['name']
                    useraction_item['target_question_author_url'] = action['target']['author']['url']
                    useraction_item['target_question_title'] = action['target']['title']
                    useraction_item['target_question_url'] = action['target']['url']
                else:
                    continue

                useraction_item['target_author_name'] = action['target']['author']['name']
                useraction_item['target_author_url'] = action['target']['author']['url']
                useraction_item['target_url'] = action['target']['url']
                # 动态的时间
                useraction_item['action_time'] = datetime.datetime.fromtimestamp(action['created_time']).strftime(
                    DATETIME_FORMAT)
                useraction_item['target_excerpt'] = action['target']['excerpt']
                useraction_item['target_id'] = action['target']['id']
                useraction_item['crawl_time'] = datetime.datetime.now().strftime(DATETIME_FORMAT)

                yield useraction_item

            if not is_end:
                yield scrapy.Request(next_url, callback=self.parse_action)

    def parse_followees(self, response):
        """
        解析关注者列表，得到用户url；
        调用parse_user爬取用户信息
        :param response:
        :return:
        """
        followees_list = response.xpath('//div[@class="List-item"]')
        for followee in followees_list:
            try:
                url_token = followee.xpath('./div/div/div[2]/h2//a/@href').extract_first()
                url_type = url_token.split('/')[-2]
                if str(url_type) == 'people':
                    user_token = url_token.split('/')[-1]
                    print(user_token)
                    yield scrapy.Request(self.user_url.format(user=user_token), callback=self.parse_user)
                    yield scrapy.Request(self.user_action_url.format(user=user_token), callback=self.parse_action)
                else:
                    continue
            except:
                continue

        zhihu_soup = BeautifulSoup(response.text, "lxml")
        page_current = zhihu_soup.find("button",
                                       class_="Button PaginationButton PaginationButton--current Button--plain")
        try:
            page_next = zhihu_soup.find("button", class_="Button PaginationButton PaginationButton-next Button--plain")
        except:
            page_next = None

        if not page_next == None:
            user = response.url.split('/')[-2]
            next_page = self.followees_url.format(
                user=user,
                page=str(int(page_current.text) + 1))
            # 获取下一页的地址然后通过yield继续返回Request请求，继续请求自己再次获取下页中的信息
            yield scrapy.Request(next_page, callback=self.parse_followers)

    def parse_followers(self, response):
        """
        爬取粉丝列表，得到用户url，调用parse_user爬取用户信息
        :param response:
        :return:
        """
        followers_list = response.xpath('//div[@class="List-item"]')
        for follower in followers_list:
            try:
                url_token = follower.xpath('./div/div/div[2]/h2//a/@href').extract_first()
                url_type = url_token.split('/')[-2]
                if str(url_type) == 'people':
                    user_token = url_token.split('/')[-1]
                    print(user_token)
                    yield scrapy.Request(self.user_url.format(user=user_token), callback=self.parse_user)
                    yield scrapy.Request(self.user_action_url.format(user=user_token), callback=self.parse_action)
                else:
                    continue
            except:
                continue

        zhihu_soup = BeautifulSoup(response.text, "lxml")
        page_current = zhihu_soup.find("button",
                                       class_="Button PaginationButton PaginationButton--current Button--plain")
        try:
            page_next = zhihu_soup.find("button", class_="Button PaginationButton PaginationButton-next Button--plain")
        except:
            page_next = None

        if not page_next == None:
            user = response.url.split('/')[-2]
            next_page = self.followers_url.format(
                user=user,
                page=str(int(page_current.text) + 1))
            # 获取下一页的地址然后通过yield继续返回Request请求，继续请求自己再次获取下页中的信息
            yield scrapy.Request(next_page, self.parse_followers)
