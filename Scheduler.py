#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''   
CS5250 Assignment 4, Scheduling policies simulator  
Sample skeleton program   
Input file:  
    input.txt   
Output files:   
    FCFS.txt   
    RR.txt  
    SRTF.txt  
    SJF.txt  
'''  
import sys
input_file = 'input.txt' 

class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.burst_time_copy = burst_time
        self.predicted_burst_time = 5

    # for printing purpose
    def __repr__(self):
        return '[pid %d -->   arrival_time %2d,   burst_time %d]' % (self.id, self.arrive_time, self.burst_time)
       
def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result

def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time        
        
def RR_scheduling(process_list, time_quantum):   
    nprocess  = len(process_list)
    current_time = 0
    waiting_time = 0
    scheduled = []
    ready_queue = []
    ready_queue.append(process_list[0])
    process_list.remove(process_list[0]) 
    while len(ready_queue)!=0:
	#schedule the current process from ready queue
        current_process = ready_queue.pop(0)
        #check the quantum is bigger than burst time
        if current_process.burst_time >= time_quantum:
            run_time = time_quantum  
        else:
	    #run for full quantum
            run_time = current_process.burst_time        
 	#update the scheduled list for output
	scheduled.append((current_time, current_process.id))
	#advance the CPU times
        current_time = current_time + run_time
        #update the the current process remaining burst time
        current_process.burst_time = current_process.burst_time - run_time 
        for process in process_list:
            if process.arrive_time <= current_time:
                ready_queue.append(process)
		#print ready_queue
        process_list = [x for x in process_list if x.arrive_time > current_time]
	#add the current process to the back of ready_queue      
        if current_process.burst_time != 0:
            ready_queue.append(current_process)
	    #print ready_queue
	#process completed
        else:
            waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        if len(ready_queue)==0 and len(process_list) > 0:
            ready_queue.append(process_list[0])
            current_time = process_list[0].arrive_time
            process_list.remove(process_list[0])
    average_waiting_time = waiting_time/float(nprocess)
    return scheduled, average_waiting_time
        
def SRTF_scheduling(process_list):
    nprocess  = len(process_list)
    scheduled = []
    current_time = 0
    waiting_time = 0
    ready_queue =  []
    current_process = process_list[0]
    ready_queue.append(process_list[0])
    process_list.remove(process_list[0])
    while len(ready_queue) > 0:
        current_process.burst_time = current_process.burst_time - 1
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time
        if len(scheduled) == 0 or scheduled[len(scheduled) - 1][1] != current_process.id:
            scheduled.append((current_time, current_process.id))
        current_time += 1
        if current_process.burst_time == 0:
            ready_queue.remove(current_process)
            waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        for process in process_list:
            if process.arrive_time <= current_time:
                ready_queue.append(process)        
        if len(ready_queue)==0 and len(process_list) > 0:
            current_time = process_list[0].arrive_time
            ready_queue.append(process_list[0])
        process_list = [x for x in process_list if x.arrive_time > current_time]
	#Process with similar burst time will be scheduled using FIFO.
        if len(ready_queue) > 0:
            current_process = min(ready_queue, key=lambda p: p.burst_time)
    average_waiting_time = waiting_time/float(nprocess)  
    return scheduled, average_waiting_time 
        
    
def SJF_scheduling(process_list, alpha):
    plistsize  = len(process_list)
    scheduled = []
    current_time = 0
    waiting_time = 0
    queue =  []
    current_process = process_list[0]
    queue.append(process_list[0])
    process_list.remove(process_list[0])
    history = dict()

    while len(queue) > 0:
        queue = sorted(queue, key=lambda p: p.predicted_burst_time)
        current_process = queue.pop(0)
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time
        if len(scheduled) == 0 or scheduled[len(scheduled) - 1][1] != current_process.id:
            scheduled.append((current_time, current_process.id))
        current_time += current_process.burst_time
        current_process.burst_time = 0
        last_predicted_burst_time = history[
            current_process.id] if current_process.id in history else current_process.predicted_burst_time
        predicted_burst_time = (alpha * current_process.burst_time_copy) + ((1 - alpha) * last_predicted_burst_time)
        history[current_process.id] = predicted_burst_time
        waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        for process in process_list:
            if process.arrive_time <= current_time:
                if process.id in history:
                    process.predicted_burst_time = history[process.id]
                queue.append(process)
        if len(queue)==0 and len(process_list) > 0:
            current_time = process_list[0].arrive_time
            queue.append(process_list[0])
            
        process_list = [x for x in process_list if x.arrive_time > current_time]
    average_waiting_time = waiting_time/float(plistsize)
    return scheduled, average_waiting_time
    

    
 
def printinput():
    process_list = read_input()
    print ("printing input")
    for process in process_list:
	pass        
	#print (process)
 
def FCFS():
    process_list = read_input()
    #FCFS
    print ("simulating FCFS")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    for output in FCFS_schedule:
	pass
        #print (output)
    print "Average Waiting time of FCFS:",FCFS_avg_waiting_time  
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )

def RR(time_quantum):
    process_list = read_input()
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum)
    print "simulating RR with time quantum =",time_quantum
    for output in RR_schedule:
	pass
        #print (output)
    print "Average Waiting time of RR:",RR_avg_waiting_time
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )


def SRTF():
    process_list = read_input()
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    print "simulating SRTF"
    for output in SRTF_schedule:
	pass
        #print (output)
    print "Average Waiting time of SRTF:",SRTF_avg_waiting_time
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )

def SJF(alpha):
    process_list = read_input()
    print "simulating SJF with alpha =",alpha
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha)
    for output in SJF_schedule:
	pass
        #print (output)
    print "Average Waiting time of SJF:",SJF_avg_waiting_time
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )


def main(argv):
    printinput()
    FCFS()
    RR(6)
    SRTF()
    SJF(0.5)
          
    
if __name__ == '__main__':
    main(sys.argv[1:])

