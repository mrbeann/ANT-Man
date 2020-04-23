# coding=utf-8

servers_dict = {}

service_dict = {
    'train-advanced': ['basic', 'config', 'order_other', 'order', 'price', 'route', 'seat', 'station',
                       'ticketinfo', 'train', 'travel', 'travel2', 'travel_plan', 'route_plan'],
    'train-basic': ['basic', 'route', 'station', 'ticketinfo', 'travel', 'seat', 'train', 'order', 'config', 'price'],
    'usertimeline': ['user-timeline', 'post-storage'],
    'hometimeline': ['home-timeline', 'post-storage'],
    'composepost': ['compose-post', 'media', 'social-graph', 'text', 'unique-id', 'url-shorten',
                    'user-mention', 'user', 'user-timeline', 'write-home-timeline', 'post-storage'],
}

# first measure is not accurate, so add one useless value here.
frequency_list = [1300000, 1200000, 1400000, 1600000, 1800000, 2000000, 2200000, 2400000]
request_types = ['mixeddworkers', 'basicworkers', 'advancedworkers']
loads = None
application_name = 'train'
measure_path = './data/real/train/'
model_path = './data/model/'
application_url = None
request_sender_url = None
deploy_list = ['PC', 'TC', 'Fridge-a', 'Fridge-b', 'capping']
focus_server = None
other_server = None
server_setting_path = None
train_exe_time = {}
application_url_social = None
focus_server_social = None
other_server_social = None
request_sender_url_social = None
measure_path_social = './data/real/social/'
server_setting_path_social = None
request_types_social = ['composepost', 'hometimeline', 'usertimeline']
social_services = ['compose-post', 'home-timeline', 'media', 'social-graph', 'text', 'user-timeline',
                   'unique-id', 'url-shorten', 'user-mention', 'user',  'write-home-timeline', 'post-storage']
loads_social = None

