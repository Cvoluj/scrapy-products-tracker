from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class SaveImagesPipeline(ImagesPipeline):
    """
    Uploads an image

    !!! If it doesn't work, try updating Pillow !!!
    """

    def get_media_requests(self, item, info):
        return [Request(item['image_url'], meta={'image_file': item['image_file']})]

    def file_path(self, request, response=None, info=None, *, item=None):
        return request.meta['image_file']
