import re
import os
import argparse

prepareForTestRegex = "@PrepareForTest\s*\(\{?[\s\S]*?\}?\)"
prepareForTestClassRegexKT = '[\w\.]*::class'
prepareForTestClassRegexJava = '[\w\.]*\.class'

mockStaticClassRegexKT = "mockStatic\s*?\((.+::class)"
mockStaticClassRegexJava = "mockStatic\s*?\((.+)\)"


def getFileContentAsText(fileName):

    fileObject = open(fileName, 'r')
    fileContent = fileObject.read()
    fileObject.close()

    return fileContent


def overrideContentToFile(content, fileName):
    file = open(fileName, 'w')
    file.write(content)
    file.close()


def getPrepareForTestContentFromFileContent(fileContent):
    prepareForTestList = re.findall(prepareForTestRegex, fileContent)
    if (len(prepareForTestList) == 0):
        return ""
    else:
        return prepareForTestList[0]


def getPrepareForTestClassListFromPrepareForTestContent(prepareForTestContent, isKotlin):

    prepareForTestClassList = re.findall(prepareForTestClassRegexKT if(
        isKotlin) else prepareForTestClassRegexJava, prepareForTestContent)
    prepareForTestClassList = [classes.strip(
        " \n") for classes in prepareForTestClassList]

    return prepareForTestClassList


def getMockStaticClassListFromFileContent(fileContent, isKotin):
    mockStaticClassList = re.findall(
        mockStaticClassRegexKT if (isKotin) else mockStaticClassRegexJava, fileContent)

    return mockStaticClassList


def optimisePrepareForTestForFile(fileName):
    fileContent = getFileContentAsText(fileName)

    isKotlin = True if(fileName.split(".")[-1] == "kt") else False

    prepareForTestContent = getPrepareForTestContentFromFileContent(
        fileContent)

    prepareForTestClassList = getPrepareForTestClassListFromPrepareForTestContent(
        prepareForTestContent, isKotlin)

    mockStaticClassList = getMockStaticClassListFromFileContent(
        fileContent, isKotlin)

    classesToRemoveFromPrepareForTestClassList = list(
        set(prepareForTestClassList) - set(mockStaticClassList))

    prepareForTestContentOptimised = prepareForTestContent

    for classToRemove in classesToRemoveFromPrepareForTestClassList:
        classToRemoveRegex = classToRemove + "\s?,?"
        prepareForTestContentOptimised = re.sub(
            classToRemoveRegex, "", prepareForTestContentOptimised)

    fileContent = fileContent.replace(
        prepareForTestContent, prepareForTestContentOptimised)

    overrideContentToFile(fileContent, fileName)


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--Root",
                    help="Give the root address")
parser.add_argument("-f", "--Filepath", help="Give the full filePath")
args = parser.parse_args()

if (args.Root):
    for root, dirs, files in os.walk(args.Root):
        for file in files:
            if ((".java" in file or ".kt" in file) and ("test" in file.lower()) and ("/src/test") in root):
                fileName = os.path.join(root, file)
                print("Started optimising on "+fileName)
                optimisePrepareForTestForFile(fileName)
elif (args.Filepath):
    optimisePrepareForTestForFile(args.Filepath)
else:
    print("Oops path or root not provided")
