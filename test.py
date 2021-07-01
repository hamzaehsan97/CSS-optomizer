import tinycss2
import urllib.request


response =  urllib.request.urlopen('https://blog.koerber-tissue.com/hs-fs/hub/4035267/hub_generated/template_assets/33561049770/1625007799686/koerber-theme/assets/koerber-primary.css')
(rules, encoding )= tinycss2.parse_stylesheet_bytes(
    skip_comments = True,
    skip_whitespace = True,
    css_bytes=response.read(),
    # Python 3.x
    protocol_encoding=response.info().get_content_type(),
    
)
for rule in rules:
    print(rule)