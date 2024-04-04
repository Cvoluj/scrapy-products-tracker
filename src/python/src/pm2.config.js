const path = require('path');
const PROJECT_PREFIX = 'S1';

const spiders = [
  {
    name: `${PROJECT_PREFIX}_zoro_category_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl zoro_category_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_zoro_products_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl zoro_products_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_quill_category_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl quill_category_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_quill_products_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl quill_products_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_customink_category_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl customink_category_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_customink_products_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl customink_products_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_costco_category_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl costco_category_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_costco_products_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl costco_products_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_viking_category_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl viking_category_spider'",
  },
  {
    name: `${PROJECT_PREFIX}_viking_products_spider`,
    interpreter_args: "-c 'poetry run scrapy crawl viking_products_spider'",
  },
];

const producers = [
  {
    name: `${PROJECT_PREFIX}_csv_category_producer`,
    interpreter_args: "-c 'poetry run scrapy csv_category_producer --chunk_size=500 --mode=worker'",
  },
  {
    name: `${PROJECT_PREFIX}_csv_product_producer`,
    interpreter_args: "-c 'poetry run scrapy csv_product_producer --chunk_size=500 --mode=worker'",
  },
];

const consumers = [
  {
    name: `${PROJECT_PREFIX}_category_result_consumer`,
    interpreter_args: "-c 'poetry run scrapy category_result_consumer --mode=worker'",
  },
  {
    name: `${PROJECT_PREFIX}_category_reply_consumer`,
    interpreter_args: "-c 'poetry run scrapy category_reply_consumer --mode=worker'",
  },
  {
    name: `${PROJECT_PREFIX}_product_result_consumer`,
    interpreter_args: "-c 'poetry run scrapy product_result_consumer --mode=worker'",
  },
  {
    name: `${PROJECT_PREFIX}_product_reply_consumer`,
    interpreter_args: "-c 'poetry run scrapy product_reply_consumer --mode=worker'",
  },
];

const commands = [
  {
    name: `${PROJECT_PREFIX}_start_category_tracking`,
    interpreter_args: "-c 'poetry run scrapy start_tracking --model=CategoryTargets'",
  },
  {
    name: `${PROJECT_PREFIX}_start_products_tracking`,
    interpreter_args: "-c 'poetry run scrapy start_tracking --model=ProductTargets'",
  },
];

const processNames = [];
const apps = [];

Array.from([producers, spiders, consumers, commands]).map(t => {
  t.reduce((a, v) => {
    if (!v.hasOwnProperty('name') || v.name.length === 0) {
      console.error('ERROR: process name field is required');
      process.exit(1);
    }
    if (processNames.includes(v.name)) {
      console.error(`ERROR: Duplicate process name declared: ${v.name}. Check required`);
      process.exit(1);
    }

    processNames.push(v.name);
    a.push(
      Object.assign(
        {},
        {
          cwd: ".",
          interpreter: "/bin/bash",
          script: "poetry",
          autorestart: false,
          watch: false,
          instances: 1,
          combine_logs: true,
          merge_logs: true,
          error_file: path.join('logs', `${v.name}.log`),
          out_file: path.join('logs', `${v.name}.log`),
          max_restarts: 5,
          max_memory_restart: "128M",
        },
        v,
        (v.hasOwnProperty('cron_restart')) ? {
          cron_restart: v.cron_restart,
          autorestart: false,
        } : null,
      )
    );
    return a
  }, apps)
});

module.exports = {
  apps: apps
};
