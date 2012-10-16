"""ParCrawler.py"""

__author__      = "M. Orazow, E. Dimogerontakis, H. Sang"
__copyright__   = "http://creativecommons.org/licenses/by-sa/3.0/"


import urllib2
import re
from threading import Thread
from collections import deque
from httplib import BadStatusLine

api_key = '7532207114f5ffc75d40b547885ea358'
server = "http://ws.audioscrobbler.com/2.0/"
user = "rj"
limit = 5000
maxusers = 1000
maxlevel = 5

def getFriendsReq(user,page):
    userName = "%20".join(user.split(' '))
    try:
        command = server+"?method=user.getfriends&"+\
            "user="+userName+"&limit="+str(limit)+"&page="+str(page)+"&api_key="+api_key 
        data = urllib2.urlopen(command).read()
        errors = re.findall("<error>(.*)</error>", data)
        while len(errors) > 0 :
            print errors
            command = server+"?method=user.getfriends&"+\
                "user="+userName+"&limit="+str(limit)+"&page="+str(page)+"&api_key="+api_key 
            data = urllib2.urlopen(command).read()
            errors = re.findall("<error>(.*)</error>", data)
        return data
    except :
        print "could not fetch %s" % command


def getFriends(users, degrees, friends, marked):
    """Get results from of friends from all pages"""
    while users:
        user = users.popleft()
        if user in marked:
            continue
        data = getFriendsReq(user,1)
        if data == None:
            continue
        degree = int(re.search('total="(\d+)"', data).group(1))
        if degree == 0 :
            continue
        degrees.append(degree)
        friends.extend(re.findall("<name>(.*)</name>", data))
        # In case we have to read more than one pages
        if degree > limit:
            pagesnum = degree/limit+1
            for x in range(2,pagesnum+1) :
                data = getFriendsReq(user,x)
                if data == None:
                    continue
                friends.extend(re.findall("<name>(.*)</name>", data))

    
def bfs(root) :
    marked = set()        # marked set to check whether we have seen user or not
    users = deque([root]) # users that have not been seen yet
    degrees = deque()
    N = 0
    f = open("results.txt", "w")
    while N < maxlevel :
        N = N + 1
        friends = deque()
        old_users = list(users)
        threads = [Thread(target=getFriends, args=(users, degrees, friends, marked)) for i in xrange(128)]
        for thread in threads:
            thread.setDaemon(True)
            thread.start()
        for thread in threads:
            thread.join()
        marked = marked.union(set(old_users))
        users = friends
        SumK = 0
        for d in degrees:
            SumK += d
        print SumK/len(degrees), len(degrees)
        f.write(str(SumK / len(degrees))+' '+str(len(degrees)))
    f.close()
    return SumK/len(degrees), len(degrees)

if __name__ == "__main__":
    degree, N = bfs(user)
    print "Final average degree: "+str(degree)
    print "Size of graph: "+str(N)


