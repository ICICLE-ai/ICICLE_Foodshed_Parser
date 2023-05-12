from pdb import set_trace as bp
import json
import sys

def command_to_dict(command):
    command_dict = {}
    for pair in command.split(" "):
        split_idx = -1
        if pair.startswith("add") or pair.startswith("remove"):
            key = "cmd"
            value = pair.strip()
        elif pair.startswith("type"):
            key = "type"
            split_idx = pair.rfind(":")
            value = pair[split_idx + 1:].strip()
        elif pair.startswith("near"):
            key = "location"
            split_idx = pair.rfind(":")
            street1 = pair[split_idx + 1:].strip()
            trunc = pair[:split_idx]
            split_idx = trunc.rfind(":")
            street2 = trunc[split_idx + 1:].strip()
            value = [street1, street2]
        elif pair.startswith("quantity"):
            split_idx = pair.rfind(":")
            key = "Qt"
            value = int(pair[split_idx + 1:].strip())
        elif pair.startswith("att:hasCar"):
            split_idx = pair.rfind(":")
            key = "hasCar"
            value = bool(pair[split_idx + 1:].strip())
        elif pair.startswith("att:resource"):
            split_idx = pair.rfind(":")
            key = "resource"
            try:
                value = int(pair[split_idx + 1:].strip())
            except ValueError:
                value = pair[split_idx + 1:].strip()
        else:
            raise Exception("Cannot identify " + pair)

        command_dict[key] = value
    return command_dict

def toCommand(canonStr):
    def getLocation(toks):
        location = ['near']
        locPhrase = " ".join(toks[:3])
        if 'the corner of' in locPhrase:
            location.append('corner_of')
            toks = toks[3:]
            andIdx = toks.index('and')
            firstStreet = "_".join(toks[:andIdx])
            location.append(firstStreet)
            toks = toks[andIdx+1:]
            secondStreet = "_".join(toks)
            location.append(secondStreet)
        else:
            location.append("_".join(toks))
        toks = []
        location = ":".join(location)
        return (location, toks)

    def getAtt(toks):
        attBuilder = ['att']
        attEndIdx = len(toks)
        for idx, tok in enumerate(toks):
            if tok in {'and', 'near', 'with'}:
                attEndIdx = idx
                break
        attToks = toks[:attEndIdx]
        toks = toks[min(attEndIdx+1, len(toks)):]
        if 'resource' in attToks or 'income' in attToks:
            attBuilder.append('resource')
            if attToks[-1].isnumeric():
                attBuilder.append(str(attToks[-1]))
            else:
                attBuilder.append(attToks[0])
        if 'car' in attToks:
            attBuilder.append('hasCar')
            if 'no' in attToks:
                attBuilder.append('True')
            else:
                attBuilder.append('False')
        attString = ":".join(attBuilder)
        return(attString, toks)

    canonList = canonStr.strip().split()
    command = canonList.pop(0)
    
    quantity = canonList.pop(0)
    if quantity == 'a':
        quantity = 1
    quantityStr = ":".join(['quantity', str(quantity)])
    
    objType = canonList.pop(0)
    typeList = ['type']
    if objType in {'spm', 'csmp'}:
        typeList.append('market')
    typeList.append(objType)
    typeStr = ":".join(typeList)

    atts = []
    location = False
    while len(canonList) > 0:
        nextTok = canonList.pop(0)
        if 'near' in nextTok:
            location, canonList = getLocation(canonList)
        if 'with' in nextTok:
            att, canonList = getAtt(canonList)
            atts.append(att)
    
    if objType == 'household':
        hasCarFlag = False
        hasResourceFlag = False
        for att in atts:
            if ':resource' in att:
                hasResourceFlag = True
            if ':hasCar' in att:
                hasCarFlag = True
        
        if not hasCarFlag:
            atts.append('att:hasCar:Default')
        if not hasResourceFlag:
            atts.append('att:resource:Default')
    
    outCommand = [command, typeStr]
    outCommand.extend(atts)
    if location != False:
        outCommand.append(location)
    outCommand.append(quantityStr)
    outCommandStr = " ".join(outCommand)
    return outCommandStr

def readLog(logFile):
    testSents = []
    fullTest = dict()
    candidate = False
    with open(logFile, 'r') as fin:
        for line in fin.readlines():
            if "Completion" in line:
                if candidate != False:
                    candidate = candidate.split('<s>')[-1]
                    candidate = candidate.split('[')
                    candidateScore = float(candidate[-1].strip()[:-2])
                    candidateSent = candidate[0].strip()[:-1]
                    candidateList = [candidateSent, candidateScore]
                    testSents.append(candidateList)
                candidate = line.strip()
            if '->' in line:
                candidate = False
            if 'natural:' in line:
                naturalLine = line.split('natural:')[-1].strip()
                testSents.sort(key=lambda x: x[1])
                fullTest[naturalLine] = [testSents]
            if 'gold:' in line:
                goldLine = line.split('gold:')[-1].strip()
                fullTest[naturalLine].append(goldLine)
    return fullTest

def prettyPrint(candidates):
    headers = ['Rank', 'Candidate Command', 'Uncertainty Score']
    candidates = candidates[:5]
    for idx, candidate in enumerate(candidates):
        candidate.insert(0, idx+1)
    print('\n')
    print('{:<10} {:<50} {:<20}'.format(*headers))
    for candidate in candidates:
        print('{:<10} {:<50} {:<20}'.format(*candidate))
    print('\n')
    

def canonToCmd(example, inFile = False):
    def parseLocation(locationString):
        if 'corner ' in locationString:
            locationString = locationString.replace('the corner of', '')
            streets = locationString.split(' and ')
            return streets
        return locationString

    allCommands = []
    sents = example.split('. ')
    for sent in sents:
        commandDict = False
        if "Add " in sent:
            location = "Default"
            if ' near ' in sent:
                location = sent.split(' near ')[-1].strip()
            sent = sent.split()
            qty = sent[1]
            obj = sent[2]
            commandDict = {'type': 'add', 'qty': qty, 'obj': obj, 'location': location}
        elif "Remove " in sent:
            location = "Default"
            if ' near ' in sent:
                location = sent.split(' near ')[-1].strip()
            sent = sent.split()
            qty = sent[1]
            obj = sent[2]
            commandDict = {'type': 'remove', 'qty': qty, 'obj': obj, 'location': location}
        elif "Modify " in sent:
            qty = 1
            attribute = 'food_availability'
            changeType = 'set'
            targetValue = 'Default'
            location = 'Default'
            sent = sent.split(' by ')
            modifier = sent[1:]
            sent = sent[0]
            if ' resources' in modifier[0]:
                attribute = 'resources'
            if len(modifier) > 1:
                targetValue = modifier[-1].strip()
                modifier = modifier[0].split()
                changeType = modifier[0]
            else:
                modifier = modifier[0].split()
                targetValue = modifier[-1]
            if ' near ' in sent:
                sent = sent.split(' near ')
                location = sent[-1].strip()
                sent = sent[0].strip()
            sent = sent.split()
            qty = sent[1].strip()
            obj = sent[2].strip()
            commandDict = {'type': 'modify', 'qty':qty, 'obj': obj, 'location': location, 'attribute':attribute, 'changeType':changeType, 'targetValue':targetValue}
        elif "Convert " in sent:
            sent = sent.split(' to ')
            target = sent[-1]
            sent = sent[0]
            location = "Default"
            if ' near ' in sent:
                sent = sent.split(' near ')
                location = sent[-1].strip()
                sent = sent[0].strip()
            sent = sent.split()
            qty = sent[1]
            source = sent[2]
            commandDict = {'type': 'convert', 'qty': qty, 'source': source, 'target': target, 'location':location}
        elif "Compare the " in sent:
            commandDict = {'type': 'Compare', 'subject': 'reported_values'}
            if "executions" in sent:
                commandDict['subject'] = 'executions'
            if 'accumulation' in sent:
                commandDict['accumulate'] = True
        elif "until a relative " in sent:
            accumulate = False
            if 'accumulation' in sent:
                sent = sent.replace(' with accumulation', '')
                accumulate = True
            sent = sent.replace('Continue until a relative', '')
            sent = sent.replace('of food availability by', '')
            sent = sent.split()
            percentage = sent[1]
            direction = sent[0]
            commandDict = {'type': 'grid', 'percentage_change':percentage, 'change_direction': direction, 'accumulate': accumulate}
        elif "Report " in sent:
            commandDict = {'type': 'report', 'subject': 'Default'}
            if ' over ' in sent:
                subject = sent.split(' over ')[-1].strip()
                commandDict['subject'] = subject
            value = sent.split()[1]
            commandDict['value'] = value.strip()
        elif 'Run within scope of ' in sent:
            zone = 'Default'
            time = 'Default'
            sent = sent.replace('Run within scope of ', '')
            if ' and ' in sent:
                sent = sent.split('and')
                zone = " ".join(sent[0].split()[:-1])
                time = sent[-1].split()[-2]
            else:
                sent = sent.split()
                if 'weeks' in sent[-1]:
                    time = sent[-2]
                else:
                    zone = " ".join(sent[:-1])
            commandDict = {'type': 'scope', 'zone': zone, 'time': time}
        if commandDict != False:
            allCommands.append(commandDict)
    exampleCommand = json.dumps(allCommands)

    return exampleCommand

def main():
    # What will be the impact on food availability if a new grocery store opens on Moon Road and Eisenhower Road
    testDict = readLog('tempLog.txt')
    # command = input('Enter your command:\n')
    command = sys.argv[1]
    candidates = testDict[command][0]
    prettyPrint(candidates)
    selection = input('\nSelect a command (Numerical Value):\n')
    selection = int(selection)-1
    selectedCommand = candidates[selection]
    # parsedCommand = toCommand(selectedCommand[1])
    # outDict = command_to_dict(parsedCommand)
    outDict = canonToCmd(selectedCommand[1])
    print("\nCanonical Form: " + selectedCommand[1])
    print("Output Dictionary: " + str(outDict) + "\n")
    with open('demoOutputDict.json','w') as fout:
        outLine = json.dumps(outDict)
        fout.write(outLine)
    return 0

if __name__ == "__main__":
    main()