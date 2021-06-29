from pprint import pprint
import cssutils
from html.entities import name2codepoint
import tinycss
import cssselect
from html.parser import HTMLParser
import urllib.request
import chardet
import validators
import os




class Optomize():
    def __init__(self, html_path, css_file):
        self.html_path = html_path
        self.css_file = css_file
        self.classes = []
        self.html_file_name = ""
    
    def read_html(self):
        with open(os.getcwd()+"/optomize/files/"+self.html_file_name+".html", 'r') as file:
            htmlFeed = file.read().replace('\n', '')
        return htmlFeed


    ## Remove Duplicates from the classes list using a set function
    def removeDuplicates(self, classes):
        classes = list(set(classes))
        return classes

    ## Read in CSS
    def readCSS(self, fileName):
        with open(fileName, 'r') as file:
            CSSFeed = file.read().replace('\n', '')
        stylesheet = tinycss.make_parser().parse_stylesheet(CSSFeed)
        return stylesheet

    ## Split CSS by @ Rules
    def seperateAtRules(self, fileName):
        listOfQueries = []
        with open(fileName, 'r') as file:
            NewFeed = file.read().replace('\n','')
        seperated = NewFeed.split('@')
        for z in range(1,len(seperated)):
            returnedAtText = self.returnAtText(seperated[z])
            if returnedAtText == "NestedRule":
                if z == len(seperated)-1:
                    seperated[z] =  seperated[z] + ' }'
                    listOfQueries.append('@'+self.returnAtText(seperated[z]))
                else:
                    addition = seperated[z+1]
                    seperated[z+1] = seperated[z] + " @" + addition
            else:
                listOfQueries.append('@'+returnedAtText)
        return listOfQueries

    ## Clean and return @ Rule
    def returnAtText(self, seperatedByAt):
        counter = 0
        returnText = ''
        queryOpened = False
        RuleOpened = False
        for i in range(0,len(seperatedByAt)):
            if seperatedByAt[i] == ';':
                queryOpened = True
            if seperatedByAt[i] == '{':
                counter+=1
                RuleOpened= True
            elif seperatedByAt[i] == '}':
                counter-=1
            returnText = returnText + seperatedByAt[i]
            if counter == 0 and queryOpened == True and RuleOpened == True:
                break
        if counter != 0 and queryOpened == True and RuleOpened == True:
            return ("NestedRule")
        return returnText



    ## Check rules for any ',' for extra rules.
    # return list with complex rules for further processing
    def seperateByComma(self, stylesheet, i):
        rule = stylesheet.rules[i].selector.as_css()
        rules = rule.split(',')
        if '' in rules:
            rules.remove('') 
        return rules

    ## Check rules for any ' ' decendant selectors
    # Return Dict with descendants
    def checkForDescendants(self, rulesCommaSeperated):
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
    def checkForPseudoSelector(self, rulesDescendantSeperated):
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
    def checkForAdjecentSelector(self, rulesPseudoSeperated):
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
    def removePeriodHashFromRuleName(self, rulesAdjecentSeperated):
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
    def seperatedRules(self, stylesheet, i):
        rulesCommaSeperated = self.seperateByComma(stylesheet, i)
        rulesDescendantSeperated = self.checkForDescendants(rulesCommaSeperated)
        rulesPseudoSeperated = self.checkForPseudoSelector(rulesDescendantSeperated)
        rulesAdjecentSeperated = self.checkForAdjecentSelector(rulesPseudoSeperated)
        rules = self.removePeriodHashFromRuleName(rulesAdjecentSeperated)
        return rules

        


    ## add name value in dictionary and collect in list
    def nameAndValue(self, stylesheet, i):
        nameValueList = []
        for n in range(0,len(stylesheet.rules[i].declarations)):
            nameValueDict = {
                "name":stylesheet.rules[i].declarations[n].name,
                "value": stylesheet.rules[i].declarations[n].value.as_css()
            }
            nameValueList.append(nameValueDict)
        return nameValueList

    ## Return complete CSS Dict    
    def rulesNamesLabelsTuple(self, stylesheet):
        CSSList = []
        for i in range(0,len(stylesheet.rules)):
            CSSDict = {
            "rules": [],
            "functions": {},
            }
            CSSDict["rules"]=self.seperatedRules(stylesheet, i)
            CSSDict["functions"]=self.nameAndValue(stylesheet, i)
            CSSList.append(CSSDict)
            # print(str(i)+"\n")
            # print(CSSList[i])
            # print("\n")
        return CSSList

    ## Find matching classes
    def findMatchingClasses(self, CSSList, classes):
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
    def getRules(self, matchingClass):
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
        




    def getFunction(self, matchingClass):
        functionString=""
        for i in range(0,len(matchingClass['functions'])):
            functionName = matchingClass['functions'][i]['name']
            functionValue = matchingClass['functions'][i]['value']

            functionString = functionString + functionName
            functionString = functionString + " : " + functionValue + ";"
        return functionString + "}"




    def returnMatchingCSS(self, MatchingClasses, ListOfAtRules):
        CSS = []
        giantCSS_String = ""
        for i in range(0,len(MatchingClasses)):
            rule = self.getRules(MatchingClasses[i])
            function = self.getFunction(MatchingClasses[i])
            RuleAndFunction = rule + function
            giantCSS_String = giantCSS_String + RuleAndFunction + " \n"
            CSS.append(RuleAndFunction)
        for z in range(0,len(ListOfAtRules)):
            giantCSS_String = giantCSS_String + ListOfAtRules[z] + " \n"
        f = open("optomize/files/results.css", "w")
        f.write(giantCSS_String)
        f.close()
        return CSS

    def process_url(self, html_url):
        if(html_url.find('http') == -1 and html_url.find('www') != -1):
            html_url = 'https://'+html_url
        elif(html_url.find('http') == -1 and html_url.find('www') == -1):
            html_url = 'https://www.' + html_url
        return html_url


    def create_html_file(self):
        html_url = self.process_url(self.html_path)
        if validators.url(html_url):
            try:
                html_file_bytes = urllib.request.urlopen(html_url)
                html_byte_array = html_file_bytes.read()
                encoding_type = chardet.detect(html_byte_array)
                html_str = html_byte_array.decode(encoding_type['encoding'])
                split_arr = self.html_path.split(".")
                self.html_file_name = split_arr[1]
                html_write = open(os.getcwd()+"/optomize/files/"+self.html_file_name+".html", "w")
                html_write.write(html_str)
                html_write.close()
                html_file_bytes.close()
            except Exception as e:
                print(e)
        else:
            print("Error: Incorrect url format")

    def reset_vars(self):
        self.html_path = ""
        self.css_file = ""
        self.classes = []
        self.html_file_name = ""

    def run(self):
        changes = []
        self.create_html_file()
        parser = MyHTMLParser()
        htmlFeed = self.read_html()
        parser.feed(htmlFeed)
        classes = parser.classes
        print("LENGTH OF CLASSES = ",len(classes))
        classes_b = self.removeDuplicates(classes)
        stylesheet = self.readCSS(self.css_file)
        CSSList = self.rulesNamesLabelsTuple(stylesheet)
        MatchingClasses = self.findMatchingClasses(CSSList, classes_b)
        ListOfAtRules = self.seperateAtRules(self.css_file)
        MatchingCSS = self.returnMatchingCSS(MatchingClasses, ListOfAtRules)

        changes.append("Total number of rules in CSS file = "+ str(len(CSSList)))
        changes.append("Total number of classes and ID in HTML file = "+str(len(classes_b)))
        changes.append("Total number of matching classes/rules in the CSS file = "+ str(len(MatchingClasses)))
        changes.append("Total number of @ links bypassed = "+str(len(ListOfAtRules)))
        os.remove(os.getcwd()+"/optomize/files/"+self.html_file_name+".html")
        self.reset_vars()
        del parser
        


        return({"results": MatchingCSS, 'changes': changes})



#Read in html tags
#Choose only tags that contain class and id
class MyHTMLParser(HTMLParser):
    classes=[]
    def handle_starttag(self, tag, attrs):
        for n in range (0,len(attrs)):
            if attrs[n][0] == 'class' or attrs[n][0] == 'id':
                attrList = attrs[n][1].split()
                for i in attrList:
                    self.classes.append(i)



