from .__inner__ import api

def build_profile(name,displayName,avatar,description):
    return {
        'name': name,
        'displayName': displayName,
        'avatar': avatar,
        'description': description
    }

#TODO: 最近聊天列表
@api.route('recent-chat') 
def recent_chat():
    return [
          build_profile(name='jess',displayName='Jess C', avatar='/samples/sample.png',description='Snowy mountain peak under a starry night sky.'),
          build_profile(name='catty',displayName='Catty', avatar='/samples/sample2.png',description='Desert oasis with camels and a vibrant sunset.'),
          build_profile(name='yuki',displayName='Yuki', avatar='/samples/sample3.png',description='Lighthouse on a rocky coast during a storm.'),
          build_profile(name='elle',displayName='Elle', avatar='/samples/sample4.jpg',description='Cherry blossoms by a serene lake in spring.'),
          build_profile(name='jessica',displayName='Jessica', avatar='/samples/sample5.jpg',description='Ancient castle ruins under a full moon.')
    ]

#TODO: 推荐聊天列表
@api.route('recommend-chat') 
def recommend_chat():
    return [
          build_profile(name='jess',displayName='Jess C', avatar='/samples/sample.png',description='Snowy mountain peak under a starry night sky.'),
          build_profile(name='catty',displayName='Catty', avatar='/samples/sample2.png',description='Desert oasis with camels and a vibrant sunset.'),
          build_profile(name='yuki',displayName='Yuki', avatar='/samples/sample3.png',description='Lighthouse on a rocky coast during a storm.'),
          build_profile(name='elle',displayName='Elle', avatar='/samples/sample4.jpg',description='Cherry blossoms by a serene lake in spring.'),
          build_profile(name='jessica',displayName='Jessica', avatar='/samples/sample5.jpg',description='Ancient castle ruins under a full moon.')
    ]
