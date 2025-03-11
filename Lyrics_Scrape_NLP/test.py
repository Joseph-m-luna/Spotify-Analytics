import requests
from bs4 import BeautifulSoup


# url = "https://www.musixmatch.com/search?query=16+tons"

# headers = {
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "accept-encoding": "gzip, deflate, br, zstd",
#     "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,de-DE;q=0.6,de;q=0.5",
#     "cache-control": "max-age=0",
#     "cookie": "mxm_bab=AA; _vwo_uuid_v2=D8CFEF7B638F557D83C432A6BC2F4EF36|2c059428710b9af7ae3716d94cae4f3f; mp_e69e49ebd7b89e5b4de2d45fc657b1ba_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A195776c5efe58a-0487b10d0c89dd-14462c6e-4b9600-195776c5efe58a%22%2C%22%24device_id%22%3A%20%22195776c5efe58a-0487b10d0c89dd-14462c6e-4b9600-195776c5efe58a%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.musixmatch.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.musixmatch.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.musixmatch.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.musixmatch.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D; _fbp=fb.1.1741465345827.618853016992964856; show-pro-banner=false; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Mar+08+2025+12%3A27%3A11+GMT-0800+(Pacific+Standard+Time)&version=202407.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=bd1bc9c0-4e7e-4134-9223-6019db18514e&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&AwaitingReconsent=false&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0",
#     "priority": "u=0, i",
#     "referer": "https://www.google.com/",
#     "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Linux\"",
#     "sec-fetch-dest": "document",
#     "sec-fetch-mode": "navigate",
#     "sec-fetch-site": "same-origin",
#     "sec-fetch-user": "?1",
#     "upgrade-insecure-requests": "1",
#     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
# }

# response = requests.get(url, headers=headers)
# response.raise_for_status()

url = "https://search.azlyrics.com/search.php?q=somebody+to+lean+on&w=lyrics&p=1&x=3ef797227307e0c1e25d9ff9afb5f4f9248014a66c6170388d4c3e4213c5fcfe"

response = requests.get(url)
response.raise_for_status()


print(response.text)

with open ("test.html", "w") as file:
    file.write(response.text)

soup = BeautifulSoup(response.text, "html.parser")