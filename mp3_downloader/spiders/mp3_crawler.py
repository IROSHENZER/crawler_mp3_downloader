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
        # Extract all links from the page
        links = response.css('a::attr(href)').getall()
        
        for link in links:
            # Decode and remove URL encoding
            decoded_link = unquote(link)
            
            # Check if the link is within the allowed domain
            if self.allowed_domains[0] not in decoded_link:
                continue
            
            # Check if the link points to an MP3 file
            if decoded_link.endswith('.mp3'):
                yield response.follow(link, callback=self.save_mp3)
            elif decoded_link == 'mp3 site link':
                # Exclude metadata links
                continue
            else:
                # Follow the decoded link to crawl into subdirectory
                yield response.follow(link, callback=self.parse)
                
    def save_mp3(self, response):
        # Extracting the MP3 filename from the URL
        filename = os.path.basename(response.url)
        
        # Remove special characters and replace %20 with actual spaces
        filename = re.sub(r'[%()]+', '', filename).replace('%20', ' ').strip()
        
        # Remove numbers
        filename = re.sub(r'\d+', '', filename).strip()
        
        # Replace multiple spaces with a single space
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        # Replace 20 with a space or hyphen
        filename = filename.replace('20', ' ').replace('-', ' ')
        
        # Insert spaces before capital letters
        filename = re.sub(r'([a-z])([A-Z])', r'\1 \2', filename)
        
        # Remove extra spaces and strip
        filename = ' '.join(filename.split()).strip()
        
        # Remove .mp from the end of filename if it exists
        if filename.lower().endswith('.mp'):
            filename = filename[:-3]
        
        # Remove .mp3 from filename
        filename_without_extension = filename.replace('.mp3', '')
        
        # Extracting the relative path to recreate folder structure
        relative_path = os.path.dirname(unquote(response.url).split('albums/')[1])
        
        # Remove special characters and replace %20 with actual spaces
        relative_path = re.sub(r'[%()]+', '', relative_path).replace('%20', ' ').strip()
        
        # Replace 20 with a space or hyphen
        relative_path = relative_path.replace('20', ' ').replace('-', ' ')
        
        # Insert spaces before capital letters
        relative_path = re.sub(r'([a-z])([A-Z])', r'\1 \2', relative_path)
        
        # Remove extra spaces and strip
        relative_path = ' '.join(relative_path.split()).strip()
        
        # Specify the directory where you want to save the MP3 files
        save_dir = os.path.join('D:/audio download/mp3_downloader/downloads', relative_path)
        
        # Create the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Print and log the filename
        print(f'Processing file: {filename_without_extension}')
        
        # Save the MP3 file without .mp3 extension
        with open(os.path.join(save_dir, filename_without_extension + '.mp3'), 'wb') as f:
            f.write(response.body)
        
        self.log(f'Saved file {filename_without_extension}')
        
        # Set metadata and album art using eyed3
        audiofile = eyed3.load(os.path.join(save_dir, filename_without_extension + '.mp3'))
        
        # Clear existing tags
        if audiofile.tag:
            audiofile.tag.clear()
        
        # Set new tags
        audiofile.tag.artist = 'www.website.com'
        audiofile.tag.album_artist = 'www.website.com'
        audiofile.tag.composer = 'www.website.com'
        audiofile.tag.album = 'www.website.com'
        audiofile.tag.comments.set('www.website.com')
        
        # Set album art
        album_art_path = 'D:/audio download/mp3_downloader/art.jpeg'
        if os.path.exists(album_art_path):
            with open(album_art_path, 'rb') as img:
                image_data = img.read()
            audiofile.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, image_data, 'image/jpeg', description='Cover')
        
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
