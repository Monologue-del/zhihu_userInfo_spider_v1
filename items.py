# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class UserInfoItem(scrapy.Item):
    """
    用户基本信息
    """
    id = Field()
    url_token = Field()
    url = Field()
    type = Field()
    name = Field()
    gender = Field()
    headline = Field()
    locations = Field()
    business = Field()
    employments = Field()
    educations = Field()
    description = Field()
    exp = Field()
    level = Field()
    identity = Field()
    best_answerer = Field()
    best_topics = Field()
    follower_count = Field()
    following_count = Field()
    answer_count = Field()
    question_count = Field()
    articles_count = Field()
    columns_count = Field()
    zvideo_count = Field()
    favorite_count = Field()
    favorited_count = Field()
    voteup_count = Field()
    thanked_count = Field()
    live_count = Field()
    hosted_live_count = Field()
    participated_live_count = Field()
    included_answers_count = Field()
    included_articles_count = Field()
    following_columns_count = Field()
    following_topic_count = Field()
    following_question_count = Field()
    following_favlists_count = Field()
    recognized_count = Field()
    crawl_time = scrapy.Field()


class UserActionItem(scrapy.Item):
    """
    用户动态
    """
    action_id = Field()
    actor_name = Field()
    actor_url = Field()
    action_text = Field()
    verb = Field()
    action_time = Field()
    target_excerpt = Field()
    target_created_time = Field()
    target_id = Field()
    target_url = Field()
    target_author_name = Field()
    target_author_url = Field()
    target_question_author_name = Field()
    target_question_author_url = Field()
    target_question_title = Field()
    target_question_url = Field()
    crawl_time = Field()