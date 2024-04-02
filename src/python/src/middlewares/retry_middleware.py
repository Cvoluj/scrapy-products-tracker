from scrapy import Spider, Request
from scrapy.http import Response


class RetryMiddleware:
    """
    Middleware to handle retries for requests that receive a 403 response.

    This middleware checks if a response status code is 403. If so, it attempts to retry the request
    a specified number of times before finally giving up. It sets the 'Connection' header to 'close'
    to ensure that the connection is not reused, potentially allowing for IP change if using a proxy
    that changes IP per request.
    """

    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        """
        Processes a response by retrying the request if it received a 403 status code.

        Args:
            request (Request): The request that received a 403 response.
            response (Response): The response received from making the request.
            spider (Spider): The spider that made the request.

        Returns:
            Response: The original response if the retry limit is reached or the status code is not
            403. A new request object for retry if the status code is 403 and retry limit is not
            reached.
        """
        if response.status == 403:
            request.headers["Connection"] = "close"
            retry_times = request.meta.get("retry_times", 0) + 1
            max_retry_times = spider.settings.getint("RETRY_TIMES", 5)

            if retry_times <= max_retry_times:
                spider.logger.info(f"Retrying {request.url} due to 403, attempt {retry_times}")
                request = request.copy()
                request.meta["retry_times"] = retry_times
                return request
        return response
