from scrapy import cmdline

cmdline.execute("scrapy crawl AmzonMaster".split())
cmdline.execute("scrapy crawl AmzonSlaver".split())
cmdline.execute("scrapy crawl JdSlaver".split())

