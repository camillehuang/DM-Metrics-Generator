"""
Meta
====
    $Id: //splunk/branches/bieber/test/bin/dm_metrics_generator.py#1 $
    $DateTime: 2011/10/05 10:03:01 $
    $Author: chuang $
    $Change: 2012/07/31 $
"""

'''
Testlink test category: Deployment Monitoring manual testing
 Purpose: generate some events of metrics.log to help manual test progress
 Preconditions:
    1. suggest to enable DM on search head only.
    2. Clean all eventdata and execute this script.
    3. Adjust your machine time after stop splunk.
    4. Create some saved searches for indexing past data at the same time. (make your life easier)
 Postconditions: None
    1. Remove added saved searches after test finished manually.
'''
import os
from datetime import datetime, timedelta
from shutil import copy

file_name = str(datetime.now().strftime("%Y%m%d_%H%M")) + '-metrics.txt'
f = open(file_name,'w')
#FORWARDER_NAME = 'chuangteki-macbook-pro.local'
FORWARDER_NAME = 'FakeForwarder'#'卡蜜兒的轉發者2'
FORWARDER_IP = '172.18.90.235'
LAST_INDEXER_IP = '172.18.90.230'
#HOST_NAME = 'WIN-VS1UV357AGH'

HOST_NAME = 'FakeHostName'#'卡蜜兒的VM'
#GUID = '2A4A2102-EF26-40B7-9E0D-DE3FB13CA15A'
GUID = '2A4A2102-EF26-40B7-9E0D-DE3FB13CA15B'
INDEXER_NAME = 'chuang-fake'
SPLUNK_VERSION = '4.3.4' # edit it every version
INTERVAL = 60 #30sec
event_count = 0

#------------Write log-------------------------------------------------------------------------------------
def log_per_host_thruput(dt, Name, kb):
    f.write(dt + ' INFO  Metrics - group=per_host_thruput, series="' + Name + '", kbps=0.008008, eps=0.066667, kb=' + str(kb) + ', ev=2, avg_age=-4.000000, max_age=-4\n')
    global event_count
    event_count +=1

def log_per_index_thruput(dt, kb, series):
    f.write(dt + ' INFO  Metrics - group=per_index_thruput, series="'+ series +'", kbps=0.017673, eps=0.032258, kb=' + str(kb) + ', ev=1, avg_age=1813.000000, max_age=1813\n')
    global event_count
    event_count +=1

def log_per_source_thruput(): #TODO for source event
    f.write(dt + ' INFO  Metrics - group=per_source_thruput, series="c:\program files\splunk\var\log\splunk\metrics.log", kbps=0.364290, eps=2.166667, kb=10.928711, ev=65, avg_age=1.107692, max_age=3\n')
    global event_count
    event_count +=1
    
def log_tcpin_connections(dt, kb):
    forwarderNameLog = FORWARDER_NAME
    f.write(dt + ' INFO  Metrics - group=tcpin_connections, ' + FORWARDER_IP + ':61656:9997, connectionType=cooked, sourcePort=61656, sourceHost=' + FORWARDER_IP + ', sourceIp=' +  FORWARDER_IP + ', destPort=9997, _tcp_Bps=74.19, _tcp_KBps=0.07, _tcp_avg_thruput=0.09, kb=' + str(kb) + ', _tcp_Kprocessed=317.00, _tcp_eps=0.13, build=105575, version='+ SPLUNK_VERSION +', os=Darwin, arch=x86_64, hostname=' + forwarderNameLog +', guid=' + GUID + ', fwdType=full, ssl=false, lastIndexer=' + LAST_INDEXER_IP + ':9997, ack=false\n')
    global event_count
    event_count +=1

def log_indexqueue(dt, kb, max_kb):
    f.write(dt + ' INFO  Metrics - group=queue, name=indexqueue, max_size_kb='+ str(max_kb) +', current_size_kb=' + str(kb) + ', current_size=0, largest_size=5, smallest_size=0\n')
    global event_count
    event_count +=1

def log_parsingqueue(dt, kb, max_kb):
    f.write(dt + ' INFO  Metrics - group=queue, name=parsingqueue, max_size_kb='+ str(max_kb) +', current_size_kb=' + str(kb) + ', current_size=0, largest_size=5, smallest_size=0\n')
    global event_count
    event_count +=1

#-----------Test cases--------------------------------------------------------------------------------------
def index_throughput(t, end_t, indexerNameLog, lastWeek_index_kb, today_index_kb, lastWeek_parsing_kb,today_parsing_kb, is_over_load): #splunk-1551,1552 : the whole day 00:00~23:59
    multiple = 2
        
    if is_over_load == 1:
        multiple = 1

    t = t + timedelta(minutes=-30)
    if lastWeek_index_kb >= 0 and is_over_load != 1: # generate last week if index kb >=0
       # Last week
       t_lastWeek = t + timedelta(days=-7) 
       end_t_lastWeek = t + timedelta(days=-6)# + timedelta(minutes=-30)
    
       while t_lastWeek < end_t_lastWeek:
          dt = t_lastWeek.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
          log_per_host_thruput(dt, indexerNameLog, lastWeek_index_kb)
          log_per_index_thruput(dt, lastWeek_index_kb, 'default') # default
          if today_index_kb == 0:
              log_indexqueue(dt, lastWeek_index_kb, 500)
              log_parsingqueue(dt, lastWeek_parsing_kb, 6000)
          else:
              log_indexqueue(dt, lastWeek_index_kb, lastWeek_index_kb * multiple)
              log_parsingqueue(dt, lastWeek_parsing_kb, lastWeek_parsing_kb * multiple)       
          #logTcpin_connections(dt, index_kb)
          t_lastWeek = t_lastWeek + timedelta(seconds=+INTERVAL)

    # Today
    while t < end_t:
       dt = t.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
       log_per_host_thruput(dt, indexerNameLog, today_index_kb)
       log_per_index_thruput(dt, today_index_kb, 'default')
       if today_index_kb == 0:
           log_indexqueue(dt, today_index_kb, 500)
           log_parsingqueue(dt, today_parsing_kb, 6000)
       else:
           log_indexqueue(dt, today_index_kb, today_index_kb * multiple)
           log_parsingqueue(dt, today_parsing_kb, today_parsing_kb * multiple)
       #log_tcpin_connections(dt, today_index_kb)
       t = t + timedelta(seconds=+INTERVAL)

def idle_indexer(t, end_t, idle_num):
    index_kb = 0
    i = range(idle_num)
    
    for x in i:
        startT = t;
        indexerNameLog = INDEXER_NAME + str(i[x])
        index_throughput(t, end_t, indexerNameLog, -1, 0, 0, 0, 0)
        #f.write('\n\n\n\n\n\n\n\n\n')
    
def over_loaded_indexer(t, end_t, over_num):
    index_kb = 400
    parsing_kb = 4000
    i = range(over_num)

    for x in i:
        indexerNameLog = INDEXER_NAME + str(i[x])
        index_throughput(t, end_t, indexerNameLog, index_kb, index_kb, parsing_kb,parsing_kb, 1) #1 means overload
        #f.write('\n\n\n\n\n\n\n\n\n')
    #print 'Copy to another instance!'
    
def quiet_forwarder(t, end_t): #1557
    #f.write(dt + ' INFO  Metrics - group=per_host_thruput, series="' + FORWARDER_NAME + '", kbps=0.006380, eps=0.033333, kb=0.0, ev=1, avg_age=2.000000, max_age=2\n')
    kb = 0
    while t <= end_t:
       dt = t.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
       log_tcpin_connections(dt, kb) # indexing from forwarder's data
       t = t + timedelta(seconds=+INTERVAL)
    
def less_data_forwarder(t, end_t):
    t_lastWeek = t + timedelta(days=-7)
    end_t_lastWeek = end_t + timedelta(days=-7)
    index_kb = 0.547852
    tcpin_kb = 34.0
    while t_lastWeek <= end_t_lastWeek:
       dt = t_lastWeek.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
       #log_per_index_thruput(dt, index_kb,  'summary_forwarders')
       log_per_host_thruput(dt, FORWARDER_NAME, tcpin_kb)
       log_tcpin_connections(dt, tcpin_kb)
       t_lastWeek = t_lastWeek + timedelta(seconds=+INTERVAL)

    index_kb = 0.547852
    tcpin_kb = 5.00
    while t <= end_t:
       dt = t.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
       #log_per_index_thruput(dt, index_kb,  'summary_forwarders')
       log_per_host_thruput(dt, FORWARDER_NAME, tcpin_kb)
       log_tcpin_connections(dt, tcpin_kb)
       t = t + timedelta(seconds=+INTERVAL)
    print 'Put savedsearches.conf to splunk\etc\apps\SplunkDeploymentMonitor\local'

def license_usage_summary(t, end_t):
   t_last30D = t + timedelta(days=-31) + timedelta(hours=-t.hour)
   parsing_kb = 4000
   long_interval = 3600 #one event every 1 hour

   t_peak1 = t + timedelta(days=-28) + timedelta(hours=-t.hour)
   t_peak2 = t + timedelta(days=-24) + timedelta(hours=-t.hour)
   
   while t_last30D <= end_t:
       dt = t_last30D.strftime("%m-%d-%Y %H:%M:%S.000 +0800")
       if t_last30D <= t_peak1 and t_last30D <= t_peak2: # 5 peaks
          index_kb =  1048576*6 # 6 gb
       else: index_kb =  1048576*3
       #logPer_host_thruput(dt, indexerName, index_kb)
       log_per_index_thruput(dt, index_kb, 'default')
       log_indexqueue(dt, index_kb, index_kb * 2)
       log_parsingqueue(dt, parsing_kb, parsing_kb * 2)
       t_last30D = t_last30D + timedelta(seconds=+long_interval)
   print 'Each usage is 3 GB.\nBefore testing, clean eventdata'

#-----------Main------------------------------------------------------------------------------------------------   
def main(argv=None):
    saved_search_conf_path = os.path.join(os.path.expandvars("%SPLUNK_HOME%"), "etc", "apps", "SplunkDeploymentMonitor", "local")
    metrics_file = os.path.join(os.path.expandvars("%SPLUNK_HOME%"), "var", "log", "splunk", "metrics.log")
    
    print 'Select test item:\n1. 1557:quiet forwarder\n2. 1561:less data forwarder\n3. 1554:idle indexer\n4. 1555:over loaded indexer\n5. 1760:license usage/report\n6. 1550~1552:index throughput'
    case = raw_input('Input number:')
    #t = datetime(2011, 9, 19, 17, 0, 0) # specify date time
    if datetime.now().minute <30:
        t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 30, 0)+timedelta(hours=-1)
        end_t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 30, 0)
    else:
        t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 0)
        end_t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 0)+timedelta(hours=+1)

    #index_throughput(t, end_t, INDEXER_NAME, 0,0,0,0) # splunk-1550,1551, 1552. Input the whole day
    if case == '1':
        quiet_forwarder(t, end_t)
    elif case == '2':
        less_data_forwarder(t, end_t)
    elif case == '3':
        idle_num = raw_input('How many idle indexer?')
        idle_indexer(t, end_t, int(idle_num)) # splunk-1554, input how many idle indexers you want
    elif case == '4':
        over_num = raw_input('How many over-loaded indexer?')
        over_loaded_indexer(t, end_t, int(over_num))
    elif case == '5':
        t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 0)
        end_t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour+1, 0, 0)
        license_usage_summary(t, end_t)
    elif case == '6':
        t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0)# + timedelta(hours=-1) #today 0:00
        end_t = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, 0, 0)+ timedelta(hours=+1) # end of this hour
        kbps = raw_input('Today throughput :(2KBps)')
        if len(kbps) == 0:
            kbps = 2
        else:
            kbps = int(kbps)
        kb = kbps*INTERVAL
        index_throughput(t, end_t, INDEXER_NAME, kb/2, kb, 100, 200, 0) #today is double of lastweek
        print 'lastweek per event=%dKB, today per event=%dKB. lastweek avg=%dKBps, today avg=%dKBps' % (kb/2, kb, kbps/2, kbps)
    else: exit()

    #indexingPastSavedsearches()
    
    f.close()    
    #print 'Please empty metrics.log and past the content of ' + file_name + ' and then save in UTF-8 format.'
    
    if raw_input('Copy the savedsearches.conf to DM %s?n (y/n)' % (saved_search_conf_path)) == 'y':
        copy("savedsearches.conf", saved_search_conf_path) 
    copy(file_name, metrics_file)
    print 'The event count is %s' % (event_count)

if __name__ == "__main__":
    main()
