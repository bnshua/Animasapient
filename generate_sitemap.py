import urllib.request, json, os, re

SUPA_URL = os.environ['SUPA_URL']
SUPA_KEY = os.environ['SUPA_KEY']
BASE = 'https://www.animasapient.xyz'

req = urllib.request.Request(
  SUPA_URL + '/rest/v1/posts?select=id,title,slug,category,date,excerpt,byline,image_url,tags&order=date.desc&limit=10000',
  headers={'apikey': SUPA_KEY, 'Authorization': 'Bearer ' + SUPA_KEY}
)
with urllib.request.urlopen(req) as r:
  posts = json.loads(r.read())

def slug(s):
  return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', (s or '').lower())).strip('-')

def esc(s):
  return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

static_urls = [
  (BASE + '/', 'weekly', '1.0', ''),
  (BASE + '/about', 'monthly', '0.6', ''),
  (BASE + '/philosophy', 'weekly', '0.8', ''),
  (BASE + '/religion-spirituality', 'weekly', '0.8', ''),
  (BASE + '/geography', 'weekly', '0.8', ''),
  (BASE + '/culture', 'weekly', '0.8', ''),
]

article_urls = []

for p in posts:
  cat = slug(p.get('category',''))
  art = p.get('slug') or slug(p.get('title',''))
  if not cat or not art:
    continue

  full_url = BASE + '/' + cat + '/' + art
  title = esc(p.get('title',''))
  desc = esc((p.get('excerpt') or '')[:160])
  img = esc(p.get('image_url') or BASE + '/image.png')
  author = esc(p.get('byline') or 'Animasapient')
  date = p.get('date','')
  keywords = esc(p.get('tags') or p.get('category',''))
  post_id = p.get('id','')

  html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Animasapient</title>
<meta name="description" content="{desc}">
<meta name="author" content="{author}">
<meta name="keywords" content="{keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{full_url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{full_url}">
<meta property="og:image" content="{img}">
<meta property="og:site_name" content="Animasapient">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{desc}",
  "url": "{full_url}",
  "image": "{img}",
  "datePublished": "{date}",
  "author": {{"@type": "Person", "name": "{author}"}},
  "publisher": {{"@type": "Organization", "name": "Animasapient", "url": "{BASE}"}}
}}
</script>
<script>window.location.replace('/?post={post_id}');</script>
</head>
<body><p>Loading: {title}</p></body>
</html>"""

  folder = cat + '/' + art
  os.makedirs(folder, exist_ok=True)
  with open(folder + '/index.html', 'w') as f:
    f.write(html)

  article_urls.append((full_url, 'monthly', '0.9', date))

# Write sitemap.xml
def url_block(loc, freq, pri, lastmod):
  ld = f'\n    <lastmod>{lastmod}</lastmod>' if lastmod else ''
  return f'  <url>\n    <loc>{loc}</loc>{ld}\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>'

xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
xml += '\n'.join(url_block(*u) for u in static_urls + article_urls)
xml += '\n</urlset>\n'

with open('sitemap.xml', 'w') as f:
  f.write(xml)

print(f'Done: {len(article_urls)} article pages + sitemap.xml')
