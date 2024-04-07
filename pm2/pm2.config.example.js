const path = require('path');
const {
  PYTHON_INTERPRETER,
  SCRAPY_SCRIPT,
  PROJECT_PREFIX,
  MAX_MEMORY_RESTART,
  PYTHON_CWD,
  TYPESCRIPT_CWD,
  PM2_LOG_DIRECTORY,
  NODEJS_SCRIPT,
} = require('./settings/settings');

const spiders = [
  {
    name: `${PROJECT_PREFIX}_zoro_category_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl zoro_category_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_zoro_products_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl zoro_products_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_quill_category_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl quill_category_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_quill_products_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl quill_products_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_customink_category_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl customink_category_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_customink_products_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl customink_products_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_costco_category_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl costco_category_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_costco_products_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl costco_products_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_viking_category_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl viking_category_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_viking_products_spider`,
    script: SCRAPY_SCRIPT,
    args: "crawl viking_products_spider",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
];

const producers = [
  {
    name: `${PROJECT_PREFIX}_category_producer`,
    script: SCRAPY_SCRIPT,
    args: "category_producer --chunk_size=500 --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_product_producer`,
    script: SCRAPY_SCRIPT,
    args: "product_producer --chunk_size=500 --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
];

const consumers = [
  {
    name: `${PROJECT_PREFIX}_category_result_consumer`,
    script: SCRAPY_SCRIPT,
    args: "category_result_consumer --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_category_reply_consumer`,
    script: SCRAPY_SCRIPT,
    args: "category_reply_consumer --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_product_result_consumer`,
    script: SCRAPY_SCRIPT,
    args: "product_result_consumer --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
  {
    name: `${PROJECT_PREFIX}_product_reply_consumer`,
    script: SCRAPY_SCRIPT,
    args: "product_reply_consumer --mode=worker",
    interpreter: PYTHON_INTERPRETER,
    instances: 1,
    autorestart: true,
  },
];

const commands = [
  // {
  //   name: `${PROJECT_PREFIX}_start_category_tracking`,
  //   script: SCRAPY_SCRIPT,
  //   args: "start_tracking --model=CategoryTargets",
  //   interpreter: PYTHON_INTERPRETER,
  //   instances: 1,
  //   autorestart: true,
  // },
  // {
  //   name: `${PROJECT_PREFIX}_start_products_tracking`,
  //   script: SCRAPY_SCRIPT,
  //   args: "start_tracking --model=ProductTargets",
  //   interpreter: PYTHON_INTERPRETER,
  //   instances: 1,
  //   autorestart: true,
  // },
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
          cwd: PYTHON_CWD,
          combine_logs: true,
          merge_logs: true,
          error_file: path.join(PM2_LOG_DIRECTORY, `${v.name}.log`),
          out_file: path.join(PM2_LOG_DIRECTORY, `${v.name}.log`),
          max_restarts: 10,
          max_memory_restart: MAX_MEMORY_RESTART,
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
