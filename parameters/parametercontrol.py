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
    """

    :return: Dictionary of key-value(ID,Value) paramater pairs
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
        print("ParameterName:{}  ID:{} VariableName:{}  Value:{}".format(paramName,paramID,varName,value))

    num = 1
    paramDict = dict.fromkeys(paramIDList)
    for item in paramValues:
        paramDict[num] = item
        num += 1


    return paramDict


def setParameterValues(paramIDS,values):
    """

    """
    try:
        if(len(paramIDS)) == len(values):

            OpalApiPy.GetParameterControl(0)

            valuePairsDict = dict.fromkeys(paramIDS)
            num = 0
            for item in values:
                valuePairsDict[paramIDS[num]] = item
                num +=1

            valuePairsTup = valuePairsDict.items()
            OpalApiPy.SetParameters(tuple(valuePairsTup))

    except:
        print("Error: Number of IDS must match number of values")


    finally:
        # Releases parameter control when finished
        OpalApiPy.GetParameterControl(0)