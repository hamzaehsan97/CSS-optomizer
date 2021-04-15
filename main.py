
from pprint import pprint
from html.parser import HTMLParser
import cssutils
from html.entities import name2codepoint
import tinycss
import cssselect

##Classes and id array
classes = []

## Read html as text
with open('index.html', 'r') as file:
    htmlFeed = file.read().replace('\n', '')

#Read in html tags
#Choose only tags that contain class and id
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'class' or attr[0] == 'id':
                attrList = attr[1].split()
                for i in attrList:
                    classes.append(i)

## Remove Duplicates from the classes list using a set function
def removeDuplicates(classes):
    classes = list(set(classes))
    return classes

## Read in CSS
def readCSS(fileName):
    with open(fileName, 'r') as file:
        CSSFeed = file.read().replace('\n', '')
    stylesheet = tinycss.make_parser().parse_stylesheet(CSSFeed)
    return stylesheet


## Seperate rules in stylesheet and return rules list
def seperateRules(stylesheet):
    seperateRulesReturn = []
    for i in range(0,len(stylesheet.rules)):
        rule = stylesheet.rules[i].selector.as_css()
        ruleSplit = rule.split(',')
        seperateRulesReturn.append(ruleSplit)
    return seperateRulesReturn



parser = MyHTMLParser()
parser.feed(htmlFeed)
classes = removeDuplicates(classes)
stylesheet = readCSS('styling.CSS')
##
selector_string = stylesheet.rules[0].selector.as_css()
selectors = cssselect.parse(selector_string)
##
seperatedRules = seperateRules(stylesheet)
# print(seperatedRules)
# print(len(seperatedRules))

    