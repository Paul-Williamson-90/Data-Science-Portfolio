import time

word = ['~',0,1,'_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_','_']


def rules(state,word,index):
    if state == 'S':
        if word[index] == 1 or word[index] == 0:
            index+=1
            return state, word,index
        elif word[index] == '_':
            index-=1
            state = 'I'
            return state, word, index
        
    elif state == 'I':
        if word[index] == 0:
            index -=1
            return state, word, index
        elif word[index] == 1:
            word[index] = 0
            state = 'C'
            return state, word, index
        elif word[index] == '~':
            index +=1
            state = 'Z'
            return state, word, index

    
    elif state == 'Z':
        if word[index] == '_' or word[index]==0:
            word[index] = 1
            state = 'Y'
            return state, word, index
    
    elif state == 'Y':
        if word[index] == 1:
            index+=1
            return state, word, index
        elif word[index] == '_':
            word[index] = 0
            state = 'h'
            return state, word, index
            
    elif state == 'C':
        if word[index] == 0:
            index +=1
            state = 'D'
            return state, word, index 
    
    elif state == 'C2':
        if word[index] == 0:
            word[index] = 1#
            state = 'D'
            return state, word, index
        
    elif state == 'D':
        if word [index] == 1 or word[index]==0:
            index +=1
            return state, word, index
        elif word[index] == '_':
            word[index] = 'H'
            state = 'E'
            return state,word,index
        elif word[index] == '#':
            word[index] = 'G'
            state = 'E'
            return state, word, index
        
        """TRANSITION TO MULTIPLY"""       
    elif state == 'E':
        # Finds 0 or end, plants 1
        if word[index] in ['A','B','C','D','E','F','G','H']:
            index += 1
            return state, word, index
        # new multiply count
        elif word[index] == '_':
            word[index] = 1
            state = 'J' # job done go back 
            return state, word, index
        # change 0 to 1 (index 0)
        elif word[index] == 0:
            word[index] = 1
            state = 'J' # job done, go back
            return state, word, index
        # change 1 to 0 (index 0)
        elif word[index] == 1:
            word[index] = 0
            state = 'K' # carry on
            return state,word,index
        # transition to input counter reduction
        elif word[index] == '#':
            index-=1
            state = 'G' # transition
            return state, word, index

    elif state == 'J':
        if word[index] == 1 or word[index] == 0:
            index-=1
            return state,word,index
        # change letter 
        elif word[index] in ['#','A','B','C','D','E','F','G','H']:
            i = ['#','A','B','C','D','E','F','G','H'].index(word[index])
            word[index] = ['#','A','B','C','D','E','F','G','H'][i-1]
            state = 'E'
            return state, word, index
        
    elif state == 'K':
        if word[index] == 0:
            index+=1
            state = 'K2' 
            return state, word, index 
        
    elif state == 'K2':
        if word[index] == 1:
            word[index] = 0
            state = 'K'
            return state, word, index
        elif word[index] == 0:
            word[index] = 1
            state = 'J' # go back
            return state, word, index
        elif word[index] == '_':
            word[index] = 1
            state = 'J' # go back
            return state, word, index
        
    # COUNTER REDUCTION SECTION
    elif state == 'G':
        if word[index] == '#':
            index-=1
            return state, word, index
        elif word[index] == 0:
            index -=1
            return state, word, index
        elif word[index] == 1:
            word[index] = 0
            state = 'G2'
            return state, word, index 
        elif word[index] == '~':
            index+=1
            state ='L'
            return state, word, index
        elif word[index] == '@':
            word[index] = '_'
            state = 'L4'
            return state, word, index
        
    elif state == 'G2':
        if word[index] == 0 or word[index] == 1:
            index+=1
            state = 'G3'
            return state, word, index 
        
    elif state == 'G3':
        if word[index] == 1:
            index+=1
            return state, word, index
        elif word[index] == 0:
            word[index] = 1
            state = 'G4'
            return state, word, index
        elif word[index] == '#': 
            state = 'E'
            word[index] = 'H'
            return state, word, index
        
    elif state == 'G4':
        if word[index] == 1 or word[index] == 0:
            index+=1
            return state, word, index
        elif word[index] == '#':
            word[index] = 'H'
            state = 'E'
            return state, word, index 
            
    #SWAPPING MODE
    elif state == 'L': 
        if word[index] == 0 or word[index] == 1:
            word[index] = '_'
            return state, word, index
        elif word[index] == '_':
            index +=1
            return state, word, index
        elif word[index] == '#':
            word[index] = 'B'
            state = 'LL'
            return state, word, index 
        
    elif state == 'LL':
        if word[index] == 'B':
            index-=1
            return state, word, index
        elif word[index] == '_':
            word[index] = '@'
            state = 'LL2'
            return state, word, index
        
    elif state == 'LL2':
        if word[index] == '@':
            index +=1
            state = 'E'
            return state, word, index
         
            
    elif state == 'L2':
        if word[index] == '_':
            index+=1
            state = 'L3'
            return state, word, index 
       
    elif state == 'L3':
        if word[index] == 0 or word[index] == 1:
            index+=1
            return state, word, index
        elif word[index] == '_':
            word[index] = '*'
            state = 'M'
            return state, word, index 
        
    elif state == 'L4':
        if word[index] == '_':
            index +=1
            return state, word, index
        elif word[index] == '#':
            word[index]='_'
            state = 'L5'
            return state, word, index
        
    elif state == 'L5':
        if word[index] == '_':
            index+=1
            state = 'L6'
            return state, word, index
    
    elif state == 'L6':
        if word[index] == 0 or word[index] == 1:
            index+=1
            return state, word, index
        elif word[index] == '_':
            word[index] = '*'
            state = 'M'
            return state, word, index
            
    # Mirror on star
    elif state == 'M':
        # move back one
        if word[index] == '*': 
            index-=1
            return state, word, index 
        elif word[index] == '_':
            index-=1
            return state, word, index
        elif word[index] ==0: 
            word[index] = '_'
            state = 'N'
            return state, word, index
        elif word[index] ==1:
            word[index] = '_'
            state = 'O'
            return state, word, index
        elif word[index] == '~':
            index+=1
            state = 'R'
            return state, word, index
    
    elif state == 'N':
        # place 0
        if word[index] == '_':
            index+=1
            return state, word, index
        elif word[index] == '*':
            index+=1
            state = 'N2'
            return state, word, index 
    
    elif state == 'N2':
        if word[index] == '*' or word[index] == 1 or word[index] == 0:
            index+=1
            return state, word, index
        elif word[index] == '_':
            word[index] = 0
            state = 'P'
            return state, word, index
    
    elif state == 'O':
        # place 1
        if word[index] == '_':
            index+=1
            return state, word, index
        elif word[index] == '*':
            index+=1
            state = 'O2'
            return state, word, index 
    
    elif state == 'O2':
        if word[index] == '*' or word[index] == 1 or word[index] == 0:
            index+=1
            return state, word, index
        elif word[index] == '_':
            word[index] = 1
            state = 'P'
            return state, word, index
        
    elif state == 'P':
        if word[index] == 1 or word[index] == 0:
            index-=1
            return state, word, index 
        elif word[index] == '*':
            index-=1
            state = 'M'
            return state, word, index
        
    # END GAAME    
    elif state == 'R':
        if word[index] == '_':
            index+=1
            return state, word, index
        elif word[index] == '*':
            word[index] = '_'
            state = 'R2'
            return state, word, index
        
    elif state == 'R2':
        if word[index] == '_':
            index +=1
            state = 'R3'
            return state, word, index
        
    elif state == 'R3':
        if word[index] == 1 or word[index] == 0:
            index +=1
            return state, word, index
        elif word[index] =='_':
            word[index] = '*'
            state = 'R4'
            return state, word, index
        
    elif state == 'R4':
        if word[index] == '*' or word[index] == 1 or word[index] == 0:
            index-=1
            return state, word, index
        elif word[index] == '_':
            index+=1
            state = 'R5'
            return state, word, index
        
    elif state == 'R5':
        if word[index] == '_':
            index+=1
            return state, word, index
        elif word[index] == 0:
            word[index] = '_'
            state = 'T'
            return state, word, index
        elif word[index] == 1:
            word[index] = '_'
            state = 'U'
            return state, word, index
        elif word[index] == '*':
            word[index] = '_'
            state = 'h'
            return state, word, index
        
    elif state == 'T':
        # STEALING 0
        if word[index] == '_':
            index-=1
            return state, word, index
        if word[index] == 1 or word[index] == 0 or word[index] == '~':
            index+=1
            state = 'T2'
            return state, word, index
        
    elif state == 'T2':
        if word[index] == '_':
            word[index] = 0
            state = 'V'
            return state, word, index
        
    elif state == 'U':
        # STEALING 0
        if word[index] == '_':
            index-=1
            return state, word, index
        if word[index] == 1 or word[index] == 0 or word[index] == '~':
            index+=1
            state = 'U2'
            return state, word, index
        
    elif state == 'U2':
        if word[index] == '_':
            word[index] = 1
            state = 'V'
            return state, word, index
        
    elif state == 'V':
        # going back to the mirror
        if word[index] == 1 or word[index] == 0:
            index+=1
            state = 'R5'
            return state, word, index
        
    
def function(word):
    index = 1
    state = 'S'
    arrow = ['_' for x in word]
    print('====================================')
    print(f'\nState: {state}')
    for l in word:
        print(f'{l} ',end='')
    print('\n')
    arrow = ['_' for x in word]
    arrow[index] = '^'
    for a in arrow:
        print(f'{a} ',end='')
    print('')
    time.sleep(0.5)
    while True:
        state,word,index = rules(state,word,index)    
        print('====================================')
        print(f'\nState: {state}')
        for l in word:
            print(f'{l} ',end='')
        print('\n')
        arrow = ['_' for x in word]
        arrow[index] = '^'
        for a in arrow:
            print(f'{a} ',end='')
        print('')
        time.sleep(0.5)
        if state == 'h':
            break
        
function(word)
        
        
        
        
        
        
        
        
        
        
        
        