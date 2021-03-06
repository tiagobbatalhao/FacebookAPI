import credentials
import time
from datetime import datetime
from datetime import timedelta
import json
import facebook
import sys

post_fields = [
    'id',
    'admin_creator',
    'caption',
    'created_time',
    'description',
    'feed_targeting',
    'from',
    'link',
    'message',
    'name',
    'object_id',
    'parent_id',
    'permalink_url',
    'place',
    'properties',
    'shares',
    'status_type',
    'story',
    'targeting',
    'to',
    'type',
    'updated_time',
]
post_fields = ','.join(post_fields)

post_metrics_reach = [
    'post_impressions',
    'post_impressions_paid',
    'post_impressions_fan',
    'post_impressions_fan_paid',
    'post_impressions_organic',
    'post_impressions_viral',
    'post_impressions_nonviral',
    'post_impressions_by_story_type',
    'post_consumptions',
    'post_consumptions_by_type',
    'post_negative_feedback',
    'post_negative_feedback_by_type',
]
post_metrics_reach += [x+'_unique' for x in post_metrics_reach]
post_metrics_reach += [
    'post_engaged_users',
    'post_engaged_fan',
    'post_fan_reach',
    'post_reactions_by_type_total',
]
post_metrics_reach = ','.join(post_metrics_reach)

comment_fields = [
    'id',
    'comment_count',
    'created_time',
    'from',
    'like_count',
    'message',
    'message_tags',
    'object',
    'parent',
]
comment_fields = ','.join(comment_fields)


def get_posts(graph, limit = 200):
    posts = []
    for post in graph.get_all_connections(id='me', connection_name='posts', fields = post_fields):
        posts.append(post)
        if len(posts) > limit:
            break
    return posts

def get_post_reactions(graph, post_id):
    data = [x for x in graph.get_all_connections(id=post_id, connection_name='reactions')]
    data = {post_id: data}
    return data

def get_post_comments(graph, post_id):
    comments = []
    for comment in graph.get_all_connections(id=post_id, connection_name='comments', fields = comment_fields):
        if 'parent' not in comment:
            comment['parent_id'] = post_id
        else:
            comment['parent_id'] = comment['parent']['id']
        comments.append(comment)
        comments += get_post_comments(graph, comment['id'])
    return comments

def get_post_shared(graph, post_id):
    shares = []
    for sharedpost in graph.get_all_connections(id=post_id, connection_name='sharedposts'):
        shares.append(sharedpost)
        shares += get_post_shared(graph, sharedpost['id'])
    return shares

def get_posts_by_date(graph, date_start, date_end, get_reach = False):
    if isinstance(date_start,str):
        date_start = datetime.strptime(date_start, r'%Y-%m-%d')
    if isinstance(date_end,str):
        date_end = datetime.strptime(date_end, r'%Y-%m-%d') + timedelta(days=1)
    assert date_end >= date_start, u'date_end must be later than date_start'
    posts = []
    for post in graph.get_all_connections(id='me', connection_name='posts', fields = post_fields):
        date_post = datetime.strptime(post['created_time'][:19], r'%Y-%m-%dT%H:%M:%S')
        if date_post < date_start:
            break
        elif date_post <= date_end:
            if get_reach:
                post['insights'] = {}
                for metric in graph.get_all_connections(id=post['id'], connection_name='insights', metric = post_metrics_reach):
                    post['insights'][metric['name']] = metric
            posts.append(post)
    return posts


def get_reactions(graph, posts):
    reactions = {}
    for post in posts:
        reactions.update(get_post_reactions(graph, post['id']))
        print('Retrieved reactions for {} of {} posts.'.format(len(reactions),len(posts)))
    return reactions

def get_shares(graph, posts):
    shares = []
    for post in posts:
        shares += get_post_shared(graph, post['id'])
        print('Retrieved {} shares for {} posts.'.format(len(shares),len(posts)))
    return shares

def get_comments(graph, posts):
    comments = []
    for count,post in enumerate(posts):
        this = get_post_comments(graph, post['id'])
        for comment in this:
            comment['post_id'] = post['id']
        comments += this
        print('Retrieved {} comments in {} posts.'.format(len(comments),count+1))
    return comments


# def get_shares(graph_or_posts, date_start, date_end):
#     if isinstance(graph_or_posts,list):
#         # This is a list of posts
#         posts = graph_or_posts
#     else:
#         # This is a facebook graph object
#         posts = get_posts_by_date(graph_or_posts, date_start, date_end)
#     if isinstance(date_start,str):
#         date_start = datetime.strptime(date_start, r'%Y-%m-%d')
#     if isinstance(date_end,str):
#         date_end = datetime.strptime(date_end, r'%Y-%m-%d')
#     assert date_end >= date_start, u'date_end must be later than date_start'
#     shares = {}
#     for post in posts:
#         date_post = datetime.strptime(post['created_time'][:19], r'%Y-%m-%dT%H:%M:%S')
#         # if date_post < date_start:
#         #     break
#         if (date_post <= date_end) and (date_post >= date_start):
#             shares.update(get_post_shared(graph, post['id']))
#         # print(post['id'], post['created_time'], len(reactions))
#         print('Retrieved shares for {} of {} posts.'.format(len(shares),len(posts)))
#     return shares
#






if __name__ == '__main__':
    if len(sys.argv)>=1 and sys.argv[1]=='reactions':
        if len(sys.argv) != 6:
            help = """This requires 4 arguments: client, date_start, date_end, filename"""
            print(help)
        else:
            client = sys.argv[2]
            graph = facebook.GraphAPI(access_token=credentials.access_token[client], version='2.12')
            posts = get_posts_by_date(graph, sys.argv[3], sys.argv[4])
            with open(sys.argv[5] + '_posts.json', 'w') as infile:
                json.dump(posts, infile)
            reactions = get_reactions(posts, sys.argv[3], sys.argv[4])
            with open(sys.argv[5] + '_reactions.json', 'w') as infile:
                json.dump(reactions, infile)


    if len(sys.argv)>=1 and sys.argv[1]=='complete':
        if len(sys.argv) != 6:
            help = """This requires 4 arguments: client, date_start, date_end, filename"""
            print(help)
        else:
            client = sys.argv[2]
            graph = facebook.GraphAPI(access_token=credentials.access_token[client], version='2.12')
            posts = get_posts_by_date(graph, sys.argv[3], sys.argv[4], get_reach=True)
            print('{} posts found.'.format(len(posts)))
            with open(sys.argv[5] + '_posts.json', 'w') as infile:
                json.dump(posts, infile)
            comments = get_comments(graph, posts)
            with open(sys.argv[5] + '_comments.json', 'w') as infile:
                json.dump(comments, infile)
            reactions = get_reactions(graph, posts + comments)
            with open(sys.argv[5] + '_reactions.json', 'w') as infile:
                json.dump(reactions, infile)
