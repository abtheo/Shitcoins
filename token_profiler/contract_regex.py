import re

contractPattern = re.compile(r'0x[\da-f]{40}', flags=re.IGNORECASE)

while(True):
    print("Enter some text: ")
    contract = input()
    print("You entered: " + contract)
    matches = contractPattern.findall(contract) # returns list of groups
    print("Number of matches: " + str(len(matches)))
    for g in matches:
        print(g)
