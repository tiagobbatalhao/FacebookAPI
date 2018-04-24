import credentials
import time
from datetime import datetime
import json
import facebook
import sys

page_metrics = [
    ('page_stories',('day','week','days_28')),
    ('page_storytellers',('day','week','days_28')),
    ('page_stories_by_story_type',('day','week','days_28')),
    ('page_storytellers_by_story_type',('day','week','days_28')),
    ('page_storytellers_by_age_gender',('day','week','days_28')),
    ('page_storytellers_by_city',('day','week','days_28')),
    ('page_impressions',('day','week','days_28')),
    ('page_impressions_unique',('day','week','days_28')),
    ('page_impressions_paid',('day','week','days_28')),
    ('page_impressions_paid_unique',('day','week','days_28')),
    ('page_impressions_organic',('day','week','days_28')),
    ('page_impressions_organic_unique',('day','week','days_28')),
    ('page_impressions_by_story_type',('day','week','days_28')),
    ('page_impressions_by_story_type_unique',('day','week','days_28')),
    ('page_impressions_by_city_unique',('day','week','days_28')),
    ('page_impressions_by_age_gender_unique',('day','week','days_28')),
    ('page_impressions_frequency_distribution',('day','week','days_28')),
    ('page_engaged_users',('day','week','days_28')),
    ('page_post_engagements',('day','week','days_28')),
    ('page_consumptions',('day','week','days_28')),
    ('page_consumptions_unique',('day','week','days_28')),
    ('page_consumptions_by_consumption_type',('day','week','days_28')),
    ('page_consumptions_by_consumption_type_unique',('day','week','days_28')),
    ('page_negative_feedback',('day','week','days_28')),
    ('page_negative_feedback_unique',('day','week','days_28')),
    ('page_negative_feedback_by_type',('day','week','days_28')),
    ('page_negative_feedback_by_type_unique',('day','week','days_28')),
    ('page_positive_feedback_by_type',('day','week','days_28')),
    ('page_positive_feedback_by_type_unique',('day','week','days_28')),
    ('page_actions_post_reactions_like_total',('day')),
    ('page_actions_post_reactions_love_total',('day')),
    ('page_actions_post_reactions_wow_total',('day')),
    ('page_actions_post_reactions_haha_total',('day')),
    ('page_actions_post_reactions_sorry_total',('day')),
    ('page_actions_post_reactions_anger_total',('day')),
    ('page_actions_post_reactions_total',('day')),
]

def get_page_metrics(graph, **kwargs):
    metrics = {}
    metrics_str = ','.join([x[0] for x in page_metrics])
    for metric in graph.get_all_connections(id='me', connection_name='insights', metric = metrics_str, **kwargs):
        metrics[metric['name']] = metric
    return metrics


if __name__ == '__main__':
    if len(sys.argv)>=1 and sys.argv[1]=='insights':
        if len(sys.argv) != 6:
            help = """This requires 4 arguments: client, date_start, date_end, filename"""
            print(help)
        else:
            client = sys.argv[2]
            graph = facebook.GraphAPI(access_token=credentials.access_token[client], version='2.12')
            kwargs = {}
            kwargs['since'] = sys.argv[3]
            kwargs['until'] = sys.argv[4]
            kwargs['period'] = 'day'
            metrics = get_page_metrics(graph, **kwargs)
            with open(sys.argv[5] + '_pageinsights.json', 'w') as infile:
                json.dump(metrics, infile)
