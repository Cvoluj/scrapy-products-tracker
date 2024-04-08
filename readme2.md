# PRODUCTS TRACKER

### Overview:
Products tracker is a service for tracking and storing product data within specified categories or directly specified products.

At the current version, the tracker allows fetching the "history" and dynamics of products from the following sites:

- www.zoro.com
- www.quill.com
- www.costco.com
- www.customink.com
- www.viking-direct.co.uk

Categories are defined by direct links through importing from a CSV file. Products are specified by direct links from a CSV file or as a result of scraping categories.

In the current version, the tracker allows initiating a session from 1 CSV file with categories and 1 CSV file with direct links to products. Example of csv file with links [here](#csv-example)

### Features:

- pm2 for running all processes
- configuration via ENV variables and/or .env file
- possibility to add new spiders (see [here](#Spiders))
- deployment capability (see [requirements and instructions](#Deploy))
## Installation:
To work with the project, you'll need Python 3.11+, Poetry, Docker (for running MySQL and RabbitMQ containers), Node.js (for running the pm2 module).

1. Clone the repository.
2. Run `cp .env.example .env` (.env setup guide [here](#env-setup))
3. Navigate to `src/python/src`.
4. Run `poetry install`.
5. Activate the virtual environment with `poetry shell`.
6. Run `scrapy`.
7. Start MySQL and RabbitMQ in `docker-compose.yml`.
8. Place the file with links for scraping into the project directory.
9. Start the session with pm2 (supports 2 files with categories/products).





### ENV setup

### CSV example
```csv
head url,
https://www.zoro.com/impact-bit-socket-sets/c/11945/,
https://www.quill.com/whole-bean-coffee/cbk/53110.html,
https://www.customink.com/products/drinkware/glassware/58,
https://www.costco.com/holiday-gift-baskets.html,

```
