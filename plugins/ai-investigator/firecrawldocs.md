Using the API
Introduction
Firecrawl API Reference
​
Base URL
All requests contain the following base URL:
https://api.firecrawl.dev 

​
Authentication
For authentication, it’s required to include an Authorization header. The header should contain Bearer fc-123456789, where fc-123456789 represents your API Key.
Authorization: Bearer fc-123456789

​
​
Response codes
Firecrawl employs conventional HTTP status codes to signify the outcome of your requests.
Typically, 2xx HTTP status codes denote success, 4xx codes represent failures related to the user, and 5xx codes signal infrastructure problems.
Status
Description
200
Request was successful.
400
Verify the correctness of the parameters.
401
The API key was not provided.
402
Payment required
404
The requested resource could not be located.
429
The rate limit has been surpassed.
5xx
Signifies a server error with Firecrawl.

Refer to the Error Codes section for a detailed explanation of all potential API errors.
​
​
Rate limit
The Firecrawl API has a rate limit to ensure the stability and reliability of the service. The rate limit is applied to all endpoints and is based on the number of requests made within a specific time frame.
When you exceed the rate limit, you will receive a 429 response code.
Endpoints
Scrape
POST
/
scrape
Send
Authorization
Body
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Body
application/json
url
string
required
The URL to scrape
formats
enum<string>[]
Formats to include in the output.
Available options: markdown, html, rawHtml, links, screenshot, extract, screenshot@fullPage
onlyMainContent
boolean
default: true
Only return the main content of the page excluding headers, navs, footers, etc.
includeTags
string[]
Tags to include in the output.
excludeTags
string[]
Tags to exclude from the output.
headers
object
Headers to send with the request. Can be used to send cookies, user-agent, etc.
waitFor
integer
default: 0
Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.
mobile
boolean
default: false
Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.
skipTlsVerification
boolean
default: false
Skip TLS certificate verification when making requests
timeout
integer
default: 30000
Timeout in milliseconds for the request
extract
object
Extract object
Show child attributes
actions
object[]
Actions to perform on the page before grabbing the content
Wait
Screenshot
Click
Write text
Press a key
Scroll
Scrape
Show child attributes
location
object
Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.
Show child attributes
Response
200 - application/json
success
boolean
data
object

import requests

url = "https://api.firecrawl.dev/v1/scrape"

payload = {
    "url": "<string>",
    "formats": ["markdown"],
    "onlyMainContent": True,
    "includeTags": ["<string>"],
    "excludeTags": ["<string>"],
    "headers": {},
    "waitFor": 123,
    "mobile": True,
    "skipTlsVerification": True,
    "timeout": 123,
    "extract": {
        "schema": {},
        "systemPrompt": "<string>",
        "prompt": "<string>"
    },
    "actions": [
        {
            "type": "wait",
            "milliseconds": 2,
            "selector": "#my-element"
        }
    ],
    "location": {
        "country": "<string>",
        "languages": ["en-US"]
    }
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)



—


{
  "success": true,
  "data": {
    "markdown": "<string>",
    "html": "<string>",
    "rawHtml": "<string>",
    "screenshot": "<string>",
    "links": [
      "<string>"
    ],
    "actions": {
      "screenshots": [
        "<string>"
      ]
    },
    "metadata": {
      "title": "<string>",
      "description": "<string>",
      "language": "<string>",
      "sourceURL": "<string>",
      "<any other metadata> ": "<string>",
      "statusCode": 123,
      "error": "<string>"
    },
    "llm_extraction": {},
    "warning": "<string>"
  }
}




—-



Endpoints
Crawl
POST
/
crawl
Send
Authorization
Body
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Body
application/json
url
string
required
The base URL to start crawling from
excludePaths
string[]
Specifies URL patterns to exclude from the crawl by comparing website paths against the provided regex patterns. For example, if you set "excludePaths": ["blog/*"] for the base URL firecrawl.dev, any results matching that pattern will be excluded, such as https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap.
includePaths
string[]
Specifies URL patterns to include in the crawl by comparing website paths against the provided regex patterns. Only the paths that match the specified patterns will be included in the response. For example, if you set "includePaths": ["blog/*"] for the base URL firecrawl.dev, only results matching that pattern will be included, such as https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap.
maxDepth
integer
default: 2
Maximum depth to crawl relative to the entered URL.
ignoreSitemap
boolean
default: true
Ignore the website sitemap when crawling
limit
integer
default: 10
Maximum number of pages to crawl. Default limit is 10000.
allowBackwardLinks
boolean
default: false
Enables the crawler to navigate from a specific URL to previously linked pages.
allowExternalLinks
boolean
default: false
Allows the crawler to follow links to external websites.
webhook
string
The URL to send the webhook to. This will trigger for crawl started (crawl.started) ,every page crawled (crawl.page) and when the crawl is completed (crawl.completed or crawl.failed). The response will be the same as the /scrape endpoint.
scrapeOptions
object
Show child attributes
Response
200 - application/json
success
boolean
id
string
url
string


—


import requests

url = "https://api.firecrawl.dev/v1/crawl"

payload = {
    "url": "<string>",
    "excludePaths": ["<string>"],
    "includePaths": ["<string>"],
    "maxDepth": 123,
    "ignoreSitemap": True,
    "limit": 123,
    "allowBackwardLinks": True,
    "allowExternalLinks": True,
    "webhook": "<string>",
    "scrapeOptions": {
        "formats": ["markdown"],
        "headers": {},
        "includeTags": ["<string>"],
        "excludeTags": ["<string>"],
        "onlyMainContent": True,
        "mobile": True,
        "waitFor": 123
    }
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)



—-


{
  "success": true,
  "id": "<string>",
  "url": "<string>"
}



—-



Endpoints
Get Crawl Status
GET
/
crawl
/
{id}
Send
Authorization
Path
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Path Parameters
id
string
required
The ID of the crawl job
Response
200 - application/json
status
string
The current status of the crawl. Can be scraping, completed, or failed.
total
integer
The total number of pages that were attempted to be crawled.
completed
integer
The number of pages that have been successfully crawled.
creditsUsed
integer
The number of credits used for the crawl.
expiresAt
string
The date and time when the crawl will expire.
next
string | null
The URL to retrieve the next 10MB of data. Returned if the crawl is not completed or if the response is larger than 10MB.
data
object[]
The data of the crawl.
Hide child attributes
data.markdown
string
data.html
string | null
HTML version of the content on page if includeHtml is true
data.rawHtml
string | null
Raw HTML content of the page if includeRawHtml is true
data.links
string[]
List of links on the page if includeLinks is true
data.screenshot
string | null
Screenshot of the page if includeScreenshot is true
data.metadata
object
Show child attributes
Crawl



—-


import requests

url = "https://api.firecrawl.dev/v1/crawl/{id}"

headers = {"Authorization": "Bearer <token>"}

response = requests.request("GET", url, headers=headers)

print(response.text)


—

{
  "status": "<string>",
  "total": 123,
  "completed": 123,
  "creditsUsed": 123,
  "expiresAt": "2023-11-07T05:31:56Z",
  "next": "<string>",
  "data": [
    {
      "markdown": "<string>",
      "html": "<string>",
      "rawHtml": "<string>",
      "links": [
        "<string>"
      ],
      "screenshot": "<string>",
      "metadata": {
        "title": "<string>",
        "description": "<string>",
        "language": "<string>",
        "sourceURL": "<string>",
        "<any other metadata> ": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ]
}



—--


Endpoints
Map
POST
/
map
Send
Authorization
Body
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Body
application/json
url
string
required
The base URL to start crawling from
search
string
Search query to use for mapping. During the Alpha phase, the 'smart' part of the search functionality is limited to 1000 search results. However, if map finds more results, there is no limit applied.
ignoreSitemap
boolean
default: true
Ignore the website sitemap when crawling
includeSubdomains
boolean
default: false
Include subdomains of the website
limit
integer
default: 5000
Maximum number of links to return
Response
200 - application/json
success
boolean
links
string[]


—-


import requests

url = "https://api.firecrawl.dev/v1/map"

payload = {
    "url": "<string>",
    "search": "<string>",
    "ignoreSitemap": True,
    "includeSubdomains": True,
    "limit": 123
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)



—


Endpoints
Batch Scrape
POST
/
batch
/
scrape
Send
Authorization
Body
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Body
application/json
urls
string[]
formats
enum<string>[]
Formats to include in the output.
Available options: markdown, html, rawHtml, links, screenshot, extract, screenshot@fullPage
onlyMainContent
boolean
default: true
Only return the main content of the page excluding headers, navs, footers, etc.
includeTags
string[]
Tags to include in the output.
excludeTags
string[]
Tags to exclude from the output.
headers
object
Headers to send with the request. Can be used to send cookies, user-agent, etc.
waitFor
integer
default: 0
Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.
timeout
integer
default: 30000
Timeout in milliseconds for the request
extract
object
Extract object
Show child attributes
actions
object[]
Actions to perform on the page before grabbing the content
Wait
Screenshot
Click
Write text
Press a key
Scroll
Scrape
Hide child attributes
actions.type
enum<string>
required
Wait for a specified amount of milliseconds
Available options: wait
actions.milliseconds
integer
Number of milliseconds to wait
actions.selector
string
Query selector to find the element by


—


import requests

url = "https://api.firecrawl.dev/v1/batch/scrape"

payload = {
    "urls": ["<string>"],
    "formats": ["markdown"],
    "onlyMainContent": True,
    "includeTags": ["<string>"],
    "excludeTags": ["<string>"],
    "headers": {},
    "waitFor": 123,
    "timeout": 123,
    "extract": {
        "schema": {},
        "systemPrompt": "<string>",
        "prompt": "<string>"
    },
    "actions": [
        {
            "type": "wait",
            "milliseconds": 2,
            "selector": "#my-element"
        }
    ]
}
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)



—


Endpoints
Get Batch Scrape Status
GET
/
batch
/
scrape
/
{id}
Send
Authorization
Path
Authorizations
Authorization
string
headerrequired
Bearer authentication header of the form Bearer <token>, where <token> is your auth token.
Path Parameters
id
string
required
The ID of the batch scrape job
Response
200 - application/json
status
string
The current status of the batch scrape. Can be scraping, completed, or failed.
total
integer
The total number of pages that were attempted to be scraped.
completed
integer
The number of pages that have been successfully scraped.
creditsUsed
integer
The number of credits used for the batch scrape.
expiresAt
string
The date and time when the batch scrape will expire.
next
string | null
The URL to retrieve the next 10MB of data. Returned if the batch scrape is not completed or if the response is larger than 10MB.
data
object[]
The data of the batch scrape.
Hide child attributes
data.markdown
string
data.html
string | null
HTML version of the content on page if includeHtml is true
data.rawHtml
string | null
Raw HTML content of the page if includeRawHtml is true
data.links
string[]
List of links on the page if includeLinks is true
data.screenshot
string | null
Screenshot of the page if includeScreenshot is true
data.metadata
object



—


import requests

url = "https://api.firecrawl.dev/v1/batch/scrape/{id}"

headers = {"Authorization": "Bearer <token>"}

response = requests.request("GET", url, headers=headers)

print(response.text)


—

{
  "status": "<string>",
  "total": 123,
  "completed": 123,
  "creditsUsed": 123,
  "expiresAt": "2023-11-07T05:31:56Z",
  "next": "<string>",
  "data": [
    {
      "markdown": "<string>",
      "html": "<string>",
      "rawHtml": "<string>",
      "links": [
        "<string>"
      ],
      "screenshot": "<string>",
      "metadata": {
        "title": "<string>",
        "description": "<string>",
        "language": "<string>",
        "sourceURL": "<string>",
        "<any other metadata> ": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ]
}


