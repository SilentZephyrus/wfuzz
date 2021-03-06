import re
from urlparse import urlparse, urljoin

from wfuzz.plugin_api.mixins import DiscoveryPluginMixin
from wfuzz.plugin_api.base import BasePlugin
from wfuzz.plugin_api.urlutils import parse_url
from wfuzz.externals.moduleman.plugin import moduleman_plugin

@moduleman_plugin
class links(BasePlugin, DiscoveryPluginMixin):
    name = "links"
    author = ("Xavi Mendez (@xmendez)",)
    version = "0.1"
    summary = "Parses HTML looking for new content."
    description = ("Parses HTML looking for new content",)
    category = ["default", "active", "discovery"]
    priority = 99

    parameters = (
    )


    def __init__(self):
	BasePlugin.__init__(self)

	regex = [ 'href="((?!mailto:|tel:|#|javascript:).*?)"',
	    'src="((?!javascript:).*?)"',
	    'action="((?!javascript:).*?)"',
	    # http://en.wikipedia.org/wiki/Meta_refresh
	    '<meta.*content="\d+;url=(.*?)">',
	    'getJSON\("(.*?)"',
	]

	self.regex = []
	for i in regex:
	    self.regex.append(re.compile(i, re.MULTILINE|re.DOTALL))

    def validate(self, fuzzresult):
	return fuzzresult.code in [200]

    def process(self, fuzzresult):
	l = []

	#<a href="www.owasp.org/index.php/OWASP_EU_Summit_2008">O
	#ParseResult(scheme='', netloc='', path='www.owasp.org/index.php/OWASP_EU_Summit_2008', params='', query='', fragment='')

	for r in self.regex:
	    for i in r.findall(fuzzresult.history.content):
		parsed_link = parse_url(i)

		if (not parsed_link.scheme or parsed_link.scheme == "http" or parsed_link.scheme == "https") and \
		    (not parsed_link.netloc and parsed_link.path):
		    if i not in l:
			l.append(i)

			# dir path
			split_path = parsed_link.path.split("/")
			newpath = '/'.join(split_path[:-1]) + "/"
			self.queue_url(urljoin(fuzzresult.url, newpath))

			# file path
			self.queue_url(urljoin(fuzzresult.url, i))


