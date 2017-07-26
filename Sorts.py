import random

def mergeSort(alist=[]):
    if len(alist) > 1:
        mid = len(alist) // 2
        lefthalf = alist[:mid]
        righthalf = alist[mid:]

        mergeSort(lefthalf)
        mergeSort(righthalf)

        i=0
        j=0
        k=0

        while i < len(lefthalf) and j < len(righthalf):
            if lefthalf[i] < righthalf[j]:
                alist[k]=lefthalf[i]
                i = i+1
            else:
                alist[k]=righthalf[j]
                j = j+1
            k = k+1
        while i < len(lefthalf):
            alist[k]=lefthalf[i]
            i = i+1
            k = k+1
        while j < len(righthalf):
            alist[k]=righthalf[j]
            j = j+1
            k = k+1

def quickSort(alist):
   quickSortHelper(alist,0,len(alist)-1)

def quickSortHelper(alist,first,last):
   if first<last:

       splitpoint = partition(alist,first,last)

       quickSortHelper(alist,first,splitpoint-1)
       quickSortHelper(alist,splitpoint+1,last)

def partition(alist,first,last):
   pivotvalue = alist[first]
   leftmark = first+1
   rightmark = last

   done = False
   while not done:
       while leftmark <= rightmark and alist[leftmark] <= pivotvalue:
           leftmark = leftmark + 1
       while alist[rightmark] >= pivotvalue and rightmark >= leftmark:
           rightmark = rightmark -1
       if rightmark < leftmark:
           done = True
       else:
           temp = alist[leftmark]
           alist[leftmark] = alist[rightmark]
           alist[rightmark] = temp

   temp = alist[first]
   alist[first] = alist[rightmark]
   alist[rightmark] = temp

   return rightmark

def bubbleSort(alist):
    for passnum in range(len(alist)-1,0,-1):
        for i in range(passnum):
            if alist[i]>alist[i+1]:
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp

if __name__ == '__main__':
    alist = random.sample(range(1,10000), 1000)
    blist = random.sample(range(1,10000), 1000)
    clist = random.sample(range(1,10000), 1000)
    mergeSort(alist)
    quickSort(blist)
    bubbleSort(clist)
    print(alist)
    print(blist)
    print(clist)
