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

## Split CSS by @ Rules
def seperateAtRules(fileName):
    listOfQueries = []
    with open(fileName, 'r') as file:
        NewFeed = file.read().replace('\n','')
    seperated = NewFeed.split('@')
    for z in range(1,len(seperated)):
        listOfQueries.append('@'+returnAtText(seperated[z]))
    return listOfQueries

## Clean and return @ Rule
def returnAtText(seperatedByAt):
    counter = 0
    returnText = ''
    queryOpened = False
    for i in range(0,len(seperatedByAt)):
        if seperatedByAt[i] == '{':
            queryOpened = True
            counter+=1
        elif seperatedByAt[i] == '}':
            counter-=1
        returnText = returnText + seperatedByAt[i]
        if counter == 0 and queryOpened == True:
            break
    return returnText



## Check rules for any ',' for extra rules.
# return list with complex rules for further processing
def seperateByComma(stylesheet, i):
    rule = stylesheet.rules[i].selector.as_css()
    rules = rule.split(',')
    if '' in rules:
        rules.remove('') 
    return rules

## Check rules for any ' ' decendant selectors
# Return Dict with descendants
def checkForDescendants(rulesCommaSeperated):
    # returnList = []
    for i in range(0,len(rulesCommaSeperated)):
        selectedRule = []
        selectedRule.append(rulesCommaSeperated[i])
        selectedRule[0] = selectedRule[0].lstrip()
        selectedRule = selectedRule[0].split(' ')
        if(len(selectedRule) == 1):
            rulesCommaSeperated[i] = {"ruleName": selectedRule[0],
            "descendants": False}
        elif len(selectedRule) > 1:
            rulesCommaSeperated[i] = {"ruleName": selectedRule[0],
            "descendants": selectedRule[1:]}
        else: 
            rulesCommaSeperated.remove[i]
            # rulesCommaSeperated[i] = {"ruleName": selectedRule[0],
            # "descendants": False,
            # "error": True}
    return rulesCommaSeperated

## Check rules for any ':' pseudo selectors
# Return Dict with pseudo Selector 
def checkForPseudoSelector(rulesDescendantSeperated):
    for i in range(0,len(rulesDescendantSeperated)):
        ruleName = rulesDescendantSeperated[i]["ruleName"]
        ruleNameSplit = ruleName.split(":")
        if ruleNameSplit[0] == '':
            rulesDescendantSeperated[i]['pseudoSelectors'] = False
            pass
        else:
            if len(ruleNameSplit) > 1:
                rulesDescendantSeperated[i]['ruleName'] = ruleNameSplit[0]
                rulesDescendantSeperated[i]['pseudoSelectors'] = ruleNameSplit[1]
            else:
                rulesDescendantSeperated[i]['pseudoSelectors'] = False
    return rulesDescendantSeperated

## check rules for any '+' adjecant sibling selectors
# return Dict with adject Selectors
def checkForAdjecentSelector(rulesPseudoSeperated):
    for i in range(0,len(rulesPseudoSeperated)):
        ruleName = rulesPseudoSeperated[i]['ruleName']
        ruleNameSplit = ruleName.split("+")
        if len(ruleNameSplit) > 1:
            rulesPseudoSeperated[i]['ruleName'] = ruleNameSplit[0]
            rulesPseudoSeperated[i]['adjecentSelectors'] = ruleNameSplit[1]
        else:
            rulesPseudoSeperated[i]['adjecentSelectors'] = False
    return rulesPseudoSeperated

## Remove '.' or '# from ruleName
# return Dict with proper class name and selectorType
def removePeriodHashFromRuleName(rulesAdjecentSeperated):
    for i in range(0,len(rulesAdjecentSeperated)):
        ruleName = rulesAdjecentSeperated[i]['ruleName']
        if(ruleName[0] == '.'):
            RuleNamePeriod  = rulesAdjecentSeperated[i]['ruleName']
            RuleNamePeriodSplit = RuleNamePeriod.split('.')
            rulesAdjecentSeperated[i]['ruleName'] = RuleNamePeriodSplit[1]
            rulesAdjecentSeperated[i]['selectorType'] = "class"
        elif(ruleName[0] == '#'):
            RuleNameHash  = rulesAdjecentSeperated[i]['ruleName']
            RuleNameHashSplit = RuleNameHash.split('#')
            rulesAdjecentSeperated[i]['ruleName'] = RuleNameHashSplit[1]
            rulesAdjecentSeperated[i]['selectorType'] = "id"
        elif(ruleName[0]=='@'):
            print("Found an @")
        else:
            ## Seperate Tag name and rule name
            RuleNameTag  = rulesAdjecentSeperated[i]['ruleName']
            rulesAdjecentSeperated[i]['selectorType'] = "tag"
            ruleNamePeriodSplit = RuleNameTag.split(".")
            if len(ruleNamePeriodSplit) < 2:
                rulesAdjecentSeperated[i]['tagName'] = False
                rulesAdjecentSeperated[i]['ruleName'] = ruleNamePeriodSplit[0]
            else:
                rulesAdjecentSeperated[i]['tagName'] = ruleNamePeriodSplit[0]
                rulesAdjecentSeperated[i]['ruleName'] = ruleNamePeriodSplit[1]
    return rulesAdjecentSeperated

## Check rules for any ',' for extra rules.
## Check rules for any ' ' decendant selectors
## Check rules for any ':' pseudo selectors
## Check rules for any '+' adjecant sibling selectors
## Remove '.' or '# from ruleName
## Return properly split rules dict

## Game Plan
# 1. Seperate the rules by ','
# 2. Look for any descendants
# 3. Look for any pseudo selectors
# 4. Look for any adjacent siblings
# 5. Remove class '.' or '#' from the ruleName
def seperatedRules(stylesheet, i):
    rulesCommaSeperated = seperateByComma(stylesheet, i)
    rulesDescendantSeperated = checkForDescendants(rulesCommaSeperated)
    rulesPseudoSeperated = checkForPseudoSelector(rulesDescendantSeperated)
    rulesAdjecentSeperated = checkForAdjecentSelector(rulesPseudoSeperated)
    rules = removePeriodHashFromRuleName(rulesAdjecentSeperated)
    return rules

    


## add name value in dictionary and collect in list
def nameAndValue(stylesheet, i):
    nameValueList = []
    for n in range(0,len(stylesheet.rules[i].declarations)):
        nameValueDict = {
            "name":stylesheet.rules[i].declarations[n].name,
            "value": stylesheet.rules[i].declarations[n].value.as_css()
        }
        nameValueList.append(nameValueDict)
    return nameValueList

## Return complete CSS Dict    
def rulesNamesLabelsTuple(stylesheet):
    CSSList = []
    for i in range(0,len(stylesheet.rules)):
        CSSDict = {
        "rules": [],
        "functions": {},
        }
        CSSDict["rules"]=seperatedRules(stylesheet, i)
        CSSDict["functions"]=nameAndValue(stylesheet, i)
        CSSList.append(CSSDict)
        # print(str(i)+"\n")
        # print(CSSList[i])
        # print("\n")
    return CSSList

## Find matching classes
def findMatchingClasses(CSSList, classes):
    matchingList = []
    for i in range(0,len(classes)):
        for n in range(0,len(CSSList)):
            rulesList = CSSList[n]['rules']
            for z in range(0,len(rulesList)):
                CSSruleName = rulesList[z]['ruleName']
                htmlRuleName = classes[i]
                if CSSruleName == htmlRuleName:
                    matchingList.append(CSSList[n])
    
    for p in range(0,len(CSSList)):
        rulesList = CSSList[p]['rules']
        for l in range(0,len(rulesList)):
            if rulesList[l]['selectorType'] == 'tag':
                matchingList.append(CSSList[p])
        
    return matchingList

## Return matching rules in CSS format plus "{"
def getRules(matchingClass):
    ruleString=""
    for z in range(0,len(matchingClass['rules'])):
        if(z > 0):
            ruleString = ruleString + " , "
        selectorType = matchingClass['rules'][z]['selectorType']
        ruleName = matchingClass['rules'][z]['ruleName']
        pseudoSelectors = matchingClass['rules'][z]['pseudoSelectors']
        descendants = matchingClass['rules'][z]['descendants']
        adjecentSelectors = matchingClass['rules'][z]['adjecentSelectors']
        if selectorType == "class":
            ruleString = ruleString + "."
            ruleString = ruleString + ruleName
        elif selectorType == "id":
            ruleString = ruleString + "#"
            ruleString = ruleString + ruleName
        elif selectorType == "tag":
            if matchingClass['rules'][z]["tagName"] == False:
                ruleString = ruleString + ruleName
            else:
                ruleString = ruleString + matchingClass['rules'][z]["tagName"] + "."
                ruleString = ruleString + ruleName
        else:
            ruleString = ruleString + "."
            ruleString = ruleString + ruleName

        
        
        if pseudoSelectors == False:
            pass
        else:
            ruleString = ruleString + ":"
            ruleString = ruleString + pseudoSelectors
        
        if adjecentSelectors == False:
            pass
        else:
            ruleString = ruleString + "+"
            ruleString = ruleString + adjecentSelectors
        
        if descendants == False:
            pass
        else:
            for n in range(0,len(descendants)):
                ruleString = ruleString + " " + descendants[n]
    
    return ruleString + " { "
    




def getFunction(matchingClass):
    functionString=""
    for i in range(0,len(matchingClass['functions'])):
        functionName = matchingClass['functions'][i]['name']
        functionValue = matchingClass['functions'][i]['value']

        functionString = functionString + functionName
        functionString = functionString + " : " + functionValue + ";"
    return functionString + "}"




def returnMatchingCSS(MatchingClasses, ListOfAtRules):
    CSS = []
    giantCSS_String = ""
    for i in range(0,len(MatchingClasses)):
        rule = getRules(MatchingClasses[i])
        function = getFunction(MatchingClasses[i])
        RuleAndFunction = rule + function
        giantCSS_String = giantCSS_String + RuleAndFunction + " \n"
        CSS.append(RuleAndFunction)
    for z in range(0,len(ListOfAtRules)):
        giantCSS_String = giantCSS_String + ListOfAtRules[z] + " \n"
    f = open("results.CSS", "w")
    f.write(giantCSS_String)
    f.close()
    return CSS
    


parser = MyHTMLParser()
parser.feed(htmlFeed)
classes = removeDuplicates(classes)
stylesheet = readCSS('styling.CSS')
CSSList = rulesNamesLabelsTuple(stylesheet)
MatchingClasses = findMatchingClasses(CSSList, classes)
ListOfAtRules = seperateAtRules('styling.CSS')
MatchingCSS = returnMatchingCSS(MatchingClasses, ListOfAtRules)
print("Total number of rules in CSS file = "+ str(len(CSSList)))
print("Total number of classes and ID in HTML file = "+str(len(classes)))
print("Total number of matching classes/rules in the CSS file = "+ str(len(MatchingClasses)))
print("Total number of @ links bypassed = "+str(len(ListOfAtRules)))

