import os
import asyncio
import aiohttp
import flickrapi
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def download_images_from_flickr():
    api_key = 'c6a2c45591d4973ff525042472446ca2'
    api_secret = '202ffe6f387ce29b'
    flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True)

    group_keywords = ['2015', '2016', '2017', '2018']

    for gk in group_keywords:
        yield get_flickr_urls(gk, flickr)

def get_flickr_urls(group_keyword, flickr):

    per_page = 50

    photos = flickr.walk(text=group_keyword,
                        extras='url_c',
                        per_page=per_page)

    urls, group_photos = [], []
    photo_counter = 1

    for i, photo in enumerate(photos):
        if photo_counter > per_page: 
            break

        url = photo.get('url_c')
        title = photo.get('title')
        
        if url and title: 
            urls.append(url)
            group_photos.append({'title': title, 'url': url.split('/')[-1], 'group': group_keyword})
            photo_counter += 1


    print('group:', group_keyword, '- downloading...')
    return urls, group_photos
    
async def stream_download_image(session, url, image_path):
    image = image_path + url.split('/')[-1]
    async with session.get(url) as response:
        with open(image, 'wb') as fd:
            while True:
                chunk = await response.content.read(10)
                if not chunk:
                    break
                fd.write(chunk)

async def main():
    output = []

    image_path = BASE_DIR + '/media/'

    if not os.path.exists(image_path):
        os.makedirs(image_path)

    for (urls, group_photos) in download_images_from_flickr():
        output.append(group_photos)
        async with aiohttp.ClientSession() as session:
            for url in urls:
                await stream_download_image(session, url, image_path)
    
    print('download complete')
    
    data = json.loads(json.dumps(output))

    with open(BASE_DIR + '/flickr.json', 'w') as outfile:
        json.dump(data, outfile)


def json_to_database():
    data = open(BASE_DIR + '/flickr.json').read()
    groups = json.loads(data)
    
    try:
        user = User.objects.get(id=1) # superuser by default
    except User.DoesNotExist:
        print('create atleast one user using manage.py createsuperuser')
        return

    for photos in groups:
        group = Group.objects.create(user=user, name=photos[0]['group'])
        for photo in photos:
            Photo.objects.create(group=group, title=photo['title'], image=photo['url'])

    print('json written in DB')


if __name__ == '__main__':
  os.environ['DJANGO_SETTINGS_MODULE']='flickr.settings'

  from django import setup
  setup()
  
  from django.contrib.auth.models import User
  from flickr_api.models import Photo, Group

  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
  json_to_database()

