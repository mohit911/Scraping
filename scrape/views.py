from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render, HttpResponseRedirect
from scrape.models import ScrapeUrl, ScrapeData

import urllib2
import timeit
import requests

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from threading import Thread

# Create your views here.


def home(request):
    websites = ScrapeUrl.objects.all()

    '''Start creating paginator. '''
    paginator = Paginator(websites, 3)

    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        websites = paginator.page(page)
    except(EmptyPage, InvalidPage):
        websites = paginator.page(paginator.num_pages)

    context = {'websites': websites}
    template = 'home.html'
    return render(request, template, context)


def view_website(request, id):
    website_link = ScrapeUrl.objects.get(id=id)
    scrape_data = ScrapeData.objects.filter(scrapeUrl_link=website_link)

    '''Start creating paginator. '''
    paginator = Paginator(scrape_data, 6)

    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        scrape_data = paginator.page(page)
    except(EmptyPage, InvalidPage):
        scrape_data = paginator.page(paginator.num_pages)

    context = {'scrape_data': scrape_data, 'website_link': website_link}
    template = 'scrapedata.html'
    return render(request, template, context)


def search_db(request):
    websites = []
    searchtext = request.GET.get('searchtext')
    results = ScrapeUrl.objects.filter(scrapeUrl_link__icontains=searchtext)
    websites = results
    context = {'websites': websites}
    template = 'results.html'
    return render(request, template, context)


def save_in_db(scrape_url, image_info, first_time, second_time, data):
    try:
        try:
            x = ScrapeUrl.objects.get(scrapeUrl_link=scrape_url)
            x.head_data = data
            x.scrape_time = first_time + second_time
            x.save()
        except ScrapeUrl.DoesNotExist:
            x = ScrapeUrl.objects.create(
                scrapeUrl_link=scrape_url,
                head_data=data,
                scrape_time=first_time + second_time)

        for image in image_info:
            try:
                ScrapeData.objects.create(
                    scrapeUrl_link=x,
                    image_link=image['url'],
                    image_width=image['width'],
                    image_height=image['height'])
            except:
                pass
        return
    except:
        print("=============Database saving failed.=============")
        return


def scrape(request):
    context = {}
    image_info = []
    try:
        start = int(timeit.default_timer())
        scrape_url = request.GET.get('scrapeUrl')
        page = urllib2.urlopen(scrape_url).read()
        soup1 = BeautifulSoup(page)

        og_title = soup1.findAll(attrs={"property": "og:title"})
        if not og_title:
            twitter_title = soup1.findAll(attrs={"name": "twitter:title"})
        if not og_title and not twitter_title:
            title = soup1.find("title")

        stop = int(timeit.default_timer())
        first_time = stop - start

        if og_title:
            data = og_title
        elif twitter_title:
            data = twitter_title
        elif title:
            data = title
        else:
            pass
        data = str(data)

        start2 = int(timeit.default_timer())
        images = []
        try:
            for x in soup1.findAll('img'):
                if not '.gif' in x['src']:
                    images.append(x['src'])
        except:
            if not images:
                return HttpResponseRedirect(reverse('home'))

        def get_dimensions(url):
            image_dict = {}
            data = requests.get(url).content
            im = Image.open(BytesIO(data))
            width, height = im.size
            image_dict['url'] = url
            image_dict['width'] = width
            image_dict['height'] = height
            image_info.append(image_dict)

        threads = []
        for i in images:
            t = Thread(target=get_dimensions, args=[i])
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        stop2 = int(timeit.default_timer())
        second_time = stop2 - start2
        total = first_time + second_time

        save_in_db(scrape_url, image_info, first_time, second_time, data)

        context = {'head_data': data, 'total_time': total, 'image_info': image_info}
        template = 'scrapedata.html'
        return render(request, template, context)
    except:
        print('Failed in Exception.')
        context = {'success': False, 'message': 'Saving failed'}
        return HttpResponseRedirect(reverse('home'))
