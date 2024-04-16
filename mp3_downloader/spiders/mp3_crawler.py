import scrapy
import os
import re
from urllib.parse import unquote
import eyed3

class Mp3CrawlerSpider(scrapy.Spider):
    name = 'mp3_crawler'
    
    start_urls = [' mp3 site link']
    
    allowed_domains = ['link domain']

    def parse(self, response):
        links = response.css('a::attr(href)').getall()
        
        for link in links:
            decoded_link = unquote(link)
            
            if self.allowed_domains[0] not in decoded_link:
                continue
            
            if decoded_link.endswith('.mp3'):
                yield response.follow(link, callback=self.save_mp3)
            elif decoded_link == 'mp3 site link':
                continue
            else:
                yield response.follow(link, callback=self.parse)
                
    def save_mp3(self, response):
        filename = os.path.basename(response.url)
        
        filename = re.sub(r'[%()]+', '', filename).replace('%20', ' ').strip()
        
        filename = re.sub(r'\d+', '', filename).strip()
        
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        filename = filename.replace('20', ' ').replace('-', ' ')
        
        filename = re.sub(r'([a-z])([A-Z])', r'\1 \2', filename)
        
        filename = ' '.join(filename.split()).strip()
        
        if filename.lower().endswith('.mp'):
            filename = filename[:-3]
        
        filename_without_extension = filename.replace('.mp3', '')
        
        relative_path = os.path.dirname(unquote(response.url).split('albums/')[1])
        
        relative_path = re.sub(r'[%()]+', '', relative_path).replace('%20', ' ').strip()
        
        relative_path = relative_path.replace('20', ' ').replace('-', ' ')
        
        relative_path = re.sub(r'([a-z])([A-Z])', r'\1 \2', relative_path)
        
        relative_path = ' '.join(relative_path.split()).strip()
        
        save_dir = os.path.join('D:/audio download/mp3_downloader/downloads', relative_path)
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        print(f'Processing file: {filename_without_extension}')
        
        with open(os.path.join(save_dir, filename_without_extension + '.mp3'), 'wb') as f:
            f.write(response.body)
        
        self.log(f'Saved file {filename_without_extension}')
        
        audiofile = eyed3.load(os.path.join(save_dir, filename_without_extension + '.mp3'))
        
        if audiofile.tag:
            audiofile.tag.clear()
        
        audiofile.tag.artist = 'www.website.com'
        audiofile.tag.album_artist = 'www.website.com'
        audiofile.tag.composer = 'www.website.com'
        audiofile.tag.album = 'www.website.com'
        audiofile.tag.comments.set('www.website.com')
        
        album_art_path = 'D:/audio download/mp3_downloader/art.jpeg'
        if os.path.exists(album_art_path):
            with open(album_art_path, 'rb') as img:
                image_data = img.read()
            audiofile.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, image_data, 'image/jpeg', description='Cover')
        
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
