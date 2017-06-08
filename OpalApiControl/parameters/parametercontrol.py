#***************************************************************************************
#Description
# Accesses parameter signals in RT-Lab. Parameter Signals are defined in the sm_master
# of RT-Lab and have values that are predefined in model development.  This module allows for
# the dynamic changing, reading and viewing of parameters through the Opal RT-Lab API functions
#
#***************************************************************************************


#***************************************************************************************
# Modules
#***************************************************************************************
import OpalApiPy


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
        # Sets Parameter value if Only one Signal Id and Value are input
        valuePair = ((paramIDS,values),(paramIDS,values))
        OpalApiPy.SetParameters(tuple(valuePair))

    elif(len(paramIDS)) == len(values):
        # Sets Parameter Values for groupings of Signal Id's and Value's

        # Allows access to Parameter Control of API call
        OpalApiPy.GetParameterControl(0)

        # Converts user input Value and Signal Id's into a dictionary for  key=ID arg=value pairing
        # and then the dictionary is converted to a tuple for proper RT-Lab API function input
        valuePairsDict = dict.fromkeys(paramIDS)
        num = 0
        for item in values:
            valuePairsDict[paramIDS[num]] = item
            num +=1

        valuePairsTup = valuePairsDict.items()
        OpalApiPy.SetParameters(tuple(valuePairsTup))
        #Releases parameter control when finished
        OpalApiPy.GetParameterControl(0)
    else:
        print"error:Proper ID, Value Pair not given."

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

