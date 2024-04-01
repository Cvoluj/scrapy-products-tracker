from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class SaveImagesPipeline(ImagesPipeline):
    """
    Custom image pipeline for saving downloaded product images.

    This pipeline retrieves image URLs and filenames from the scraped product data and generates Scrapy Request objects for downloading the images.
    It also defines how to construct the filenames for the downloaded images based on information from the product item.
    """

    def get_media_requests(self, item, info):
        """
        Generates Scrapy Request objects for downloading product images based on information in the item.

        Args:
            item (ProductItem): The Scrapy item object containing product data, including the image URL.
            info (scrapy.crawler.CrawlerProcess): Information about the Scrapy crawler process.

        Returns:
            list: A list containing a single Scrapy Request object for downloading the product image.
        """

        return [Request(item['image_url'], meta={'image_file': item['image_file']})]

    def file_path(self, request, response=None, info=None, *, item=None):
        """
        Constructs the filename for the downloaded product image based on information in the item.

        This method uses the 'image_file' field from the product item to create a unique filename for the downloaded image.

        Args:
            request (scrapy.Request): The Scrapy Request object for the image download.
            item (ProductItem): The Scrapy item object containing product data, including the 'image_file' field.

        Returns:
            str: The filename for the downloaded product image.
        """

        return request.meta['image_file']
