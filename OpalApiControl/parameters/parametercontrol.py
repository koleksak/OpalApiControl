#***************************************************************************************
#Description
# Allows control of parameter values
#
#***************************************************************************************


#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.config import *


#***************************************************************************************
# Globals
#***************************************************************************************




#***************************************************************************************
# Main
#*******


def showParameterValues():
    """Displays a list of Parameters By Name, ID, and Value
    """

    parameterList = list(OpalApiPy.GetParametersDescription())

    # print(parameterList
    count = 0
    paramIDList = []
    paramValues = []
    while(count < len(parameterList)):
        paramID, path, paramName, varName, value,void = parameterList[count]
        paramIDList.append(paramID)
        paramValues.append(value)
        count +=1
        print("ParameterName:{}  ID:{} VariableName:{}  Value:{}".format(path,paramID,varName,value))


def setParameterValues(paramIDS,values):
    """Takes either two single integers as inputs,
    or a tuple of IDS, and a tuple of Values.
    Usage:
        setParameterValues(int1,int2)

        or:

        paramIds = (1,2,3)
        values = (value1,value2,value3)
        setParameterValues(paramIds,values)
    """
    # try:
    if(isinstance(paramIDS,int) & (isinstance(values,float) | (isinstance(values,int)))):
        valuePair = ((paramIDS,values),(paramIDS,values))
        OpalApiPy.SetParameters(tuple(valuePair))

    elif(len(paramIDS)) == len(values):

        OpalApiPy.GetParameterControl(0)

        valuePairsDict = dict.fromkeys(paramIDS)
        num = 0
        for item in values:
            valuePairsDict[paramIDS[num]] = item
            num +=1

        valuePairsTup = valuePairsDict.items()
        OpalApiPy.SetParameters(tuple(valuePairsTup))


        # print("Error: Number of IDS must match number of values")


    # finally:
        # Releases parameter control when finished
    #     OpalApiPy.GetParameterControl(0)

def getParametersDict():
    """Returns a Dictionary of key-value(ID,VALUE) for each parameter in the connected model"""

    parameterList = list(OpalApiPy.GetParametersDescription())

    count = 0
    paramIDList = []
    paramValues = []
    while (count < len(parameterList)):
        paramID, path, paramName, varName, value, void = parameterList[count]
        paramIDList.append(paramID)
        paramValues.append(value)
        count += 1

    num = 1
    paramDict = dict.fromkeys(paramIDList)
    for item in paramValues:
        paramDict[num] = item
        num += 1


    return paramDict

