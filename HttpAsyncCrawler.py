"""HttpAsyncRequests.py"""

__author__      = "E. Dimogerontakis, M. Orazow, H. Sang"
__copyright__   = "http://creativecommons.org/licenses/by-sa/3.0/"


import urllib2
import re
import requests
import grequests
from unicodedata import normalize
from time import gmtime, strftime


#Start connection with server and set
#initial parameters
api_key = 'bd29aa9bb83d795b55ea2a00c063e84a'
server = "http://ws.audioscrobbler.com/2.0/"
user = "rj"
limit = 500
maxusers = 50000000
marked = set(user)


def getFriendsReq(user,page):
    """Make a getFriends request to the server"""
    command = server+"?method=user.getfriends&"+\
        "user="+user+"&limit="+str(limit)+"&page="+str(page)+"&api_key="+api_key 
    
    data = urllib2.urlopen(command).read()      # XML format
    try :
        errors = re.findall("<error>(.*)</error>", data)
    except HTTPError,e:
        print e.reason
    # Error Handling
    # Redo the request if no answer due to error of server or connection
    # Should be in the lowest level of request
    while len(errors) > 0 :
        print errors
        command = server+"?method=user.getfriends&"+\
            "user="+user+"&limit="+str(limit)+"&page="+str(page)+"&api_key="+api_key 
        data = urllib2.urlopen(command).read()      # XML format
        errors = re.findall("<error>(.*)</error>", data)
    return data


def getFriends(user):
    """Get results from of friends from all pages"""
    data = getFriendsReq(user,1) 
    degree = int(re.search('total="(\d+)"', data).group(1))
    friends = re.findall("<name>(.*)</name>", data)
    # In case we have to read more than one pages
    if degree > limit :
        pagesnum = degree/limit+1
        for x in range(2,pagesnum+1) :
            data = getFriendsReq(user,x)
            friends1 = re.findall("<name>(.*)</name>", data)
            friends += friends1
    return degree,friends


def prepReq(user,page) :
    command = server+"?method=user.getfriends&"+\
        "user="+str(user)+"&limit="+str(limit)+"&page="+str(page)+"&api_key="+api_key
    return command


def getResp(reply) :
    if not reply.text : # Bypass empty reply from grequests
        return 0,'none'
    resp = normalize('NFKD',reply.text).encode('ascii','ignore').strip('[]')
    degree = getDegree(resp)
    return degree, resp

def getNames(res) :
    return re.findall("<name>(.*)</name>",res)

def getDegree(res) :
     return int(re.search('total="(\d+)"', res).group(1))
    
def getUser(res) :
    return re.findall('<friends for="(.*)" page',res)

def ser(l) :
    if l :
        return l[0]+ser(l[1:])
    else :
        return []

# handle the outcome of each request
def handler(res, d) :
    user = getUser(res)
    friends = getNames(res)
    if d > limit :
        pagesnum = d/limit+1
        for x in range(2,pagesnum+1) :
            friends1 = getNames(normalize('NFKD',requests.get(prepReq(user[0],x)).text).encode('ascii','ignore').strip('[]'))
            friends += friends1
    return friends


def bfs(root,f) :
    """ Run bfs using Grequests"""
    countzeros = 0
    degree,tosearch = getFriends(root)
    SumK = degree
    N = 1
    out = str(N)+','+str(SumK/N)+','+str(degree)
    f.write('%s\n' %out)
    page = 1
    level =0
    while N < maxusers :
        print strftime("%Y-%m-%d %H:%M:%S", gmtime())
        level = level + 1
        print "Start of level: " +str(level)
        marked.union(set(tosearch))
        # Fix urls
        urls = map(prepReq,tosearch,[1]*len(tosearch))
        # Prepare requests
        reqs = (grequests.get(u) for u in urls)
        tosearch = []
        for req in grequests.map(reqs,prefetch=True, size=1000):
            degree, resp =  getResp(req)
            if degree == 0 :
                countzeros = countzeros + 1
                continue
            N = N + 1
            SumK += degree
            out = str(N)+','+str(SumK/N)+','+str(degree)
            f.write('%s\n' %out)
            resp1 = handler(resp, degree)
            resp2 = filter(lambda x: x not in marked, resp1)
            tosearch += resp2
            marked.union(set(resp2))
        print "\nUsers checked: "+str(N)
        print "Average Degree: "+str(SumK/N)
        print "Total known users: "+str(N+len(tosearch))
        print "Total zeros: "+str(countzeros)
        print "\nEnd of level "+str(level)+'\n\n\n'
    return N, tosearch
    

if __name__ == "__main__":
    f = open('results','w')
    N, tosearch = bfs(user,f)
    f.close()
    print "Size of graph: "+str(N)
    print len(tosearch)


