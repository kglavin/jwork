#
#  Module inspired by SPELL paper
#  parses logfiles into a set of messages with wildcarding for the positions
#  within the messages where this is expected differences.
#
#  These differences are the parameterizatoin of the log message into its generic form.
#
#



class LCSObject:
    """ spellpaper  LCS object
        this object holds the generalised version of the message, where elements that have been found to have 
        different values but still match the LCS(longest common subsequence)  parameter are indicated by a single * token.
        the paramVector provides a place vector into the message where these wild cards exist, this paramVector is
        used in matching operations to generate a list of paramters taken from the input log entry that is being matched 
    """
    
    def __init__(self,seq,id=0):
        self.lineIds = []
        self.paramVector = []
        self.lineIds.append(id)
        self.LCSseq = seq
        
    
    def getLCS(self,seq):
        ''' calculates the LCS value as desribed in the paper '''
        count = 0
        lastMatch = -1
        for s in self.LCSseq:
            if s == "*":
                continue
            for j in range( lastMatch +1, len(seq)):
                if s == seq[j]:
                    lastMatch = j
                    count = count+1
                    break        
        return count
    
    def insert(self,seq,id=0):
        ''' inserts a new log entry ( sequence of tokens) into this LCSseq object, 
            as this new seq is being inserted it updates the stored sequence with additional * parameters 
            as required'''
        
        sequenceIndex = 0;        
        if id is not 0:
            self.lineIds.append(id)
        t = ""
        tp = []
        lastMatch = -1
        wildcard = False
        for s in self.LCSseq:
            if s == "*":
                if wildcard == False:
                    t = t + "* "
                wildcard = True
                continue
            for j in range(lastMatch +1, len(seq)):
                if s == seq[j]:
                    wildcard = False
                    t = t + s + " "
                    lastMatch = j
                    break
                elif wildcard == False:

                    ## this is a deviation from the SPELL paper, in this implementation I dicate that the first token will not be a * element
                    ## as I use the first token to form a mini search tree in the LCSMultiMap object
                    ## try to not * the first element
                    if j > 0 :
                        t = t + "* "
                        wildcard = True
                    else:
                        t = t + s + " "
                    ##
                    #this implementation would allow first token to be *
                    #t = t + "* "
                    #wildcard = True
                    ##            
        self.LCSseq = t.split()
        # regenerate the parameter vector ( list of indexs that in the token list that have a * 
        for x in self.LCSseq:
            sequenceIndex = sequenceIndex+1
            if x == "*":
                tp.append(sequenceIndex)
        self.paramVector = tp

    def len(self):
        return(len(self.LCSseq))
        
    def count(self):
        return(len(self.lineIds))
    
    def join(self):
        return("".join(self.LCSseq))
    
    def debug(self,ident=""):
        print(ident+'LCSOBJ:lineIds num = ',len(self.lineIds))
        print(ident+'LCSOBJ:paramVector = ',len(self.paramVector), " ".join(str(x)+" " for x in self.paramVector))
        print(ident+'LCSOBJ:LCSseq = ', self.LCSseq)


        
class LCSMap:
    """ spell LCSMap object : as described in the paper, the LCSMap object holds a list of LCSObj which each hold a single token sequence."""
    
    def __init__(self):
        self.LCSObjects = []
        self.lineId = 0
        

    def insert(self,seq):
        ''' inserting a new token sequence into map, if an exising LCSObj is compatibile with this token sequence 
            then that existing LCSObj is updated otherwise a new LCSObj is created for this token sequence. '''
        obj = self.getMatch(seq)
        
        if obj != None:
            self.lineId = self.lineId + 1
            obj.insert(seq, self.lineId)
        else :
            self.lineId = self.lineId + 1
            self.LCSObjects.append(LCSObject(seq,self.lineId))

            
    ### getMatch as per the paper with /2 paramters < size of message sequence
    def getMatch(self,seq):
        ''' searchs the map for a LCSObj that is compatible with the input token sequence, if nothing is compatible is will return None'''
        match = None
        matchlen = 0
        
        for obj in self.LCSObjects:
            if (obj.len() < len(seq)/2) or (obj.len() > len(seq) *2) :
                continue    
            k = obj.getLCS(seq)
            if k  >= len(seq)/2 and k > matchlen :
                matchlen = k
                match = obj
        return match

    
    def objectAt(self,i):
        return(self.LCSObjects[i])
    
    def len(self):
        return(len(self.LCSObjects))
    
    def debug(self,ident= ""):
        did='-m--'
        print(ident+did+'LCSMap:lineId = ',self.lineId)
        for o in self.LCSObjects:
            o.debug(ident+did)

            
class LCSMultiMap:
    """ LCSMultiMap is not part of the spell paper, although it is similiar to the prefix tree search idea. 
        for this implemenation, it is expected that the first token will not be a parameter and can be used to 
        partition up the message space. 
        for example syslog messages will have a process name so this can be used as the first token and then all messages associated with this 
        process will be grouped into a single LCSMap instance. 

        in the syslog segment blow the xccd and cronimon process names would be used for this partitioning. 

        Mon Dec 11 23:14:19 2017 daemon.warn xccd[2444]: Connection handler finished
        Mon Dec 11 23:14:19 2017 daemon.warn xccd[2444]: Connection handler finished
        Mon Dec 11 23:14:24 2017 daemon.notice cronimon[2659]: Using IP 104.220.254.161 for service uplink-internet-c11129117e62259e_v4
        Mon Dec 11 23:14:42 2017 daemon.notice cronimon[2659]: Service uplink-internet-c11129117e62259e_v4 is dead

        a set of LCSMap objects that are differenticated by a uniq key thus giving us the start of a tree search for LCS objects 
        removing some of the linear searching for large number of LCSObjects, 
        the key would be a unique field 
        -- in syslog example this would be the process name/kernel so all the LCSObjects associated with a single process 
        will be in a unique LCSMap"""

    def __init__(self):
        self.LCSMaps = {}
        

    def insert(self,key,seq):
        """ insert sequence into multimap with key as the index to choose the correct instance of LCSMap to use

        for example the syslog line
        cronimon[2659]: Using IP 104.220.254.161 for service uplink-internet-c11129117e62259e_v4

        would have a key="cronimon'
        and a seq = [ '2659', 'Using', "IP", "104.220.254.161","for","service","uplink-internet-c11129117e62259e_v4"]

        mm.insert(key,seq)

        """
        map = None
        if key not in self.LCSMaps:
            map = LCSMap()
            self.LCSMaps[key] = map
            map.insert(seq)
        else:
            map = self.LCSMaps[key]
            map.insert(seq)

            
    def getMatch(self,key,seq):
        """ searches the mulimap using the key and sequence attempting to find the LCSObj that is compatible with this message/token sequence.
            will return None,None is none exists. 
            if one exists then it will return the LCSObj and will also return a sequence of tuples with the (index, value) which 
            indexs the * entries in the returned LCSObj and the associated input value from the input sequence"""
        
        ret = None
        parms = None
        map = None
        if key in self.LCSMaps:
            map = self.LCSMaps[key]
            ret = map.getMatch(seq)
            if ret is not None:
                parms=[]
                for x in ret.paramVector:
                    parms.append((x,seq[x-1]))    
        return ret, parms
            
    def debug(self,ident=""):
        did='-d---'
        for k,v in self.LCSMaps.items():
            print(ident+did+k)
            v.debug(ident+did)
            

    
    
