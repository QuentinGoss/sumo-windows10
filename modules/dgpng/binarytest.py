from bisect import bisect_left

def main():
    wordlist = ['one','two','three','four','five','six','seven']
    numbers = [1,2,3,4,5,60,200,2500]
    
    for word in wordlist:
        print(int(''.join(str(ord(c)) for c in self.ID)))
    
    #result = index(wordlist,'one')
    #result = index(numbers,5)
    #print(result)
    return

def index(lst,el):
    # Locate the leftmost value exactly equal to x
    i = bisect_left(lst,el)
    if i != len(lst) and lst[i] == el:
        return i
    raise ValueError
   
main()
