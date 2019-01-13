"""setup.py: Script to download photos from Flickr API and map them to django models(database)"""
__author__ = "Akshay Saini" 
__email__  = "akkilsl522@gmail.com"

import os
import sys
import json
import getopt
import asyncio
import aiohttp
import flickrapi

from decouple import config


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def download_images_from_flickr():
    api_key = config('FLICKR_API_KEY')
    api_secret = config('FLICKR_API_SECRET')
    flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True)

    group_keywords = ['2015', '2016', '2017', '2018']

    for gk in group_keywords:
        yield get_flickr_urls(gk, flickr) # return list of photos urls and photo object for each group_keyword

def get_flickr_urls(group_keyword, flickr):

    per_page = 50 # number of photos per group

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


    print('\ngroup:', group_keyword, '- downloading...')
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
    
    print('\n<INFO>:: downloading complete')
    
    data = json.loads(json.dumps(output))

    with open(BASE_DIR + '/flickr.json', 'w') as outfile:
        json.dump(data, outfile)


def json_to_database(user):
    data = open(BASE_DIR + '/flickr.json').read()
    groups = json.loads(data)
    
    for photos in groups:
        group, _ = Group.objects.update_or_create(user=user, name=photos[0]['group'])
        for photo in photos:
            Photo.objects.update_or_create(group=group, title=photo['title'], image=photo['url'])

    print('<INFO>:: json written in DB')

def console_help():
    print('<HELP>:: \n\tsetupdb.py -u <username>\n\n\tsetupdb.py --username <username>\n\n')
    sys.exit()

if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE']='flickr.settings'

    from django import setup
    setup()

    from django.contrib.auth.models import User
    from flickr_api.models import Photo, Group

    username = None
   
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hu:',['help', 'username'])
    except getopt.GetoptError:
        console_help()

    if not opts or len(opts) != 1:
        console_help()

    for opt, arg in opts:
        if opt == '-u' and bool(arg):
            username = arg
        elif opt == '--username' and len(args)==1:
            username = args[0]
        else:
            console_help()

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print('<INFO>:: user', username, 'not found (you can create superuser from command - `python manage.py createsuperuser`)')
        sys.exit()
    except Exception as e:
        print('<INFO>::', str(e))
        print('<INFO>:: run command - `python manage.py migrate` and create user before running setup.py')
        sys.exit()

    print('<INFO>::', username, 'found')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    json_to_database(user)

